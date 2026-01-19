import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from getters import get_transactions, get_customers, get_stores

# Sidhuvud
st.header("Transaktioner")

# Standardtema för grafer
sns.set_theme(style="whitegrid")

# Hämtar data från databasen
tx = get_transactions()
cust = get_customers()
stores = get_stores()

# Säkerställer att transaktioner finns och att datumkolumnen är korrekt
if tx.empty or "date" not in tx.columns:
    st.info("Inga transaktioner eller saknad datumkolumn.")
    st.stop()

# Konverterar datum och filtrerar bort ogiltiga värden
tx["date"] = pd.to_datetime(tx["date"], errors="coerce")
tx = tx.dropna(subset=["date"]).copy()

# Skapar år-månad-kolumn för filtrering
tx["year_month"] = tx["date"].dt.to_period("M").dt.to_timestamp()

# Lista över tillgängliga månader
months = sorted(tx["year_month"].dropna().unique())
if not months:
    st.info("Inga datumvärden kunde tolkas.")
    st.stop()

# Månadsväljare
val_month = st.selectbox(
    "Välj månad.",
    options=months,
    index=len(months) - 1,
    format_func=lambda d: d.strftime("%Y-%m")
)

# Filtrerar transaktioner för vald månad
cur = tx[tx["year_month"] == val_month].copy()
if cur.empty:
    st.info("Inga transaktioner för vald månad.")
    st.stop()

# Nyckeltal: antal transaktioner, total försäljning, snittkorg
tot_trans = int(cur["transactionid"].nunique()) if "transactionid" in cur.columns else len(cur)
tot_sek = float(cur["totalamount"].sum()) if "totalamount" in cur.columns else float("nan")
aov = (tot_sek / tot_trans) if (tot_trans and pd.notna(tot_sek)) else float("nan")

# Visar nyckeltal i tre kolumner
c1, c2, c3 = st.columns(3)
c1.metric("Antal transaktioner", f"{tot_trans:,}".replace(",", " "))
c2.metric("Total försäljning (SEK)", f"{tot_sek:,.0f}".replace(",", " ") if pd.notna(tot_sek) else "–")
c3.metric("Snittkorg (SEK)", f"{aov:,.0f}".replace(",", " ") if pd.notna(aov) else "–")

# Sektion: toppkunder eller toppbutiker
st.subheader("Flest transaktioner denna månad")

plotted = False

# Försök att visa toppkunder om kunddata finns
if not cust.empty and "customerid" in cur.columns and "transactionid" in cur.columns:
    cur_c = cur.merge(cust, on="customerid", how="left")
    if "customername" in cur_c.columns:
        top_c = (
            cur_c.groupby("customername", dropna=False)["transactionid"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
            .iloc[::-1]
        )
        if not top_c.empty:
            fig_c, ax_c = plt.subplots(figsize=(8, 4))
            top_c.plot(kind="barh", color=sns.color_palette("flare", n_colors=len(top_c)), ax=ax_c)
            ax_c.set_title(f"Kund. {val_month.strftime('%Y-%m')}")
            ax_c.set_xlabel("Antal transaktioner")
            ax_c.set_ylabel("Kund")
            st.pyplot(fig_c)
            plotted = True

# Om inga kunder plottades, visa toppbutiker istället
if not plotted and "transactionid" in cur.columns:
    cur_s = cur.copy()
    name_col = None

    # Försök använda butiksnamn om det finns
    if not stores.empty and "storeid" in cur_s.columns:
        cur_s = cur_s.merge(stores, on="storeid", how="left")
        name_col = "storename" if "storename" in cur_s.columns else None

    # Fallback: använd storeid
    if name_col is None:
        name_col = "storeid" if "storeid" in cur_s.columns else None

    if name_col:
        top_s = (
            cur_s.groupby(name_col, dropna=False)["transactionid"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
            .iloc[::-1]
        )
        if not top_s.empty:
            fig_s, ax_s = plt.subplots(figsize=(8, 4))
            top_s.plot(kind="barh", color=sns.color_palette("flare", n_colors=len(top_s)), ax=ax_s)
            ax_s.set_title(f"Butik. {val_month.strftime('%Y-%m')}")
            ax_s.set_xlabel("Antal transaktioner")
            ax_s.set_ylabel("Butik" if name_col == "storename" else "Store ID")
            st.pyplot(fig_s)

# Daglig försäljning som linjediagram
if "totalamount" in cur.columns:
    ts = cur.groupby(pd.Grouper(key="date", freq="D"))["totalamount"].sum().reset_index()
    fig_t, ax_t = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=ts, x="date", y="totalamount", ax=ax_t, marker="o", color="#2E86C1")
    ax_t.set_title(f"Försäljning per dag. {val_month.strftime('%Y-%m')}")
    ax_t.set_xlabel("Datum")
    ax_t.set_ylabel("SEK")
    st.pyplot(fig_t)

# Exempelrader från månadens transaktioner
st.subheader("Exempelrader")

if not stores.empty and "storeid" in cur.columns:
    v = cur.merge(stores, on="storeid", how="left")
    ordered = [
        c for c in ["date", "transactionid", "customerid", "storeid", "storename", "county", "totalamount"]
        if c in v.columns
    ]
    st.dataframe(v[ordered].head(200), use_container_width=True)
else:
    show_cols = [c for c in ["date", "transactionid", "customerid", "storeid", "totalamount"] if c in cur.columns]
    st.dataframe(cur[show_cols].head(200), use_container_width=True)