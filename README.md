<h1 align=center>
<img src="assets/fise.svg" width=400 align=center>
</h1>

<a href="https://github.com/rahul4732saini/fise/actions/workflows/pytest.yml"><img src="https://github.com/rahul4732saini/fise/workflows/Pytest/badge.svg" alt="Pytest" /></a>
<a href="https://www.codefactor.io/repository/github/rahul4732saini/fise"><img src="https://www.codefactor.io/repository/github/rahul4732saini/fise/badge" alt="CodeFactor"></a>

<a href="https://www.github.com/rahul4732saini/fise"><img src="https://img.shields.io/badge/status-beta-yellow?maxAge=60" alt="projectStatus"></a>
<a href="https://www.github.com/rahul4732saini/fise"><img src="https://img.shields.io/badge/python-3.10+-blue?label=Python&maxAge=60" alt="pythonVersion"></a>
<a href="https://github.com/rahul4732saini/fise/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?maxAge=60" alt="License"></a>

<a href="https://www.github.com/rahul4732saini/fise"><img src="https://img.shields.io/github/stars/rahul4732saini/fise.svg?style=social&label=Star&maxAge=60" alt="StarProject"></a>
<a href="https://www.twitter.com/rahulsaini4732"><img src="https://img.shields.io/twitter/follow/rahulsaini4732?style=social&label=Follow&maxAge=60" alt="Twitter"></a>
<a href="https://www.linkedin.com/in/rahul-saini-9191a5286/)"><img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=social&logo=linkedin&maxAge=60" alt="LinkedIn"></a>

<h2 align=center>Description</h2>

**FiSE (File System Search Engine)** is a powerful cross-platform command line utility designed for performing seamless file, directory, and data search and delete operations. It empowers users with the ability to perform comprehensive operations using intuitive SQL-like commands. It streamlines file management tasks, making it simple to locate, query, and modify files and directories with precision and efficiency. Additionally, this utility also allows exporting search records to files and databases in a professional manner. Ideal for developers, data analysts, system administrators, and power users, FiSE enhances productivity by providing a robust and flexible toolset for search and delete operations.

<h2 align=center>Features</h2>

1. **Cross-Platform Compatibility**: Works seamlessly across multiple operating systems, including Windows, macOS, and Linux.

2. **Comprehensive Search Operations**: Performs detailed searches for files, directories, and data within files with precise and efficient results.

3. **Intuitive SQL-like Commands**: Utilizes familiar SQL-like syntax for conducting searches and managing files, reducing the learning curve.

4. **Case-Insensitive Queries**: Allows queries to be case-insensitive, making searches more flexible and user-friendly.

5. **Advanced File Management**: Provides tools for locating, querying, and modifying files and directories with precision and efficiency.

6. **Professional Export Capabilities**: Offers export functionalities for search results to external files and databases, facilitating better data management and reporting.

7. **Productivity Enhancement Tools**: Enhances workflow and efficiency with a comprehensive and flexible toolset for various file system operations.

<h2 align=center>Quick Guide</h2>

This guide offers a basic overview of the utility, highlighting some of the commonly used queries. It enables users to efficiently search, query, and manipulate files and directories across different operating systems.

**FiSE** offers two broad categories of operations, namely **Search** and **Delete**. These operations can be performed on files, file data, and directories, with the exception for file data for the Delete operation.

For a deeper insight, please refer to the [Software Documentation](./doc/getting-started.md).

### Query Syntax Breakdown

The syntax of search and delete queries in **FiSE** is as follows:

- Search Query:

```SQL
(EXPORT (FILE[<FILEPATH>]|DBMS[<DATABASE>])) (R|RECURSIVE) SEARCH([<PARAMETERS>]) <PROJECTIONS> FROM (RELATIVE|ABSOLUTE) (<FILEPATH>|<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

- Delete Query:

```SQL
(R|RECURSIVE) DELETE([<PARAMETERS>]) FROM (RELATIVE|ABSOLUTE) (<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

Where:

1. `(EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>]))` is an optional clause exclusive to the search operation and is used to export search records to a file or database.

2. `(R|RECURSIVE)` is an optional clause and used to recursively include all the files or subdirectories present within the specified directory. If not explicitly specified, operations are only limited to the current directory.

3. `(SEARCH|DELETE)[<PARAMETERS>]` defines the desired operation to be performed. Additional parameters for the operation can also be specified within `[]` to toggle the operation between different filesystem entities, and file-modes (explicitly for data search operation).

4. `<PROJECTIONS>` is only limited to the search operation and is used for accessing metadata fields related to the searched files, data, or directories. Projection names must be separated by commas. For more information about the different metadata fields that can be used in **FiSE** queries, please refer to the [Query Fields](./doc/query/query-fields.md) guide.

5. `(RELATIVE|ABSOLUTE)` is an optional clause to specify whether to include the absolute path of the files/directories in the operation if the specified path to the directory is relative.

6. `(<FILEPATH>|<DIRECTORYPATH>)` defines the path to the file/directory to operate upon. Filepath is only limited to data search operations as other operations cannot be performed on a single file.

7. `(WHERE <CONDITIONS>)` is an optional clause and is used for define conditions for filtering files, data, or directories. To know more about the various ways for defining query conditions, please refer to the [Query Conditions](./doc/query/query-conditions.md) guide.

For a deeper insight into the query syntax, please refer to the [Query Syntax](./doc/query/syntax.md) guide. Apart from that, an overview and several examples for both query types are documented in the following sections.

### Overview of Search operation

The **Search** operation encompasses the ability to search files, file data, and directories facilitating precise retrieval by allowing users to filter records based on specified search conditions.

#### Search Query Syntax

- File Search Query:

```SQL
(EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>])) (R|RECURSIVE) SELECT([TYPE FILE]) <FIELDS> FROM (RELATIVE|ABSOLUTE) <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

- Directory Search Query:

```SQL
(EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>])) (R|RECURSIVE) SELECT[TYPE DIR] <FIELDS> FROM (RELATIVE|ABSOLUTE) <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

- Data Search Query:

```SQL
(EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>])) (R|RECURSIVE) SELECT[TYPE DATA(, MODE (TEXT|BYTES))] <FIELDS> FROM (RELATIVE|ABSOLUTE) (<FILEPATH>|<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

#### Search Query Examples

```SQL
SELECT * FROM ./fise WHERE name LIKE '^.*\.py$'
```

```SQL
EXPORT FILE[records.csv] R SELECT[TYPE FILE] RELATIVE * FROM .
```

```SQL
R SELECT[TYPE DIR] name, parent FROM ABSOLUTE ./fise WHERE name IN ['query', 'common']
```

```SQL
EXPORT SQL[mysql] RECURSIVE SELECT[TYPE DIR] * FROM . WHERE name IN ['fise', 'tests', '.github'] AND parent LIKE '^.*fise$'
```

```SQL
SELECT[TYPE DATA] lineno, data FROM fise/query/parsers.py WHERE "This" IN data AND lineno BETWEEN [30, 210]
```

```SQL
EXPORT FILE[./data.xlsx] R SELECT[TYPE DATA] * FROM ./fise/query WHERE name IN ['parsers.py', 'operators.py'] AND data LIKE '^.*get_files.*$'
```

### Overview of Delete Operation

The **Delete** operation encompasses the capability to remove files and subdirectories within the designated directory, empowering users to systematically eliminate undesired data based on specified filtering conditions.

#### Delete Query Syntax

- File Deletion Query

```SQL
(R|RECURSIVE) DELETE([TYPE FILE]) FROM <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

- Directory Deletion Query

```SQL
(R|RECURSIVE) DELETE[TYPE DIR] FROM <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

#### Delete Query Examples

```SQL
DELETE FROM ./fise WHERE atime < 2015-08-15 AND name != "main.py"
```

```SQL
R DELETE[TYPE FILE] FROM . WHERE filetype IN [".js", ".cpp"] OR SIZE[b] = 0
```

```SQL
DELETE[TYPE DIR] FROM . WHERE name IN ("temp", "__pycache__", "test")
```

```SQL
RECURSIVE DELETE[TYPE DIR] FROM ./fise
```

## Legals

**FiSE** is distributed under the MIT License. Refer to [LICENSE](./LICENSE) for more details.

## Call for Contributions

The **FiSE** project always welcomes your precious expertise and enthusiasm!
The package relies on its community's wisdom and intelligence to investigate bugs and contribute code. We always appreciate improvements and contributions to this project.
