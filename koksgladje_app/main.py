
import streamlit as st
import seaborn as sns


sns.set_theme(style="whitegrid")

st.set_page_config(
    page_title="Köksglädje – Dataanalys",
    page_icon="🍳",
    layout="wide"
)


st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #fde2e4 0%, #fad2e1 45%, #f8cdd3 100%);
        border: 1px solid #f7bfc8;
        border-radius: 14px;
        padding: 22px 20px;
    ">
        <h1 style="margin: 0; color: #1f2937; font-weight: 800; font-size: 32px;">
            Köksglädje – Dataanalys
        </h1>
        <p style="margin: 8px 0 0; color: #374151; font-size: 16px;">
            Den här applikationen är utvecklad för att ge företaget en tydlig och lättillgänglig överblick över sin försäljning.
            Syftet är att visualisera vad som säljer, vad som inte gör det och vilka mönster som påverkar resultatet.
            Allt är byggt från grunden för att göra analysen möjlig även för användare utan teknisk bakgrund.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
   
st.markdown("")

# Lägger en tydlig snabbnavigering.
# Syftet är att minska klick och göra det lätt att hitta rätt analys direkt.
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    st.page_link("pages/products.py", label="🍽️ Produkter")
with nav2:
    st.page_link("pages/stores.py", label="🏬 Butiker")
with nav3:
    st.page_link("pages/transactions.py", label="📅 Transaktioner")
with nav4:
    try:
        st.page_link("pages/kategorier.py", label="🏷️ Kategorier")
    except Exception:
        pass

st.markdown("")

# Visar status över datakällor i en expander.
# Syftet är att snabbt verifiera att tabellerna laddas och att datamängden är rimlig inför granskning.
from getters import get_details, get_products_with_categories, get_transactions, get_stores
with st.expander("Datastatus"):
    try:
        details_df = get_details()
        products_df = get_products_with_categories()
        transactions_df = get_transactions()
        stores_df = get_stores()
        st.write(f"TransactionDetails. Rader: {len(details_df):,}".replace(",", " "))
        st.write(f"Produkter. Rader: {len(products_df):,}".replace(",", " "))
        st.write(f"Transaktioner. Rader: {len(transactions_df):,}".replace(",", " "))
        st.write(f"Butiker. Rader: {len(stores_df):,}".replace(",", " "))
        
    except Exception as e:
        st.error(f"Kunde inte läsa datan. {e}")


