<h1 align=center>
<img src="assets/fise.svg" width=400 align=center>
</h1>

<a href="https://www.codefactor.io/repository/github/rahul4732saini/fise"><img src="https://www.codefactor.io/repository/github/rahul4732saini/fise/badge" alt="CodeFactor"></a>
<a href="https://www.github.com/rahul4732saini/fise"><img src="https://img.shields.io/badge/status-beta-yellow?maxAge=60" alt="projectStatus"></a>
<a href="https://www.github.com/rahul4732saini/fise"><img src="https://img.shields.io/badge/python-3.10+-blue?label=Python&maxAge=60" alt="pythonVersion"></a>
<a href="https://github.com/rahul4732saini/fise/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?maxAge=60" alt="License"></a>

<a href="https://www.github.com/rahul4732saini/fise"><img src="https://img.shields.io/github/stars/rahul4732saini/fise.svg?style=social&label=Star&maxAge=60" alt="StarProject"></a>
<a href="https://www.twitter.com/rahulsaini4732"><img src="https://img.shields.io/twitter/follow/rahulsaini4732?style=social&label=Follow&maxAge=60" alt="Twitter"></a>
<a href="https://www.linkedin.com/in/rahul-saini-9191a5286/)"><img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=social&logo=linkedin&maxAge=60" alt="Linkedin"></a>

<h2 align=center>Description</h2>

**FiSE (File Search Engine)** is a powerful cross-platform command line utility designed for seamless file, directory, and content search and manipulation. It empowers users with the ability to perform comprehensive search operations using intuitive SQL-like commands. It streamlines file management tasks, making it simple to locate, query, and modify files and directories with precision and efficiency. Additionally, this utility allows exporting search records to files and databases in a professional manner. Ideal for developers, system administrators, and power users, FiSE enhances productivity by providing a robust and flexible toolset for all file system operations.

<h2 align=center>Features</h2>

1. **Cross-Platform Compatibility**: Works seamlessly across multiple operating systems, including Windows, macOS, and Linux.

2. **Comprehensive Search Operations**: Performs detailed searches for files, directories, and content within files with precise and efficient results.

3. **Intuitive SQL-like Commands**: Utilizes familiar SQL-like syntax for conducting searches and managing files, reducing the learning curve.

4. **Advanced File Management**: Provides tools for locating, querying, and modifying files and directories with precision and efficiency.

5. **Professional Export Capabilities**: Offers export functionalities for search results to external files and databases, facilitating better data management and reporting.

6. **Productivity Enhancement Tools**: Enhances workflow and efficiency with a comprehensive and flexible toolset for all file system operations.

<h2 align=center>Quick Guide</h2>

This guide offers an overview of the utility's basic usage, highlighting some of the commonly used queries. It enables users to efficiently search, query, and manipulate files and directories across different operating systems.

**FiSE** offers two broad categories of operations, namely **Search** and **Delete**. These operations can be performed on files, file contents, and directories, with the exception for file contents for the Delete operation.

### Query Syntax Breakdown

The basic syntax of the query is shown below:

- Search Query:

```SQL
EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>]) (R|RECURSIVE) SEARCH[<PARAMETERS>] <FIELDS> FROM (RELATIVE|ABSOLUTE) <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

- Delete Query:

```SQL
(R|RECURSIVE) DELETE[<PARAMETERS>] FROM (RELATIVE|ABSOLUTE) (<FILEPATH>|<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

Where:

1. `EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>])` is an optional command exclusive to the search operation and is used to export search records to a file or database.
2. `(R|RECURSIVE)` is an optional command used to recursively include all the files/directories present within the subdirectories of the specified directory. If not explicitly specified, operations are only limited to the root directory.
3. `(SEARCH|DELETE)[<PARAMETERS>]` defines the desired operation to be performed. Additional parameters can be specified within `[]` to toggle operations between different file types, and file-modes explicitly for data search operation.
4. `<FIELDS>` is only limited to search operations for accessing metadata fields related to the searched files, data, or directories. Field names must be separated by commas.
5. `(RELATIVE|ABSOLUTE)` is an optional command to specify whether to include the absolute path of the files/directories in the operation if the specified path to the directory is relative.
6. `(<FILEPATH>/<DIRECTORYPATH>)` defines the path to the file/directory to operate upon. Filepath is only limited to data search operations as other operations cannot be performed on a single file.
7. `WHERE <CONDITIONS>` is an optional query segment and is used for define conditions for filtering files, data, or directories.

Several example for both query types are defined in the following sections.

### Overview of Search operation

The **Search** operation encompasses the ability to query files, file contents, and directories facilitating precise retrieval by allowing users to filter records based on specified search conditions.

#### Search Query Syntax

- File Search Query:

```SQL
EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>]) (R|RECURSIVE) SELECT([TYPE FILE]) <FIELDS> FROM (RELATIVE|ABSOLUTE) <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

- Data Search Query:

```SQL
EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>]) (R|RECURSIVE) SELECT[TYPE DATA(, MODE (TEXT|BYTES))] <FIELDS> FROM (RELATIVE|ABSOLUTE) (<FILEPATH>|<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

- Directory Search Query:

```SQL
EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>]) (R|RECURSIVE) SELECT[TYPE DIR] <FIELDS> FROM (RELATIVE|ABSOLUTE) <DIRECTORYPATH> (WHERE <CONDITIONS>)
```

#### Search Query Examples

```SQL
SELECT * FROM ./fise WHERE name LIKE '^.*\.py$'
```

```SQL
EXPORT FILE[./records.csv] R SELECT[TYPE FILE] RELATIVE * FROM .
```

```SQL
R SELECT[TYPE DIR] name, parent FROM ABSOLUTE ./fise WHERE name IN ('query', 'common')
```

```SQL
EXPORT SQL[mysql] RECURSIVE SELECT[TYPE DIR] * FROM . WHERE name IN ('fise', 'tests', '.github') AND parent LIKE '^.*fise$'
```

```SQL
SELECT[TYPE DATA] lineno, data FROM ./fise/query/parsers.py WHERE "This" IN data AND lineno BETWEEN (30, 210)
```

```SQL
EXPORT FILE[./data.xlsx] R SELECT[TYPE DATA] * FROM ./fise/query WHERE name IN ('parsers.py', 'operators.py') AND data LIKE '^.*get_files.*$'
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
DELETE FROM ./fise WHERE atime < '2015-08-15' AND name != "main.py"
```

```SQL
R DELETE[TYPE FILE] FROM . WHERE name LIKE '^.*\.(js|cpp)$' OR SIZE[b] = 0
```

```SQL
DELETE[TYPE DIR] FROM . WHERE name IN ("temp", "__pycache__", "test")
```

```SQL
R DELETE[TYPE DIR] FROM ./fise
```

## Legals

**FiSE** is distributed under the MIT License. Refer to [LICENSE](./LICENSE) for more details.

## Call for Contributions

The **FiSE** project always welcomes your precious expertise and enthusiasm!
The package relies on its community's wisdom and intelligence to investigate bugs and contribute code. We always appreciate improvements and contributions to this project.
