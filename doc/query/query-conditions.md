<h1 align=center>Query Conditions Guide</h1>

This guide aims to provide a comprehensive overview of query conditions for filtering records in file, data and directory operations. It explains the various types of operators and operands that can be employed to define conditions, offering examples to illustrate their application. By following this guide, you will enhance your ability to construct precise and effective queries.

### Basic Overview

Conditions are defined at the end of the query after the path specifications and start with the `WHERE` keyword marking the beginning of conditions segment. Following is a basic representation of how the query would look like:

```SQL
SELECT * FROM . WHERE <CONDITIONS>
```

All conditions are separated by delimiters listed under [Logical Operators](#logical-operators).

<h2 align=center>Operators</h2>

Operators are symbols that specify the type of operation to be performed within individual query conditions. The following sections cover all the operators which can be used for defining query conditions in FiSE.

### Comparison Operators

- `=` : Equals
- `!=`: Not equal
- `<` : Less than
- `<=`: Less than or equal to
- `>` : Greater than
- `>=`: Greater than or equal to

### Collective Operators

- `IN` : Checks if a value is within an array of values. Eg: `name IN ("main.py", "classes.py")`
- `BETWEEN` : Checks if a value lies within a range of values. Eg: `ctime BETWEEN ("2022-01-01", "2023-01-01")`

### Logical Operators

Also known as **condition delimiters**, these operators are used for separating conditions from one-another.

- `AND` : Only Evaluates to `true` if both of the adjacent conditions are `true`.
- `OR` : Evaluates to `true` if either of the adjacent conditions are `true`.

### Miscellaneous Operators

- `LIKE` : Matches a string pattern (Uses standard Regular Expressions. For a deeper insight, please refer to the [Wikipedia](https://en.wikipedia.org/wiki/Regular_expression) page.)

<h2 align=center>Operands</h2>

Operands are the values or entities on which operators act. FiSE allows operands from various data types to be a part of query conditions including strings, integers, floats, regular expressions, and metadata fields. The following sections provide a deeper insight into individual operand types.

### Strings

Strings are textual data enclosed within single or double quotes (' or ").

### Integers

Integers are whole numbers without any decimal points. They are typically used to represent numerical file attributes such as size in queries.

### Floats

Floats are numbers with decimal points. They can be used for more precise numerical comparisons within FiSE queries.


### None

Similar to the `NULL` keyword in SQL, FiSE uses `None` to represent empty values or undefined data. This can also be used within query conditions to verify the presence or absence of data.

### Arrays

Arrays in FiSE queries are collections of values(strings, integers, floats, or metadata fields) enclosed within parentheses `()`, separated by commas. They allow users to specify multiple values for operations like membership checking (`IN` operation) or to check if a value lies within a specific range (`BETWEEN` operation).

### Regular Expressions

Regular expressions act as a powerful tool for pattern matching within strings. These expressions are useful for users to search for files or directories based on complex string patterns.

These regular expressions are also defined as strings enclosed within single or double quotes (' or ").

**NOTE**: Regular expressions are only limited to the `LIKE` operation. These are specified after the operator in the condition. Below is the basic syntax for reference:

```SQL
<STRING|FIELD> LIKE <REGEX>
```

### Metadata Fields

Fields refer to attributes or columns within the data being queried. In FiSE queries, fields represent metadata values associated with files or directories, such as name, size, type, or timestamps.

To get more details about the metadata fields available for different query operations, please refer to [Query-Fields](./query-fields.md).

<h2 align=center>Defining Conditions</h2>

Below is the basic structure for defining query conditions:

```SQL
<CONDITION> <DELIMITER> <CONDITION> ...
```

Where each individual condition is defined in the following manner:

```SQL
<OPERAND> <OPERATOR> <OPERAND>
```

### Nested Conditions

FiSE also allows condition nesting with the use of curly braces `()`. Conditions can be nested as deeply as desired within a query.

<h2 align=center>Examples</h2>

**Example 1**: Recursively select all files from the current directory whose name is `__init__.py`:

```SQL
R SELECT parent, size[KB], ctime FROM . WHERE name = "__init__.py"
```

**Example 2**: Recursively delete all files from `./documents` directory which have not been accessed since `2018-06-13` and have a filetype of `.docx`:

```SQL
R DELETE FROM ./documents WHERE atime <= "2018-06-13" AND type = ".docx"
```

**Example 3**: Select all files from `/home/user` directory whose name is in the following names: `roadmap.txt`, `projects.txt` and `specifications.txt`.

```SQL
SELECT * FROM `/home/user/` WHERE name IN ("roadmap.txt", "projects.txt", "specifications.txt")
```

**Example 4**: Select all datalines present within the files in the current directory which have a filetype `.py` and have the word `parse` in them.

```SQL
SELECT[TYPE DATA, MODE BYTES] * FROM . WHERE FILETYPE = '.py' AND DATALINE like ".*parse.*"
```

**Example 5**: Select all directories from `./media` directory which were created between `2010-01-01` and `2020-12-31` or `2023-01-01` and `2023-12-31` and whose name ends with `-pictures`:

```SQL
SELECT[TYPE DIR] * FROM ./media WHERE (ctime BETWEEN ("2010-01-01", "2020-12-31") or ctime BETWEEN ("2023-01-01", "2023-12-31")) AND NAME LIKE '.*-pictures$'
```

---
