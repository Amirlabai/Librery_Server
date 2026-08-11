# Module `server/utils/path_utils.py`

## Functions

### `get_project_root()`

Determines the project root directory.
If path_utils.py is in server/utils/, go up two levels to get project root.

### `_get_project_root()`

Private alias for backward compatibility.

### `is_path_under(child: str, parent: str)`

Return True if child is inside parent after path normalization.

**Arguments:**
- `child` : `str`
- `parent` : `str`

### `resolve_config_path(config_path: str)`

Resolve a config path relative to project root when not absolute.

**Arguments:**
- `config_path` : `str`

### `get_root_search_cache_dir()`

Search cache directory (letter CSV shards).
