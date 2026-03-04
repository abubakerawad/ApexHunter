import duckdb
import logging

logger = logging.getLogger(__name__)

class QueryExecutor:
    """Executes SQL queries against DuckDB."""
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def execute(self, query: str, query_type: str = "sql") -> list[dict]:
        """Executes a query and returns results as a list of dicts."""
        try:
            if query_type == "sql":
                result = self.conn.execute(query).fetchdf()
                return result.to_dict('records')
            elif query_type == "python":
                # Safe eval: assume 'df' is available if we were using pandas directly, 
                # but since we use DuckDB, we'll fetch the last view as a df
                # This is a stub for the 'python' query type
                logger.warning("Python query type is in experimental stub mode.")
                return []
            elif query_type == "sigma":
                # Sigma stub: In a real scenario, we'd use pySigma to convert to SQL
                logger.warning("Sigma query type is in stub mode. Convert Sigma to SQL manually.")
                return []
            return []
        except Exception as e:
            logger.error(f"Query execution failed ({query_type}): {e}")
            return []
