<h1 align=center>Query Operations Guide</h1>

**FiSE** offers two different operations to its users namely **Search** and **Delete**. This guide provides an in-depth description of these query operations and explains their usage and structure, offering practical examples to help users understand and utilize these functionalities effectively.

<h2 align=center>Search Operation</h2>

The Search operation allows users to query and search files, file contents, and directories based on the specific conditions. This operation also supports exporting search records to external files or databases.

For more information about the search query syntax, please refer to  the [Syntax](./syntax.md#1-search-query-syntax) guide.

To know more about the different metadata fields which can be for the search operation. Please refer to the [Query-Fields](./query-fields.md) guide.

### Examples

**File Search**:

```SQL
EXPORT FILE[./records.xlsx] R SELECT * FROM .
```

```SQL
R SELECT[TYPE FILE] NAME, SIZE[KB] CTIME, ATIME FROM 'C:/Program Files' WHERE NAME LIKE 'Python310'
```

**Data Search**:

```SQL
SELECT[TYPE DATA] LINENO, DATALINE FROM ./fise/query/conditions.py WHERE DATALINE LIKE '.*fiSE.*' AND LINENO BETWEEN (1, 100) 
```

```SQL
RECURSIVE SELECT[TYPE DATA, MODE BYTES] * FROM . WHERE name like '.*\.py'
```

**Directory Search**:

```SQL
R SELECT[TYPE DIR] NAME, PARENT FROM ./fise
```

```SQL
EXPORT SQL[postgresql] SELECT[TYPE DIR] * FROM /usr/bin/
```

<h2 align=center>Delete Operation</h2>

The Delete operation allows users to remove files and directories based on specified conditions. Unlike the search operation, the delete operation doesn't allow exporting deleted file/directory records.

For more information about the delete query syntax, please refer to the [Syntax](./syntax.md#2-delete-query-syntax) guide.

To know more about the different metadata fields which can be for the search operation. Please refer to the [Query-Fields](./query-fields.md) guide.

### Examples

**File Deletion**:

```SQL
DELETE FROM . WHERE filetype = '.js'
```

```SQL
R DELETE FROM /home/usr/projects WHERE CTIME < "2018-02-20" AND MTIME < "2019-09-28"
```

**Directory Deletion**:

```SQL
DELETE[TYPE DIR] FROM .
```

```SQL
RECURSIVE DELETE[TYPE DIR] FROM ../Documents WHERE ATIME < "2015-10-17"
```

<h2 align=center>Next Steps</h2>

To explore more advanced features, refer to the following guides for detailed insights into each topic:

1. **[Query Fields](./query-fields.md)**: Dive deep and know about the different metadata fields which can be used with different query operations.
2. **[Query Conditions](./query-conditions.md)**: Discover the ways to write precise and efficient conditions for filtering search/delete records.

---
