# SQL Essentials Cheat Sheet

A concise guide to the core concepts and commands you'll use 90% of the time in SQL.

---

## 1. The Basics (CRUD)
The foundation of interacting with any database.

*   **`SELECT`**: Retrieves data. Use `SELECT *` for all columns or specify names.
*   **`INSERT INTO`**: Adds new rows to a table.
*   **`UPDATE`**: Modifies existing data. **Always** use a `WHERE` clause to avoid updating the whole table.
*   **`DELETE`**: Removes data. Like update, requires a `WHERE` clause for safety.

## 2. Filtering and Sorting
*   **`WHERE`**: Filters records based on conditions (e.g., `WHERE price > 100`).
*   **`LIKE`**: Pattern matching (`%` for any sequence, `_` for a single character).
*   **`ORDER BY`**: Sorts results `ASC` (default) or `DESC`.
*   **`LIMIT` / `TOP`**: Restricts the number of rows returned.

## 3. Joins (Combining Tables)
*   **`INNER JOIN`**: Returns records with matching values in both tables.
*   **`LEFT JOIN`**: Returns all records from the left table, and matched records from the right (fills with `NULL` if no match).
*   **`RIGHT JOIN`**: The opposite of a Left Join.
*   **`FULL JOIN`**: Returns all records when there is a match in either table.

## 4. Aggregations
Used for performing calculations on multiple rows.
*   **`COUNT()`**: Returns the number of rows.
*   **`SUM()` / `AVG()`**: Calculates the total or average of a numeric column.
*   **`GROUP BY`**: Groups rows that have the same values into summary rows.
*   **`HAVING`**: Like `WHERE`, but for filtering **after** an aggregation has been performed.

## 5. Intermediate Concepts
*   **Subqueries**: Nesting a query inside another (e.g., `SELECT * FROM t1 WHERE id IN (SELECT id FROM t2)`).
*   **CTEs (Common Table Expressions)**: Temporary result sets defined using the `WITH` keyword to make complex queries readable.
*   **Indexes**: Used to speed up data retrieval. Think of it like a book's index.
*   **Constraints**: Rules for data (e.g., `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`).

---


## 6. Logical Order of Operations
The most important thing to remember is that SQL queries are **written** in one order but **executed** by the database engine in another. Understanding this helps you debug why an alias might not work in a `WHERE` clause.

### Written Order (Syntax)
1. `SELECT`
2. `DISTINCT`
3. `FROM`
4. `JOIN`
5. `WHERE`
6. `GROUP BY`
7. `HAVING`
8. `ORDER BY`
9. `LIMIT`

### Execution Order (Logical)
1. **`FROM` / `JOIN`**: The database gets the base data first.
2. **`WHERE`**: Filters individual rows.
3. **`GROUP BY`**: Aggregates the filtered rows.
4. **`HAVING`**: Filters the aggregated groups.
5. **`SELECT`**: Determines which columns to show (and handles aliases).
6. **`DISTINCT`**: Removes duplicates.
7. **`ORDER BY`**: Sorts the final result set.
8. **`LIMIT`**: Clips the final output.

---



## 7. Window Functions
Unlike `GROUP BY`, Window Functions perform calculations across a set of rows while still returning individual rows.

*   **`ROW_NUMBER()`**: Assigns a unique ID to each row.
*   **`RANK()`**: Assigns a rank (with gaps for ties).
*   **`DENSE_RANK()`**: Assigns a rank (no gaps for ties).
*   **`OVER(PARTITION BY ... ORDER BY ...)`**: The syntax that defines the "window."




## 8. Common Pitfalls & Best Practices

Understanding the **Logical Order of Execution** helps avoid these frequent mistakes:

*   **Alias Availability**: You cannot use an alias defined in `SELECT` within your `WHERE` clause. This is because the database filters rows (`WHERE`) *before* it even looks at what columns you want to show (`SELECT`).
    *   ❌ `SELECT price * 2 AS double_price FROM sales WHERE double_price > 100`
    *   ✅ `SELECT price * 2 AS double_price FROM sales WHERE price * 2 > 100`

*   **WHERE vs. HAVING**: Use `WHERE` to filter raw data (rows) and `HAVING` to filter aggregated data (groups). Filtering with `WHERE` is more efficient because it reduces the data before the database performs calculations.

*   **NULL Comparison**: You cannot use `=` or `!=` with `NULL`. 
    *   ❌ `WHERE column = NULL`
    *   ✅ `WHERE column IS NULL` or `WHERE column IS NOT NULL`

*   **Select Star (`*`)**: While convenient for exploration, avoid using `SELECT *` in production code. It increases network traffic and can break your application if the table schema changes.

*   **The "N+1" Problem**: Avoid running SQL queries inside a programming loop (like a `for` loop). Use **Joins** or **Subqueries** to fetch all the data you need in a single trip to the database.

---


## 9. Pro-Level SQL Patterns & Skills

Beyond basic syntax, these are the "Swiss Army Knife" patterns that solve real-world data problems.

### Self-Joins for Time Windows
Joining a table to itself is the go-to method for comparing a row against its own history or future.
*   **Use Case**: Calculating the time difference between two consecutive orders.
*   **Concept**: Match `Table A` (Current Order) with `Table A` (Previous Order) using a unique ID and a time offset.

### The "Group By" Golden Rule
Whenever you use an **Aggregate Function** (`SUM`, `COUNT`, `AVG`) alongside regular columns, **every non-aggregated column** must appear in the `GROUP BY` clause.
*   **Correct**: `SELECT department, city, COUNT(*) FROM employees GROUP BY department, city;`
*   **Incorrect**: `SELECT department, city, COUNT(*) FROM employees GROUP BY department;` (The database won't know which `city` to show for the department).

### Handling "Top N" per Group
To find the "top 3 sales per region," a standard `LIMIT` won't work because it limits the whole result set.
*   **Skill**: Use a **Window Function** (`ROW_NUMBER()` or `RANK()`) inside a **CTE**, then filter the rank in the outer query.
*   **Example**: `WHERE rank <= 3`

### Conditional Aggregation (CASE WHEN)
You can "pivot" data or create custom columns during an aggregation by nesting a `CASE` statement inside a `SUM` or `COUNT`.
*   **Example**: `SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) AS shipped_count`
*   **Benefit**: This lets you calculate multiple specific metrics in a single pass over the data.

### Coalesce for Clean Data
The `COALESCE(column, default_value)` function is essential for replacing `NULL` values with something readable (like `0` or `'N/A'`) during reporting.
*   **Example**: `COALESCE(discount, 0)` ensures your math doesn't break if a discount is missing.

---


## Summary: The SQL Core
SQL is a **declarative** language, meaning you describe *what* you want, not *how* to get it. To master it, remember:
1.  **Filtering happens early**: `WHERE` filters rows before any grouping or selecting occurs.
2.  **Aggregates happen late**: `GROUP BY` and `HAVING` only work on the data that survives the initial filter.
3.  **Aliases have limits**: Because `SELECT` is one of the last steps executed, you usually can't use its aliases in your `WHERE` or `GROUP BY` clauses.
4.  **Joins are power**: Relationships between tables (IDs) are what turn flat data into a relational system.

---

## The "Everything" Example
This query combines filtering, joining, aggregating, and window functions to find high-value customers.

```sql
WITH CustomerTotals AS (
    -- 1. Create a CTE to calculate totals per customer
    SELECT 
        c.customer_name,
        c.city,
        SUM(o.order_amount) AS total_spent,
        COUNT(o.order_id) AS order_count
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_date >= '2023-01-01' -- Filter rows early
    GROUP BY c.customer_name, c.city   -- Group for aggregation
    HAVING SUM(o.order_amount) > 500   -- Filter groups late
)
SELECT 
    customer_name,
    city,
    total_spent,
    -- Window function to rank customers by spend within their city
    RANK() OVER(PARTITION BY city ORDER BY total_spent DESC) AS city_rank
FROM CustomerTotals
ORDER BY total_spent DESC              -- Final sorting
LIMIT 10;                             -- Final clipping
