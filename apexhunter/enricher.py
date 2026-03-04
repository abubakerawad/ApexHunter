import json
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class TIEnricher:
    """Handles offline TI enrichment using local flat files."""
    def __init__(self, ti_dir: str = "intel"):
        self.ti_dir = Path(ti_dir)
        self.feeds = {}
        self.load_feeds()

    def load_feeds(self):
        """Loads all CSV/JSON files in the intel directory as lookups."""
        if not self.ti_dir.exists():
            self.ti_dir.mkdir(parents=True, exist_ok=True)
            return

        for file in self.ti_dir.glob("*"):
            try:
                if file.suffix == '.csv':
                    # Expecting simple 'indicator,type,description' format
                    df = pd.read_csv(file)
                    self.feeds[file.stem] = df.set_index(df.columns[0]).to_dict('index')
                elif file.suffix == '.json':
                    with open(file, 'r') as f:
                        self.feeds[file.stem] = json.load(f)
                logger.info(f"Loaded TI feed: {file.name}")
            except Exception as e:
                logger.error(f"Failed to load TI feed {file.name}: {e}")

    def enrich_item(self, key: str, value: str) -> dict:
        """Checks a value against all loaded feeds."""
        enrichments = {}
        for feed_name, data in self.feeds.items():
            if value in data:
                enrichments[feed_name] = data[value]
        return enrichments

    def enrich_results(self, results: list[dict], keys_to_check: list[str]) -> list[dict]:
        """Enriches a list of hits by checking specific keys (e.g., src_ip)."""
        for item in results:
            item['_enrichment'] = {}
            for key in keys_to_check:
                if key in item:
                    matches = self.enrich_item(key, str(item[key]))
                    if matches:
                        item['_enrichment'][key] = matches
        return results
