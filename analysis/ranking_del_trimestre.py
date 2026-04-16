import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CONFIGURACIÓN
# =========================

FIBRAS = [
    "FUNO11.MX",
    "FMTY14.MX",
    "FNOVA17.MX",
    "DANHOS13.MX",
    "FIBRAMQ12.MX",
    "FSHOP13.MX",
    "NEXT25.MX",
    "FINN13.MX"
]

YEARS_HISTORY = 3

resultados = []

# =========================
# PROCESO
# =========================

for ticker in FIBRAS:

    fib = yf.Ticker(ticker)

    dividends = fib.dividends
    prices = fib.history(period="4y")["Close"]

    if dividends.empty or prices.empty:
        print(ticker, "sin datos")
        continue

    # ========================
    # DIVIDENDOS
    # ========================

    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]

    df_div["fecha"] = pd.to_datetime(df_div["fecha"]).dt.tz_localize(None)

    df_div["quarter"] = df_div["fecha"].dt.to_period("Q")

    dividends_q = df_div.groupby("quarter")["dividendo"].sum()

    # ========================
    # PRECIOS
    # ========================

    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    # ========================
    # UNIÓN
    # ========================

    df = pd.DataFrame({
        "dividendo": dividends_q,
        "precio": prices_q
    }).dropna()

    print(ticker, "trimestres:", len(df))

    if len(df) < 6:
        print(ticker, "no tiene suficiente historial")
        continue

    # ========================
    # ÚLTIMO TRIMESTRE
    # ========================

    last_quarter = df.index.max()

    actual = df.loc[last_quarter]

    promedio_hist = df.iloc[-(YEARS_HISTORY*4):-1]["dividendo"].mean()

    yield_trim = actual["dividendo"] / actual["precio"]

    diferencia = (actual["dividendo"] - promedio_hist) / promedio_hist

    resultados.append({
        "fibra": ticker.replace(".MX",""),
        "trimestre": str(last_quarter),
        "dividendo": actual["dividendo"],
        "precio": actual["precio"],
        "yield": yield_trim,
        "promedio_3y": promedio_hist,
        "vs_promedio": diferencia
    })

# ========================
# VALIDACIÓN
# ========================

if len(resultados) == 0:
    print("No se encontraron datos de FIBRAs")
    exit()

# ========================
# DATAFRAME
# ========================

df_rank = pd.DataFrame(resultados)

df_rank = df_rank.sort_values("dividendo", ascending=True)

# export CSV
df_rank.to_csv("ranking_fibras_trimestre.csv", index=False)

print("\nRanking generado:\n")
print(df_rank)

# ========================
# VISUAL
# ========================

plt.figure(figsize=(12,7))

bars = plt.barh(
    df_rank["fibra"],
    df_rank["dividendo"]
)

# espacio extra eje X
max_div = df_rank["dividendo"].max()
plt.xlim(0, max_div * 1.40)

# =========================
# ETIQUETAS ALINEADAS
# =========================

for y, (_, row) in enumerate(df_rank.iterrows()):

    etiqueta = (
        f"${row['dividendo']:.2f} MXN dividendo\n"
        f"Yield: {row['yield']:.2%} "
        f"(precio prom trimestre: ${row['precio']:.2f})\n"
        f"{row['vs_promedio']:+.0%} vs promedio 3y"
    )

    plt.text(
        row["dividendo"] + max_div * 0.02,
        y,
        etiqueta,
        va="center",
        fontsize=10
    )

# =========================
# TÍTULO
# =========================

plt.title(
    f"Ranking FIBRAs — Dividendos del último trimestre disponible ({df_rank['trimestre'].iloc[0]})",
    fontsize=14,
    pad=15
)

plt.xlabel("Dividendo por certificado (MXN)")
plt.ylabel("FIBRA")

plt.grid(axis="x", alpha=0.3)

# =========================
# NOTA EXPLICATIVA
# =========================

plt.figtext(
    0.01,
    -0.02,
    "Yield calculado como dividendo trimestral dividido entre el precio promedio del trimestre. "
    "Comparación contra el promedio trimestral de dividendos de los últimos 3 años. "
    "Fuente: Yahoo Finance",
    fontsize=9
)

plt.tight_layout()

# =========================
# EXPORTAR IMAGEN
# =========================

plt.savefig(
    "ranking_fibras_trimestre.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nArchivos generados:")
print("ranking_fibras_trimestre.png")
print("ranking_fibras_trimestre.csv")