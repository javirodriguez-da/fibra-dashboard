import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

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
        "precio_prom": prices_q
    }).dropna()

    print(ticker, "trimestres:", len(df))

    if len(df) < 6:
        print(ticker, "no tiene suficiente historial")
        continue

    actual = df.iloc[-1]

    promedio_hist = df.iloc[-(YEARS_HISTORY*4):-1]["dividendo"].mean()

    yield_trimestre = actual["dividendo"] / actual["precio_prom"]

    resultados.append({
        "fibra": ticker.replace(".MX",""),
        "dividendo": actual["dividendo"],
        "yield": yield_trimestre,
        "precio": actual["precio_prom"],
        "promedio_hist": promedio_hist
    })

# ========================
# VALIDACIÓN
# ========================

if len(resultados) == 0:
    print("No se encontraron datos de FIBRAs")
    exit()

df_rank = pd.DataFrame(resultados).sort_values("dividendo", ascending=False)

print(df_rank)

# ========================
# GRÁFICA
# ========================

plt.figure(figsize=(11,6))

plt.bar(df_rank["fibra"], df_rank["dividendo"])

plt.ylim(0, df_rank["dividendo"].max()*1.35)

for i,row in df_rank.iterrows():

    etiqueta = (
        f"${row['dividendo']:.2f} | "
        f"{row['yield']:.2%} yield | "
        f"Prom 3y: ${row['promedio_hist']:.2f}"
    )

    plt.text(
        df_rank.index.get_loc(i),
        row["dividendo"]*1.05,
        etiqueta,
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

plt.title(
    "Ranking FIBRAs — Dividendos del trimestre actual\n"
    "Comparación contra promedio trimestral últimos 3 años"
)

plt.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.show()