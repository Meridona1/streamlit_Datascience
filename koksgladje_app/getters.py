import streamlit as st
import pandas as pd
from db_util import read_sql

# Hämtar alla transaktioner med datum och totalbelopp
@st.cache_data(ttl=300, show_spinner=False)
def get_transactions() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            t.TransactionID   AS transactionid,
            t.StoreID         AS storeid,
            t.CustomerID      AS customerid,
            t.TransactionDate AS date,
            t.TotalAmount     AS totalamount
        FROM Transactions t
        ORDER BY t.TransactionDate
    """)
    # Säkerställer att datumkolumnen är i rätt format
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


# Hämtar detaljerade transaktionsrader (produkter, antal, pris)
@st.cache_data(ttl=300, show_spinner=False)
def get_details() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            td.TransactionID  AS transactionid,
            td.ProductID      AS productid,
            td.Quantity       AS quantity,
            td.PriceAtPurchase AS unitprice,
            td.TotalPrice     AS totalprice
        FROM TransactionDetails td
        ORDER BY td.TransactionID
    """)
    return df


# Hämtar produkter tillsammans med kategorier
@st.cache_data(ttl=300, show_spinner=False)
def get_products_with_categories() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            p.ProductID    AS productid,
            p.ProductName  AS productname,
            p.CategoryID   AS categoryid,
            COALESCE(pc.CategoryName, CAST(p.CategoryID AS TEXT)) AS category,
            p.Description  AS description,
            p.Price        AS price,
            p.CostPrice    AS costprice
        FROM Products p
        LEFT JOIN ProductCategories pc ON p.CategoryID = pc.CategoryID
        ORDER BY p.ProductID
    """)
    return df


# Hämtar alla butiker
@st.cache_data(ttl=300, show_spinner=False)
def get_stores() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            s.StoreID   AS storeid,
            s.StoreName AS storename,
            s.Location  AS county
        FROM Stores s
        ORDER BY s.StoreID
    """)
    return df


# Hämtar kunder. Returnerar tom DataFrame om tabellen saknas.
@st.cache_data(ttl=300, show_spinner=False)
def get_customers() -> pd.DataFrame:
    try:
        df = read_sql("""
            SELECT
                c.CustomerID   AS customerid,
                c.CustomerName AS customername
            FROM Customers c
            ORDER BY c.CustomerID
        """)
        return df
    except Exception:
        # Fallback om databasen saknar kundtabell
        return pd.DataFrame(columns=["customerid", "customername"])


# Hämtar alla produktkategorier
@st.cache_data(ttl=300, show_spinner=False)
def get_categories() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            pc.CategoryID   AS categoryid,
            pc.CategoryName AS category,
            pc.Description  AS description
        FROM ProductCategories pc
        ORDER BY pc.CategoryID
    """)
    return df


# Summerar försäljning per kategori
@st.cache_data(ttl=300, show_spinner=False)
def get_sales_by_category() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            COALESCE(pc.CategoryName, CAST(p.CategoryID AS TEXT)) AS category,
            SUM(td.TotalPrice)                                    AS sales_sek,
            SUM(td.Quantity)                                      AS qty,
            COUNT(DISTINCT td.TransactionID)                      AS transactions
        FROM TransactionDetails td
        LEFT JOIN Products p           ON td.ProductID  = p.ProductID
        LEFT JOIN ProductCategories pc ON p.CategoryID  = pc.CategoryID
        GROUP BY category
        ORDER BY sales_sek DESC
    """)
    return df


# Hämtar månatlig försäljning per kategori
@st.cache_data(ttl=300, show_spinner=False)
def get_monthly_sales_by_category() -> pd.DataFrame:
    df = read_sql("""
        SELECT
            strftime('%Y-%m', t.TransactionDate) AS ym,
            COALESCE(pc.CategoryName, CAST(p.CategoryID AS TEXT)) AS category,
            SUM(td.TotalPrice)                                    AS sales_sek
        FROM TransactionDetails td
        LEFT JOIN Transactions t       ON td.TransactionID = t.TransactionID
        LEFT JOIN Products p           ON td.ProductID     = p.ProductID
        LEFT JOIN ProductCategories pc ON p.CategoryID     = pc.CategoryID
        GROUP BY ym, category
        ORDER BY ym, category
    """)
    # Konverterar år-månad till datetime
    if "ym" in df.columns:
        df["ym"] = pd.to_datetime(df["ym"], format="%Y-%m", errors="coerce")
    return df