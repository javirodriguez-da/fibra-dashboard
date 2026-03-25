import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ====================================
# CONFIGURACIÓN
# ====================================

fibras = [
    "FUNO11.MX",
    "FMTY14.MX",
    "FNOVA17.MX",
    "DANHOS13.MX",
    "FIBRAMQ12.MX",
    "FSHOP13.MX",
    "NEXT25.MX",
    "FINN13.MX"
]

START_YEAR = 2023
END_YEAR = 2025

# ====================================
# PROCESO
# ====================================

resultados = []

for fibra in fibras:

    ticker = yf.Ticker(fibra)

    # -------- PRECIOS --------
    prices = ticker.history(
        start=f"{START_YEAR}-01-01",
        end=f"{END_YEAR + 1}-01-01",
        auto_adjust=False
    )

    if prices.empty:
        continue

    prices.index = prices.index.tz_localize(None)
    prices["year"] = prices.index.year

    precio_promedio_anual = prices.groupby("year")["Close"].mean()

    # -------- DIVIDENDOS --------
    dividends = ticker.dividends.reset_index()
    dividends.columns = ["fecha", "dividendo"]
    dividends["fecha"] = dividends["fecha"].dt.tz_localize(None)
    dividends["year"] = dividends["fecha"].dt.year

    dividends = dividends[
        (dividends["year"] >= START_YEAR) &
        (dividends["year"] <= END_YEAR)
    ]

    dividendo_anual = dividends.groupby("year")["dividendo"].sum()

    # -------- YIELD ANUAL --------
    data = pd.concat(
        [precio_promedio_anual, dividendo_anual],
        axis=1,
        keys=["precio_promedio", "dividendo"]
    ).dropna()

    if data.empty:
        continue

    data["yield"] = data["dividendo"] / data["precio_promedio"]

    resultados.append({
        "FIBRA": fibra,
        "Yield promedio": data["yield"].mean(),
        "Dividendo anual promedio": data["dividendo"].mean()
    })

# ====================================
# DATAFRAME FINAL
# ====================================

df = pd.DataFrame(resultados)
df = df.sort_values("Yield promedio", ascending=False).reset_index(drop=True)

# ====================================
# GRÁFICO DE BARRAS
# ====================================

plt.figure(figsize=(12, 6))
bars = plt.bar(df["FIBRA"], df["Yield promedio"])

plt.title(
    f"Ranking de FIBRAS por Dividend Yield Promedio Anual\n"
    f"Periodo {START_YEAR}–{END_YEAR}"
)
plt.ylabel("Dividend Yield Promedio Anual")
plt.xlabel("FIBRA")

# -------- ETIQUETAS --------
for bar, yield_val, div_val in zip(
    bars,
    df["Yield promedio"],
    df["Dividendo anual promedio"]
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{yield_val:.2%}\n${div_val:.2f}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()
plt.show()
