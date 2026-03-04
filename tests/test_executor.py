import duckdb
from apexhunter.executor import QueryExecutor

def test_executor_basic():
    conn = duckdb.connect(':memory:')
    conn.execute("CREATE TABLE test_table (id INTEGER, name VARCHAR)")
    conn.execute("INSERT INTO test_table VALUES (1, 'alice'), (2, 'bob')")
    
    executor = QueryExecutor(conn)
    results = executor.execute("SELECT * FROM test_table WHERE id = 1")
    
    assert len(results) == 1
    assert results[0]['name'] == 'alice'

def test_executor_invalid_query():
    conn = duckdb.connect(':memory:')
    executor = QueryExecutor(conn)
    results = executor.execute("SELECT * FROM nonexistent_table")
    assert results == []
