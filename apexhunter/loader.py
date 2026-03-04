import pandas as pd
import duckdb
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataLoader:
    """Loads log files into DuckDB for fast querying."""
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        # Using DuckDB for fast ad-hoc SQL on large logs without full DB setup
        self.conn = duckdb.connect(database=':memory:')
        
    def load_all(self):
        """Loads all CSV, JSON, Parquet files in data_dir into DuckDB tables."""
        if not self.data_dir.exists():
             logger.warning(f"Data directory {self.data_dir} does not exist.")
             return self.conn

        for file in self.data_dir.glob("*"):
            if not file.is_file(): continue
            table_name = file.stem
            try:
                # DuckDB prefers posix-style paths even on Windows
                file_path = file.as_posix()
                if file.suffix == '.csv':
                    self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
                elif file.suffix == '.json':
                    self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_json_auto('{file_path}')")
                elif file.suffix == '.parquet':
                    self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')")
                elif file.suffix == '.evtx':
                    self._load_evtx(file, table_name)
                logger.info(f"Loaded {file.name} into table {table_name}")
            except Exception as e:
                logger.error(f"Failed to load {file.name}: {e}")

    def _load_evtx(self, file_path: Path, table_name: str):
        """Offline-first Windows Event Log parser."""
        import Evtx.Evtx as evtx
        import xml.etree.ElementTree as ET

        events = []
        with evtx.Evtx(str(file_path)) as log:
            for record in log.records():
                try:
                    xml_str = record.xml()
                    root = ET.fromstring(xml_str)
                    # Simple flattening of EVTX XML to a flat dict for DuckDB
                    event = {"event_id": record.identifier(), "timestamp": record.timestamp().isoformat()}
                    for elem in root.iter():
                        if elem.text and elem.text.strip():
                            tag = elem.tag.split('}')[-1]
                            event[tag] = elem.text.strip()
                    events.append(event)
                except: continue
        
        if events:
            df = pd.DataFrame(events)
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        
        # Security hardening: Disable filesystem writing and external extensions AFTER loading
        try:
            self.conn.execute("SET enable_external_access=false;")
        except: pass
        return self.conn
