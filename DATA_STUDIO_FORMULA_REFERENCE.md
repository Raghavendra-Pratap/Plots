# Data Studio Formula Reference (Unified + Legacy)

## TEXT_JOIN
**Aliases:** CONCAT, CONCATENATE, TEXTJOIN
**Description**: Joins text values together, with optional delimiter and empty handling.
**Syntax**: `TEXT_JOIN(delimiter, ignore_empty, text1, text2, …)`
**Parameters**:
- delimiter → Character(s) placed between joined texts
- ignore_empty → TRUE/FALSE (skip blanks or not)
- text1, text2… → Values to join
**Example**: `TEXT_JOIN(', ', TRUE, City, State, Country)`
**Use Case**: Create address strings or combine fields into a single column.




## TEXT_LENGTH
**Aliases:** LEN
**Description**: Returns the length of a text string.
**Syntax**: `TEXT_LENGTH(text)`
**Parameters**:
- text → The text string or column.
**Example**: `TEXT_LENGTH(Name)`

**Use Case**: Check if codes or IDs meet expected length.

**Category**: Text

**Status**: ✅ Available



## FIND_TEXT

**Aliases:** FIND, SEARCH

**Description**: Finds the position of text within another string.

**Syntax**: `FIND_TEXT(find_text, within_text, [start_num])`

**Parameters**:
- find_text → The text to locate
- within_text → The text to search within
- start_num → (optional) Starting position

**Example**: `FIND_TEXT('Inc', CompanyName)`

**Use Case**: Locate substrings such as domain from email addresses.

**Category**: Text

**Status**: ✅ Available



## PROPER_CASE

**Aliases:** PROPER, propper

**Description**: Converts text to proper case (capitalize each word).

**Syntax**: `PROPER_CASE(text)`

**Parameters**:
- text → The text string or column.

**Example**: `PROPER_CASE(Name)`

**Use Case**: Clean inconsistent capitalization in names or titles.

**Category**: Text

**Status**: ✅ Available



## TRIM_TEXT

**Aliases:** TRIM

**Description**: Removes extra spaces from text, leaving single spaces between words.

**Syntax**: `TRIM_TEXT(text)`

**Parameters**:
- text → The text string or column.

**Example**: `TRIM_TEXT(Comments)`

**Use Case**: Clean data imported with inconsistent spacing.

**Category**: Text

**Status**: ⏳ Planned



## ADD_VALUES

**Aliases:** ADD

**Description**: Adds two numbers or columns.

**Syntax**: `ADD_VALUES(a, b)`

**Parameters**:
- a → First number
- b → Second number

**Example**: `ADD_VALUES(Price, Tax)`

**Use Case**: Calculate total cost including tax.

**Category**: Math

**Status**: ✅ Available



## STANDARD_DEVIATION

**Aliases:** STDEV, STDDEV

**Description**: Returns the standard deviation of a column.

**Syntax**: `STANDARD_DEVIATION(values)`

**Parameters**:
- values → Column of numbers

**Example**: `STANDARD_DEVIATION(Sales)`

**Use Case**: Check variability in sales data.

**Category**: Statistics

**Status**: ✅ Available



## VARIANCE

**Description**: Returns the variance of a column.

**Syntax**: `VARIANCE(values)`

**Parameters**:
- values → Column of numbers

**Example**: `VARIANCE(Sales)`

**Use Case**: Measure spread of numerical data.

**Category**: Statistics

**Status**: ✅ Available



## PERCENTILE

**Aliases:** precentile

**Description**: Returns the nth percentile of a column.

**Syntax**: `PERCENTILE(values, percentile)`

**Parameters**:
- values → Column of numbers
- percentile → Value between 0 and 100

**Example**: `PERCENTILE(Sales, 90)`

**Use Case**: Find top 10% cutoff of sales figures.

**Category**: Statistics

**Status**: ✅ Available



## DATE_DIFF

**Aliases:** DAYS_SINCE, DATEDIF

**Description**: Returns the difference in days between two dates or between a date and today.

**Syntax**: `DATE_DIFF(date1, date2)`

**Parameters**:
- date1 → First date
- date2 → Second date or TODAY()

**Example**: `DATE_DIFF(OrderDate, TODAY())`

**Use Case**: Calculate customer age or order age.

**Category**: Date

**Status**: ✅ Available



## EXTRACT_YEAR

**Description**: Extracts the year from a date.

**Syntax**: `EXTRACT_YEAR(date)`

**Parameters**:
- date → Date value

**Example**: `EXTRACT_YEAR(OrderDate)`

**Use Case**: Group sales by year.

**Category**: Date

**Status**: ✅ Available



## EXTRACT_DAY

**Aliases:** extract_days

**Description**: Extracts the day from a date.

**Syntax**: `EXTRACT_DAY(date)`

**Parameters**:
- date → Date value

**Example**: `EXTRACT_DAY(OrderDate)`

**Use Case**: Find sales on specific days of the month.

**Category**: Date

**Status**: ✅ Available



## LOOKUP

**Aliases:** VLOOKUP, HLOOKUP, XLOOKUP, INDEXMATCH

**Description**: Finds values in a table or range based on a key.

**Syntax**: `LOOKUP(lookup_value, lookup_table, return_column)`

**Parameters**:
- lookup_value → Value to find
- lookup_table → Dataset or range
- return_column → Column to return

**Example**: `LOOKUP(CustomerID, Orders, OrderDate)`

**Use Case**: Retrieve order dates by customer ID.

**Category**: Lookup

**Status**: ✅ Available



## ADVANCED_LOOKUP

**Aliases:** LOOKUP_ALL

**Description**: Returns all matching values in a dataset for a given key.

**Syntax**: `ADVANCED_LOOKUP(lookup_value, lookup_table, return_column)`

**Parameters**:
- lookup_value → Value to find
- lookup_table → Dataset or range
- return_column → Column to return

**Example**: `ADVANCED_LOOKUP(CustomerID, Orders, Product)`

**Use Case**: Retrieve all products purchased by a customer.

**Category**: Lookup

**Status**: ✅ Available



## REMOVE_DUPLICATES

**Aliases:** remove_duplicate

**Description**: Removes duplicate rows based on selected columns.

**Syntax**: `REMOVE_DUPLICATES(columns)`

**Parameters**:
- columns → Column(s) to check for duplicates

**Example**: `REMOVE_DUPLICATES(CustomerID)`

**Use Case**: Keep unique records in datasets.

**Category**: Cleaning

**Status**: ✅ Available



## IDENTIFY_DUPLICATES

**Description**: Flags duplicate rows without removing them.

**Syntax**: `IDENTIFY_DUPLICATES(columns)`

**Parameters**:
- columns → Column(s) to check for duplicates

**Example**: `IDENTIFY_DUPLICATES(Email)`

**Use Case**: Mark duplicate entries for review.

**Category**: Cleaning

**Status**: ⏳ Planned



## COUNT_DUPLICATES

**Description**: Adds a column showing count of duplicate instances.

**Syntax**: `COUNT_DUPLICATES(columns)`

**Parameters**:
- columns → Column(s) to check for duplicates

**Example**: `COUNT_DUPLICATES(CustomerID)`

**Use Case**: Find frequency of repeated IDs.

**Category**: Cleaning

**Status**: ⏳ Planned



## DUPLICATE_SEQUENCE

**Description**: Numbers each duplicate row sequentially (1,2,3…).

**Syntax**: `DUPLICATE_SEQUENCE(columns)`

**Parameters**:
- columns → Column(s) to check for duplicates

**Example**: `DUPLICATE_SEQUENCE(CustomerID)`

**Use Case**: Retain first occurrence and track duplicate order.

**Category**: Cleaning

**Status**: ⏳ Planned



## DEDUP_KEEP

**Description**: Removes duplicates but keeps one based on rules (first/last/min/max).

**Syntax**: `DEDUP_KEEP(columns, rule)`

**Parameters**:
- columns → Column(s) to check
- rule → FIRST, LAST, MIN(col), MAX(col)

**Example**: `DEDUP_KEEP(CustomerID, FIRST)`

**Use Case**: Keep only earliest order per customer.

**Category**: Cleaning

**Status**: ⏳ Planned


