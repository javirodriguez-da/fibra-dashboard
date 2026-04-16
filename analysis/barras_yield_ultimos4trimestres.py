import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ====================================
# CONFIGURACIÓN
# ====================================

fibras = [
    "FUNO11.MX",
    "FMTY14.MX",   # mensual
    "FNOVA17.MX",
    "DANHOS13.MX",
    "FIBRAMQ12.MX",
    "FSHOP13.MX",
    "NEXT25.MX",
    "FINN13.MX"
]

NUM_TRIMESTRES = 4

# ====================================
# DIVIDENDOS
# ====================================

dividendos = []

for fibra in fibras:
    ticker = yf.Ticker(fibra)
    div = ticker.dividends.reset_index()

    if div.empty:
        continue

    div.columns = ["fecha", "dividendo"]
    div["fecha"] = div["fecha"].dt.tz_localize(None)
    div["FIBRA"] = fibra
    div["Periodo"] = div["fecha"].dt.to_period("Q")

    dividendos.append(div)

df_div = pd.concat(dividendos)

df_div_q = (
    df_div
    .groupby(["FIBRA", "Periodo"])["dividendo"]
    .sum()
    .reset_index()
)

# ====================================
# PRECIOS
# ====================================

precios = []

for fibra in fibras:
    ticker = yf.Ticker(fibra)
    prices = ticker.history(period="3y", auto_adjust=False)

    if prices.empty:
        continue

    prices.index = prices.index.tz_localize(None)
    prices["FIBRA"] = fibra
    prices["Periodo"] = prices.index.to_period("Q")

    precios.append(prices.reset_index())

df_prices = pd.concat(precios)

df_price_q = (
    df_prices
    .groupby(["FIBRA", "Periodo"])["Close"]
    .mean()
    .reset_index()
    .rename(columns={"Close": "precio_promedio"})
)

# ====================================
# UNIÓN Y MÉTRICAS
# ====================================

df_q = pd.merge(
    df_div_q,
    df_price_q,
    on=["FIBRA", "Periodo"],
    how="inner"
)

df_q["yield_trimestral"] = df_q["dividendo"] / df_q["precio_promedio"]

# Últimos N trimestres
ultimos_trimestres = (
    df_q["Periodo"]
    .sort_values()
    .unique()[-NUM_TRIMESTRES:]
)

df_q = df_q[df_q["Periodo"].isin(ultimos_trimestres)]
df_q["Periodo"] = df_q["Periodo"].astype(str)

# ====================================
# ORDEN Y POSICIONES
# ====================================

periodos = sorted(df_q["Periodo"].unique())
fibras_ord = sorted(df_q["FIBRA"].unique())

y_pos = np.arange(len(periodos))
bar_height = 0.8 / len(fibras_ord)

# ====================================
# GRÁFICO HORIZONTAL (X = YIELD)
# ====================================

fig, ax = plt.subplots(figsize=(14, 7))

for i, fibra in enumerate(fibras_ord):
    df_f = df_q[df_q["FIBRA"] == fibra]

    yields = [
        df_f[df_f["Periodo"] == p]["yield_trimestral"].values[0]
        if p in df_f["Periodo"].values else 0
        for p in periodos
    ]

    posiciones = y_pos + i * bar_height

    bars = ax.barh(
        posiciones,
        yields,
        height=bar_height,
        label=fibra
    )

    # -------- ETIQUETAS --------
    for bar, p in zip(bars, periodos):
        fila = df_f[df_f["Periodo"] == p]
        if fila.empty:
            continue

        yld = fila["yield_trimestral"].values[0]
        div_val = fila["dividendo"].values[0]
        price_val = fila["precio_promedio"].values[0]

        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" Y:{yld:.2%} | ${div_val:.2f} | P:${price_val:.2f}",
            va="center",
            ha="left",
            fontsize=8
        )

# ====================================
# FORMATO FINAL
# ====================================

ax.set_yticks(y_pos + bar_height * (len(fibras_ord) / 2))
ax.set_yticklabels(periodos)

ax.set_xlabel("Yield trimestral implícito")
ax.set_title(
    "Yield Trimestral Implícito por FIBRA\n"
    "Yield | Dividendo pagado | Precio promedio"
)

ax.legend(title="FIBRA", ncol=2)
plt.tight_layout()
plt.show()
