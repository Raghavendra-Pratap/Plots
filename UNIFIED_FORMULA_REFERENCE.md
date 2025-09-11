# Unified Formula Reference

## IF

**Description:** Returns one value if a condition is TRUE and another if FALSE.

**Example:** `IF(age > 18, 'Adult', 'Minor')`



## PIVOT

**Description:** Transforms unique values from one column into multiple columns.

**Example:** `PIVOT(Category, Sales, SUM)`



## PIVOT_TABLE

**Description:** Creates a pivot table by grouping data and applying aggregations.

**Example:** `PIVOT_TABLE(Region, SUM(Sales))`



## SUM

**Description:** Returns the sum of values.

**Example:** `SUM(Sales)`



## ADD

**Description:** Adds two numbers or columns.

**Example:** `ADD(Price, Tax)`



## UNPIVOT

**Aliases:** DEPIVOT

**Description:** Converts columns into rows (reverse of pivot).

**Example:** `UNPIVOT(Jan, Feb, Mar)`



## COUNT

**Description:** Returns the number of values in a column.

**Example:** `COUNT(CustomerID)`



## UNIQUE_COUNT

**Aliases:** COUNT_UNIQUE

**Description:** Returns the number of unique values in a column.

**Example:** `UNIQUE_COUNT(CustomerID)`



## DATE

**Aliases:** DATE_FORMAT

**Description:** Formats a date or converts a string into a date format.

**Example:** `DATE(OrderDate, 'YYYY-MM-DD')`



## UPPER

**Description:** Converts text to uppercase.

**Example:** `UPPER(Name)`



## LOWER

**Description:** Converts text to lowercase.

**Example:** `LOWER(Name)`



## PROPER

**Aliases:** propper

**Description:** Converts text to proper case (capitalize each word).

**Example:** `PROPER(Name)`



## TITLE_CASE

**Description:** Converts text to title case.

**Example:** `TITLE_CASE(BookTitle)`



## TEXT

**Description:** Converts values to text.

**Example:** `TEXT(Sales)`



## SUBTRACT

**Description:** Subtracts one number or column from another.

**Example:** `SUBTRACT(Revenue, Cost)`



## MULTIPLY

**Description:** Multiplies two numbers or columns.

**Example:** `MULTIPLY(Price, Quantity)`



## DIVIDE

**Description:** Divides one number or column by another.

**Example:** `DIVIDE(Sales, Quantity)`



## TEXT_LENGTH

**Aliases:** LEN

**Description:** Returns the length of a text string.

**Example:** `TEXT_LENGTH(Name)`



## FIND_TEXT

**Aliases:** SEARCH, FIND

**Description:** Finds the position of text in a string.

**Example:** `FIND_TEXT('Inc', CompanyName)`



## DAYS_SINCE

**Aliases:** DATE_DIFF

**Description:** Returns the number of days between two dates or between a date and today.

**Example:** `DAYS_SINCE(OrderDate)`



## EXTRACT_YEAR

**Description:** Extracts the year from a date.

**Example:** `EXTRACT_YEAR(OrderDate)`



## EXTRACT_MONTH

**Description:** Extracts the month from a date.

**Example:** `EXTRACT_MONTH(OrderDate)`



## EXTRACT_DAY

**Aliases:** extract_days

**Description:** Extracts the day from a date.

**Example:** `EXTRACT_DAY(OrderDate)`



## SUMIF

**Description:** Sums values that meet a condition.

**Example:** `SUMIF(Region = 'East', Sales)`



## COUNTIF

**Description:** Counts values that meet a condition.

**Example:** `COUNTIF(Region = 'East')`



## AVERAGEIF

**Description:** Averages values that meet a condition.

**Example:** `AVERAGEIF(Region = 'East', Sales)`



## LOOKUP

**Aliases:** VLOOKUP, HLOOKUP, INDEXMATCH, XLOOKUP

**Description:** Finds values in a column or table based on a key.

**Example:** `LOOKUP(CustomerID, OrdersTable)`



## REMOVE_DUPLICATES

**Aliases:** remove_duplicate

**Description:** Removes duplicate rows from a dataset.

**Example:** `REMOVE_DUPLICATES(CustomerID)`



## MARK_DUPLICATES

**Aliases:** mark_duplicate

**Description:** Marks duplicate rows in a dataset.

**Example:** `MARK_DUPLICATES(CustomerID)`



## FILLNA

**Aliases:** fill_NA

**Description:** Replaces missing values with a specified value or method.

**Example:** `FILLNA(Sales, 0)`



## IFERROR_DIVIDE

**Aliases:** IFERROR

**Description:** Divides two numbers and handles division by zero or errors.

**Example:** `IFERROR_DIVIDE(Sales, Quantity, 0)`



## ROW_SUM

**Description:** Sums across multiple selected columns in a row.

**Example:** `ROW_SUM(Q1, Q2, Q3, Q4)`



## MEDIAN

**Description:** Returns the median of a column.

**Example:** `MEDIAN(Sales)`



## MODE

**Description:** Returns the mode of a column.

**Example:** `MODE(Sales)`



## STDDEV

**Aliases:** STDEV

**Description:** Returns the standard deviation of a column.

**Example:** `STDDEV(Sales)`



## VARIANCE

**Description:** Returns the variance of a column.

**Example:** `VARIANCE(Sales)`



## RANK

**Description:** Returns the rank of each value in a column.

**Example:** `RANK(Sales)`



## PERCENTILE

**Aliases:** precentile

**Description:** Returns the nth percentile of a column.

**Example:** `PERCENTILE(Sales, 90)`



## TRANSPOSE

**Description:** Transposes rows into columns and vice versa.

**Example:** `TRANSPOSE(Table)`



## ROUND_COLUMN

**Aliases:** Round_column

**Description:** Rounds values in a column to a specified number of digits.

**Example:** `ROUND_COLUMN(Price, 2)`



## CEIL_COLUMN

**Aliases:** Ceil_Column

**Description:** Rounds values in a column up to the nearest integer.

**Example:** `CEIL_COLUMN(Price)`



## FLOOR_COLUMN

**Aliases:** Floor_column

**Description:** Rounds values in a column down to the nearest integer.

**Example:** `FLOOR_COLUMN(Price)`



## ROLLING_MEAN

**Description:** Calculates the moving average over a window of values.

**Example:** `ROLLING_MEAN(Sales, 7)`



## ADVANCED_LOOKUP

**Description:** Finds all matching values in a dataset for a given key.

**Example:** `ADVANCED_LOOKUP(CustomerID, OrdersTable)`


