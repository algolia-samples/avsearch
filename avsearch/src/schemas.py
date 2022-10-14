from schema import Schema

cleanup_patterns_schema = Schema([{"symbol": str, "value": str}])

category_patterns_schema = Schema([{"symbol": str, "category": str}])
