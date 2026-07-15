#![cfg(feature = "ocel-duckdb")]

#[test]
fn duckdb_runtime_executes_a_query() {
    let connection = duckdb::Connection::open_in_memory().unwrap();
    let value: i64 = connection
        .query_row("SELECT 42", [], |row| row.get(0))
        .unwrap();
    assert_eq!(value, 42);
}
