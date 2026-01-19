* Individuell inlämning – Data Science-projekt (TUC Yrkeshögskola) *

Min Streamlit-app är publicerad här:  https://meridona.streamlit.app/transactions
                                                                       

Detta projekt är en Streamlit-applikation som jag har byggt för att analysera försäljningsdata på ett tydligt och användarvänligt sätt.
Appen visar försäljning per produkt, butik, kategori och tid, och gör det enkelt att se mönster och trender i datan.

Projektet består av flera sidor:
Transaktioner – månadsvy, nyckeltal, toppkunder och toppbutiker.
Butiker – försäljning per butik och möjlighet att filtrera på län.
Produkter – toppsäljare, antal och försäljning per kategori.
Insikter – månadstrender, veckodagar och värmekarta för butik × månad.

All data hämtas från en SQLite-databas via egna getter-funktioner. Caching används för att göra appen snabb och responsiv. Visualiseringarna är byggda med pandas, seaborn och matplotlib.

