<h1 align=center><img src="../assets/fise.svg" width=300></h1>

<h1 align=center>Getting Started</h1>

Welcome to **FiSE (File Search Engine)**! This comprehensive guide will walk you through the steps to install FiSE, set it up, and perform basic operations.

<h2 align=center>Introduction</h2>

**FiSE (File Search Engine)** is a powerful cross-platform command line utility designed for performing seamless file, directory, and data search and manipulation operations. It empowers users with the ability to perform comprehensive search operations using intuitive SQL-like commands streamlining file management tasks, making it simple to locate, query, and modify files and directories with precision and efficiency. Additionally, this utility allows exporting search records to files and databases in a professional manner. Ideal for developers, system administrators, and power users, FiSE enhances productivity by providing a robust and flexible toolset for all file system operations.

<h2 align=center>Installation</h2>

This section will walk you through the steps to install and setup FiSE on your system.

### Prerequisites

Before installing FiSE, please ensure that you have the following prerequisites installed on your system:

- **Python**: FiSE requires **Python 3.10** or higher, ensure it is installed on your system along with a package manager for python such as **pip**. You can download Python from [python.org](https://www.python.org/downloads/).

- **Git** (Optional): While not mandatory, having **Git** installed can facilitate cloning the **FiSE** GitHub repository onto your system. You can download Git from [git-scm.com](https://www.git-scm.com).

### Installation

To install FiSE on your system, follow the steps mentioned below:

1. **Clone the Repository**:

   If you have **Git** installed, you can use the following git command to clone the **FiSE** GitHub repository into the current working directory:

   ```bash
   git clone https://github.com/rahul4732saini/fise.git
   ```

   Otherwise, you can download the source code archive file from the GitHub repository at [FiSE](https://www.github.com/rahul4732saini/fise).

2. **Change the current working directory**:

   Change the current directory to `./fise` to perform the remaining installation:

   ```bash
   cd ./fise
   ```

3. **Install Dependencies**:

   All the base requirements are specified within [requirements.txt](../requirements/requirements.txt) which can be installed using the following command:

   ```bash
   python -m pip install -r requirements.txt --no-cache-dir
   ```

   To utilize the additional features offered by FiSE, including the database export functionality, it is necessary to install the supplementary requirements specified within [requirements-extra.txt](../requirements/requirements-extra.txt). These requirements can be installed using the same procedure as mentioned before:

   ```bash
   python -m pip install -r requirements-extra.txt --no-cache-dir
   ```

4. **(Optional) Build Application**:

   To build the application on your current system, follow the steps mentioned under the [Build Guide](./build-executable.md).

<h2 align=center>Running FiSE</h2>

Once all the steps mentioned above for installation are completed, you can run the program using the following command to run the [main.py](../fise/main.py) file present within the **fise** directory:

```bash
python fise/main.py
```

Running this command opens a command-line interface similar to **SQL**, allowing users to type in queries and view the corresponding output.

<h2 align=center>Basic Usage</h2>

FiSE allows you to perform file, directory, and data searches using SQL-like commands. Here are a few basic examples to get you started:

### Example 1: Perform a File Search

   To search for all Python files `*.py` in the current directory:

   ```SQL
   SELECT * FROM . WHERE name LIKE ".*\.py"
   ```

### Example 2: Search for Specific Data

   To search for a specific string `FiSE` within files:

   ```SQL
   SELECT[TYPE DATA, MODE BYTES] * FROM . WHERE LINENO IN (10, 100) AND DATA LIKE ".*FiSE.*"
   ```

### Example 3: Delete Files

   To delete all JavaScript files `*.js` from a directory:

   ```SQL
   DELETE FROM . WHERE name LIKE ".*\.js"
   ```

### Example 4: Delete Directories

   To delete all directories which were created before `2020-01-01`:

   ```SQL
   DELETE[TYPE DIR] FROM . WHERE ctime < "2020-01-01"
   ```

<h2 align=center>Next Steps</h2>

To explore more advanced features, refer to the following guides for detailed insights into each topic:

1. **[Query Syntax](./query/syntax.md)**: Learn the syntax for executing various queries in FiSE.
2. **[Query Operations](./query/operations.md)**: Explore the various query operations available in FiSE.
3. **[Query Conditions](./query/query-conditions.md)**: Discover the ways to write precise and efficient conditions for filtering search/delete records.

---
