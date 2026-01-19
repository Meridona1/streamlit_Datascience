import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from getters import get_details, get_products_with_categories

# Sidhuvud
st.header("Produkter")

# Standardtema för grafer
sns.set_theme(style="whitegrid")

# Hämtar produktdetaljer och produktinformation
details_df = get_details()
products_df = get_products_with_categories()

# Stoppar om inga detaljer finns
if details_df.empty:
    st.info("Inga produktdetaljer hittades.")
    st.stop()

# Beräknar totalpris om kolumnen saknas men quantity och unitprice finns
if "totalprice" not in details_df.columns and {"quantity", "unitprice"}.issubset(details_df.columns):
    details_df["totalprice"] = details_df["quantity"] * details_df["unitprice"]

# Stoppar om totalprice fortfarande saknas
if "totalprice" not in details_df.columns:
    st.warning("Kolumnen totalprice saknas.")
    st.stop()

# Slår ihop produktdetaljer med produktnamn och kategori om möjligt
if "productid" in products_df.columns:
    merged = details_df.merge(
        products_df[["productid", "productname", "category"]],
        on="productid",
        how="left"
    )
else:
    merged = details_df.copy()

# Sektion: topp 10 produkter
st.subheader("Topp 10 produkter")

# Väljer produktnamn om det finns, annars productid
name_col = "productname" if "productname" in merged.columns else "productid"

# Summerar försäljning och tar topp 10
top10 = (
    merged.groupby(name_col)["totalprice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# Diagram för topp 10
fig1, ax1 = plt.subplots(figsize=(8, 5))
top10.iloc[::-1].plot(
    kind="barh",
    color=sns.color_palette("crest", n_colors=len(top10)),
    ax=ax1
)
ax1.set_xlabel("Total försäljning (SEK)")
ax1.set_ylabel("Produkt")
ax1.set_title("Topp 10")
st.pyplot(fig1)

# Tabell: topp 20 produkter med antal och försäljning
st.caption("Topp 20. Antal och försäljning.")
tab = (
    merged.groupby(name_col, dropna=False)
    .agg(antal=("quantity", "sum"), försäljning=("totalprice", "sum"))
    .sort_values("försäljning", ascending=False)
    .head(20)
    .reset_index()
)
st.dataframe(tab, use_container_width=True)

# Sektion: försäljning per kategori om kolumnen finns
if "category" in merged.columns:
    st.subheader("Försäljning per kategori")

    cat_sum = (
        merged.groupby("category")["totalprice"]
        .sum()
        .sort_values(ascending=False)
    )

    fig2, ax2 = plt.subplots(figsize=(9, 4))
    sns.barplot(
        x=cat_sum.index,
        y=cat_sum.values,
        ax=ax2,
        palette="crest"
    )
    ax2.set_xlabel("Kategori")
    ax2.set_ylabel("Total försäljning (SEK)")
    ax2.set_title("Kategori")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig2)