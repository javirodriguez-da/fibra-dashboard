import yfinance as yf
import pandas as pd
import os

# -------------------------
# CONFIG
# -------------------------
tickers = [
    "FMTY14.MX",
    "FUNO11.MX",
    "FIBRAMQ12.MX",
    "FCFE18.MX",
    "DANHOS13.MX",
    "FSHOP13.MX",
    "FIBRAPL14.MX",
    "FNOVA17.MX"
]

# -------------------------
# CREAR CARPETA data SI NO EXISTE
# -------------------------
os.makedirs("data", exist_ok=True)

# -------------------------
# LISTAS
# -------------------------
div_list = []
price_list = []

# -------------------------
# DESCARGA DE DATOS
# -------------------------
for ticker in tickers:
    try:
        print(f"Descargando datos de {ticker}...")

        data = yf.Ticker(ticker)

        # -------------------------
        # DIVIDENDOS
        # -------------------------
        div = data.dividends.reset_index()

        if not div.empty:
            div["ticker"] = ticker
            div_list.append(div)

        # -------------------------
        # PRECIOS
        # -------------------------
        price = data.history(period="max")[["Close"]].reset_index()

        if not price.empty:
            price["ticker"] = ticker
            price_list.append(price)

    except Exception as e:
        print(f"Error con {ticker}: {e}")

# -------------------------
# CONCATENAR DATA
# -------------------------
if div_list:
    df_div = pd.concat(div_list)
    df_div.columns = ["Fecha", "Dividendo", "ticker"]

    # limpiar fechas
    df_div["Fecha"] = pd.to_datetime(df_div["Fecha"]).dt.date

    # guardar
    df_div.to_csv("data/dividendos.csv", index=False)
    print("✅ dividendos.csv generado")
else:
    print("⚠️ No se generaron dividendos")

if price_list:
    df_price = pd.concat(price_list)
    df_price.columns = ["Fecha", "Precio", "ticker"]

    # limpiar fechas
    df_price["Fecha"] = pd.to_datetime(df_price["Fecha"]).dt.date

    # guardar
    df_price.to_csv("data/precios.csv", index=False)
    print("✅ precios.csv generado")
else:
    print("⚠️ No se generaron precios")

print("🚀 Proceso terminado")