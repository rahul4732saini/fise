<h1 align=center>Query Syntax Guide</h1>

This comprehensive guide offers detailed insights into the query syntax, aiming to help users grasp the various components and structures of different query types enabling them to perform efficient file, directory, and data search and delete operations using SQL-like commands.

<h2 align=center>Query Syntax Breakdown</h2>

**FiSE** offers two primary operations to its users namely **Search** and **Delete**. To get deep insight of these operations, please refer to the [Operations](./operations.md) guide.

#### 1. Search Query Syntax

```SQL
(EXPORT (FILE[<FILEPATH>]|SQL[<DATABASE>])) (R|RECURSIVE) SEARCH[<PARAMETERS>] <FIELDS> FROM (RELATIVE|ABSOLUTE) (<FILEPATH>|<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

#### 2. Delete Query Syntax

```SQL
(R|RECURSIVE) DELETE[<PARAMETERS>] FROM (RELATIVE|ABSOLUTE) (<FILEPATH>|<DIRECTORYPATH>) (WHERE <CONDITIONS>)
```

### Individual Components Explanation

1. **EXPORT FILE[ FILEPATH ]** or **EXPORT SQL[ DATABASE ]**:

    - This segment is optional and is used for exporting search records to a file or database.

    - **NOTE**: Currently, exporting records is only limited to search operations.

    - **File Export**: **FiSE** allows search records export only to the file formats mentioned below under the **Available File Formats** section below. To export to a file, the following rules must be followed:

        - The file specified must be non-existant.
        - The file name must be followed by a allowed suffix, **FiSE** recognizes the file export type explicitly based on the suffix of the file specified.

    - **Available File Formats**: **csv**, **html**, **xlsx** and **json**.
    - **Available Databases**: **mysql**, **postgresql** and **sqlite**.

    - **Example**: `EXPORT FILE[./results.csv]` and `EXPORT SQL[mysql]`

2. **R** or **RECURSIVE**:

    - This segment is optional and allows recursive inclusion of all the files and sub-directories present within the specified directory.

3. **SELECT[ PARAMETERS ]** or **DELETE[ PARAMETERS ]**:

    - This segments includes the operation specifications. Users can choose between two different query operations: **Search** and **Delete**.

    - **Additional parameters** can be specified to toggle between different file-types or file-modes, especially for data search operations. These can be defined within square brackets `[]` adjoining the name of the operation where each parameter is seperated by commas. Refer to the **Parameters Types** section below to know more about the different types of parameters available for operation configuration.

    - **Parameters Types**: The following are the different types of parameters which can be defined within the operation specifications:

        - **TYPE**: It is used to toggle between file, directory and data operation. The type can only be set to `data` for search operation and is not available for delete operations. To specify this parameter, use the following format: `TYPE (FILE|DIR|DATA)`. Eg: `SELECT[TYPE DIR]` configures the operation to work with directories and `DELETE[TYPE FILE]` toggles the operation to work with files. 

        - **MODE**: It is used to toggle between text and bytes filemode. It is only limited to data search operations. To specify this parameter, use the following format: `MODE (TEXT|BYTES)`. Eg: `SELECT[TYPE DATA, MODE BYTES]` toggles the operation to work with bytes data and `SELECT[TYPE DATA, MODE TEXT]` configures the operation to work with text data.

    - **NOTE**: By default, the `TYPE` parameter is set to `file` and the `MODE` is set to `text` for data search operation and do not require explicit mentionings. Users must also note that the `text` filemode can only read text files and will raise an error for bytes data.

    - Operation specifications examples with different parameters:

        - `SELECT` : Select files
        - `DELETE` : Delete files
        - `SELECT[TYPE DIR]` : Select directories
        - `SELECT[TYPE DATA, MODE BYTES]` : Select file-contents in bytes filemode
        - `DELETE[TYPE FILE]` : Delete files
        - `SELECT[TYPE DATA]`: Select file-contents in text filemode

4. **FIELDS**:

    - This segment is only limited to search operations and defines the metadata fields related to the searched files, data, or directories which are to be displayed in the output search dataframe.

    - For a deeper insight into the available metdata fields for different search query types, please refer to the [Query-Fields](./query-fields.md) guide.

5. **ABSOLUTE** or **RELATIVE**:

    - This segment is optional and specifies whether to include the absolute path of the files and directories if the specified path is relative.

6. **FILE PATH** or **DIRECTORY PATH**:

    - Defines the path to the file or directory to operate upon. The path can be either absolute or relative as desired and can be specified directly without any other specifications.

    - **Note**: Paths comprising whitespaces must be enclosed within single quotes `'` or double quotes `"`.

    - **Example**: `./src`, `/usr/local/bin` and `"C:/Program Files/Common Files"`

7. **WHERE CONDITIONS**:

    - This segment is optional and is used for filtering search and delete records based on the specified conditions.

    - For a deeper insight into query conditions, please refer to the [Query-Conditions](./query-conditions.md) guide.

<h2 align=center>Next Steps</h2>

To explore more advanced features, refer to the following guides for detailed insights into each topic:

1. **[Query Fields](./query-fields.md)**: Dive deep and know about the different metadata fields which can be used with different query operations.
2. **[Query Operations](./query/operations.md)**: Explore the various query operations available in FiSE.
3. **[Query Conditions](./query/export.md)**: Discover the ways to write precise and efficient conditions for filtering search and delete records.

---
