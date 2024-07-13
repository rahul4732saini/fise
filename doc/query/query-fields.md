<h1 align=center>Query Fields</h1>

This section provides a detailed overview of the various metadata fields that can be used for search and delete operations. Understanding these fields will help you craft precise queries to efficiently manage files, directories, and data.

### Directory Metadata Fields

1. **name**:
    - Extracts the name of the directory.
    - **Alias**: *filename*

2. **path**:
    - Extracts the relative or absolute path of the directory based on the specified path type or if it is explicitly designated as ABSOLUTE in the query.
    - **Alias**: *filepath*

3. **parent**:
    - Extracts the relative or absolute path pf the parent directory based on the specified path type or if it is explicitly designated as ABSOLUTE in the query.

4. **create_time**:
    - Extracts the creation time of the directory.
    - **Alias**: *ctime*

5. **modify_time**:
    - Extracts the last modification time of the directory.
    - **Alias**: *mtime*

6. **access_time**:
    - Extracts the last access time of the directory.
    - **Alias**: *atime*

7. **owner**:
    - Extracts the name of the owner of the directory.
    - Only available on POSIX-based systems.

8. **group**:
    - Extracts the name of the group of the directory.
    - Only available on POSIX-based systems.

9. **permissions**:
    - Extracts the 5-digit permissions code of the directory.
    - Only available on POSIX-based systems.
    - **Alias**: *perms*

### File Metadata Fields

**NOTE**: All metadata fields applicable to directories are also relevant for files, with the addition of the following specific fields:

1. **filetype**:
    - Extracts the filetype of file.
    - **Alias**: *type*

2. **size**:

    - Extracts the size of the file.

    - Users can also extract the file size in different units by accompanying the field name 'size' with a square brackets `[]` and typing in a unit specified within the **Different Size Units** section below. Eg: `size[KB]`, `size[GiB]` and `size[b]`.

    - **Different Size Units**:

        b, B, Kib, Kb, KiB, KB, Mib, Mb, MiB, MB, Gib, Gb, GiB, GB, Tib, Tb, TiB, TB

        All units correspond to their standard equivalents in size.

### File-contents Metadata Fields

1. **name**:
    - Extracts the name of the file.

2. **path**:
    - Extracts the relative or absolute path to the file based on the specified path type or if it is explicitly designated as ABSOLUTE in the query.

3. **filetype**:
    - Extracts the filetype of the file.
    - **Alias**: *type*

4. **dataline**:
    - Extracts the data at the current line.
    - **Alias**: *data*, *line*

5. **lineno**:
    - Extract the line number of the dataline.

---
