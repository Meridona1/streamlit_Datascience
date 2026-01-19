import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from getters import (
    get_details,
    get_products_with_categories,
    get_transactions,
    get_stores
)

# Standardtema för grafer
sns.set_theme(style="whitegrid")

# Sidhuvud
st.header("Insikter")

# Hämtar all nödvändig data
details_df = get_details()
products_df = get_products_with_categories()
tx_df = get_transactions()
stores_df = get_stores()

# Stoppar om inga transaktioner finns
if tx_df.empty:
    st.info("Inga transaktioner hittades.")
    st.stop()

# Säkerställer att datum är i rätt format
if "date" in tx_df.columns:
    tx_df["date"] = pd.to_datetime(tx_df["date"], errors="coerce")
    tx_df = tx_df.dropna(subset=["date"]).copy()

# Formatterare för SEK med mellanslag
sek_fmt = FuncFormatter(lambda x, p: f"{int(x):,}".replace(",", " "))

# ---------------------------------------------------------
# 1. Försäljning per kategori
# ---------------------------------------------------------

st.subheader("Försäljning per kategori")

# Kontrollerar att kategoridata går att beräkna
kan_göra_kategori = (
    not details_df.empty
    and "productid" in details_df.columns
    and {"productid", "category"}.issubset(products_df.columns)
)

if kan_göra_kategori:
    # Slår ihop detaljer med kategorier
    d = details_df.merge(
        products_df[["productid", "category"]],
        on="productid",
        how="left"
    )

    # Beräknar totalpris om det saknas
    if "totalprice" not in d.columns and {"quantity", "unitprice"}.issubset(d.columns):
        d["totalprice"] = d["quantity"] * d["unitprice"]

    # Summerar försäljning per kategori
    if "totalprice" in d.columns and "category" in d.columns:
        cat_sum = (
            d.groupby("category", dropna=False)["totalprice"]
             .sum()
             .sort_values(ascending=False)
        )

        if not cat_sum.empty:
            fig1, ax1 = plt.subplots(figsize=(9, 4))
            sns.barplot(x=cat_sum.index, y=cat_sum.values, ax=ax1, palette="crest")
            ax1.set_xlabel("Kategori")
            ax1.set_ylabel("Total försäljning (SEK)")
            ax1.yaxis.set_major_formatter(sek_fmt)
            ax1.set_title("Försäljning per kategori")
            plt.xticks(rotation=30, ha="right")
            st.pyplot(fig1)
        else:
            st.info("Det finns inga värden att summera per kategori.")
    else:
        st.info("Nödvändiga kolumner för kategorisummering saknas.")
else:
    st.info("Produktkategorier kan inte beräknas eftersom produkt- eller detaljdata saknas.")

# ---------------------------------------------------------
# 2. Försäljning per månad
# ---------------------------------------------------------

st.subheader("Försäljning per månad")

if "date" in tx_df.columns and "totalamount" in tx_df.columns:
    month_sum = (
        tx_df.assign(month=lambda d: d["date"].dt.to_period("M").dt.to_timestamp())
             .groupby("month")["totalamount"]
             .sum()
             .reset_index()
    )

    if not month_sum.empty:
        fig2, ax2 = plt.subplots(figsize=(9, 4))
        sns.lineplot(data=month_sum, x="month", y="totalamount", marker="o", ax=ax2, color="#2E86C1")
        ax2.set_xlabel("Månad")
        ax2.set_ylabel("Total försäljning (SEK)")
        ax2.yaxis.set_major_formatter(sek_fmt)
        ax2.set_title("Försäljning per månad")
        st.pyplot(fig2)
    else:
        st.info("Det finns inga månadsvärden att visa.")
else:
    st.info("Kolumner för datum eller belopp saknas för månadsgrafen.")

# ---------------------------------------------------------
# 3. Försäljning per veckodag
# ---------------------------------------------------------

st.subheader("Försäljning per veckodag")

if "date" in tx_df.columns and "totalamount" in tx_df.columns:
    wd_df = tx_df.copy()
    wd_df["_dow"] = wd_df["date"].dt.dayofweek

    ordning = [0, 1, 2, 3, 4, 5, 6]
    etiketter = ["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]

    wd_sum = (
        wd_df.groupby("_dow")["totalamount"]
             .sum()
             .reindex(ordning, fill_value=0)
    )

    fig3, ax3 = plt.subplots(figsize=(9, 4))
    wd_sum.index = etiketter
    sns.barplot(x=wd_sum.index, y=wd_sum.values, ax=ax3, palette="flare")
    ax3.set_xlabel("Veckodag")
    ax3.set_ylabel("Total försäljning (SEK)")
    ax3.yaxis.set_major_formatter(sek_fmt)
    ax3.set_title("Försäljning per veckodag")
    st.pyplot(fig3)
else:
    st.info("Kolumner för datum eller belopp saknas för veckodagsgrafen.")

# ---------------------------------------------------------
# 4. Värmekarta: Butik × månad
# ---------------------------------------------------------

st.subheader("Butik × månad")

# Låter användaren styra hur många månader som visas
months_to_show = st.sidebar.slider(
    "Antal månader i värmekartan.",
    min_value=3,
    max_value=24,
    value=12,
    step=1
)

# Väljer butiksnamn om det finns, annars storeid
store_col = None
if "storename" in tx_df.columns:
    store_col = "storename"
elif "storeid" in tx_df.columns:
    store_col = "storeid"

# Hämtar butiksnamn om bara ID finns
stores_df = get_stores()
if store_col == "storeid" and not stores_df.empty and "storeid" in stores_df.columns:
    tx_df = tx_df.merge(stores_df[["storeid", "storename"]], on="storeid", how="left")
    store_col = "storename" if "storename" in tx_df.columns else "storeid"

if store_col and "date" in tx_df.columns and "totalamount" in tx_df.columns:
    # Skapar YYYY-MM som text för stabila kolumnetiketter
    tx_df["_ym"] = tx_df["date"].dt.to_period("M").astype(str)

    month_order = sorted(tx_df["_ym"].unique())
    if month_order:
        last_n = month_order[-months_to_show:]
        tx_cut = tx_df[tx_df["_ym"].isin(last_n)].copy()
    else:
        tx_cut = tx_df.copy()

    # Summerar försäljning per butik och månad
    grid = (
        tx_cut
        .groupby([store_col, "_ym"])["totalamount"]
        .sum()
        .reset_index()
    )

    if not grid.empty:
        # Pivot: butiker i rader, månader i kolumner
        heat = (
            grid.pivot(index=store_col, columns="_ym", values="totalamount")
            .reindex(columns=last_n)
            .fillna(0)
        )

        # Dynamisk figurstorlek beroende på antal butiker och månader
        cell_h = 0.45
        base_h = 1.5
        height = max(3, base_h + cell_h * len(heat.index))
        width = max(6, 0.6 * len(heat.columns))

        fig4, ax4 = plt.subplots(figsize=(width, height))
        sns.heatmap(
            heat,
            cmap="Blues",
            ax=ax4,
            cbar_kws={"label": "SEK"},
            linewidths=0.25,
            linecolor="#ffffff"
        )

        ax4.set_xlabel("Månad")
        ax4.set_ylabel("Butik" if store_col == "storename" else "Store ID")
        ax4.set_title("Försäljning per butik och månad")
        ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha="right")

        st.pyplot(fig4)
    else:
        st.info("Det finns inga värden att visa i värmekartan.")
else:
    st.info("Nödvändiga kolumner saknas för värmekartan.")