import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from getters import get_transactions, get_stores

# Sidhuvud
st.header("Butiker")

# Standardtema för grafer
sns.set_theme(style="whitegrid")

# Hämtar transaktioner och butiksdata
tx = get_transactions()
stores = get_stores()

# Säkerställer att det finns transaktioner att analysera
if tx.empty:
    st.info("Inga transaktioner hittades.")
    st.stop()

# Slår ihop transaktioner med butiksinformation om möjligt
if "storeid" in tx.columns and not stores.empty:
    df = pd.merge(tx, stores, on="storeid", how="left")
else:
    df = tx.copy()

# Identifierar kolumner för butiksnamn och försäljningsbelopp
name_col = "storename" if "storename" in df.columns else ("storeid" if "storeid" in df.columns else None)
amt_col = "totalamount" if "totalamount" in df.columns else None

# Stoppar om viktiga kolumner saknas
if not (name_col and amt_col):
    st.warning("Nödvändiga kolumner saknas.")
    st.stop()

# Valfri filtrering på län om kolumnen finns
if "county" in df.columns and df["county"].notna().any():
    valda = st.multiselect("Län. Valfritt.", options=sorted(df["county"].dropna().unique()))
    if valda:
        df = df[df["county"].isin(valda)]

# Summerar försäljning per butik
store_sum = (
    df.groupby(name_col, dropna=False)[amt_col]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Stapeldiagram över försäljning per butik
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=store_sum, x=name_col, y=amt_col, ax=ax, palette="crest")
ax.set_xlabel("Butik" if name_col == "storename" else "Store ID")
ax.set_ylabel("Total försäljning (SEK)")
ax.set_title("Försäljning per butik")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig)

# Tabell med försäljning per butik och län (om data finns)
if "county" in df.columns and name_col == "storename":
    tab = (
        df.groupby(["storename", "county"], dropna=False)[amt_col]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.dataframe(tab, use_container_width=True)