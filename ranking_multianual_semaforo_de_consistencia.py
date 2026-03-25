import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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

START_YEAR = 2023   # editable
END_YEAR = 2025     # editable

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
    precio_promedio = prices.groupby("year")["Close"].mean()

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

    # -------- YIELD --------
    data = pd.concat(
        [precio_promedio, dividendo_anual],
        axis=1,
        keys=["precio", "dividendo"]
    ).dropna()

    if data.empty or len(data) < 2:
        continue

    data["yield"] = data["dividendo"] / data["precio"]

    yield_promedio = data["yield"].mean()
    yield_std = data["yield"].std()
    coef_variacion = yield_std / yield_promedio

    # -------- SEMÁFORO (solo color) --------
    if coef_variacion <= 0.20:
        color = "green"
    elif coef_variacion <= 0.40:
        color = "gold"
    else:
        color = "red"

    resultados.append({
        "FIBRA": fibra,
        "Yield promedio": yield_promedio,
        "Dividendo anual promedio": data["dividendo"].mean(),
        "Color": color
    })

# ====================================
# DATAFRAME FINAL
# ====================================

df = pd.DataFrame(resultados)
df = df.sort_values("Yield promedio", ascending=False).reset_index(drop=True)

# ====================================
# GRÁFICO DE BARRAS
# ====================================

plt.figure(figsize=(13, 6))

bars = plt.bar(
    df["FIBRA"],
    df["Yield promedio"],
    color=df["Color"]
)

plt.title(
    f"Ranking de FIBRAS por Dividend Yield Promedio Anual\n"
    f"Periodo {START_YEAR}–{END_YEAR}"
)
plt.ylabel("Dividend Yield Promedio Anual")
plt.xlabel("FIBRA")

# -------- AJUSTE EJE Y --------
y_max = df["Yield promedio"].max() * 1.25
plt.ylim(0, y_max)

# -------- ETIQUETAS --------
for bar, row in zip(bars, df.itertuples()):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{row._2:.2%}\n${row._3:.2f}",
        ha="center",
        va="bottom",
        fontsize=9
    )

# -------- LEYENDA --------
legend_elements = [
    Patch(facecolor="green", label=" Estable (≤ 20% variación)"),
    Patch(facecolor="gold", label=" Moderado (20–40%)"),
    Patch(facecolor="red", label=" Inestable (> 40%)")
]

plt.legend(
    handles=legend_elements,
    title="Consistencia del ingreso",
    loc="upper right"
)

plt.tight_layout()
plt.show()
