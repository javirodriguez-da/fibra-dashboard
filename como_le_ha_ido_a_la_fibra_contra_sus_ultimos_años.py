import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# ====================================
# CONFIGURACIÓN
# ====================================

fibras = [
    ##"FUNO11.MX",
    ##"FMTY14.MX",
    ##"FNOVA17.MX",
    ##"DANHOS13.MX",
    ##"FIBRAMQ12.MX",
    "FSHOP13.MX",
    ##"NEXT25.MX",
    ##"FINN13.MX"
]

START_YEAR = 2023
END_YEAR = datetime.today().year - 1

# ====================================
# PROCESO POR FIBRA
# ====================================

for ticker_symbol in fibras:

    ticker = yf.Ticker(ticker_symbol)

    # --------------------------------
    # PRECIOS HISTÓRICOS
    # --------------------------------

    prices = ticker.history(
        start=f"{START_YEAR}-01-01",
        end=f"{END_YEAR + 1}-01-01",
        auto_adjust=False
    )

    if prices.empty:
        print(f"⚠️ Sin precios para {ticker_symbol}")
        continue

    prices.index = prices.index.tz_localize(None)
    prices["año"] = prices.index.year

    # --------------------------------
    # DIVIDENDOS
    # --------------------------------

    dividends = ticker.dividends.reset_index()
    dividends.columns = ["fecha", "dividendo"]
    dividends["fecha"] = dividends["fecha"].dt.tz_localize(None)
    dividends["año"] = dividends["fecha"].dt.year

    if dividends.empty:
        print(f"⚠️ Sin dividendos para {ticker_symbol}")
        continue

    # --------------------------------
    # MÉTRICAS ANUALES
    # --------------------------------

    precio_anual = prices.groupby("año").agg(
        precio_promedio=("Close", "mean"),
        precio_min=("Low", "min"),
        precio_max=("High", "max")
    )

    dividendo_anual = dividends.groupby("año")["dividendo"].sum()

    df = precio_anual.join(dividendo_anual)
    df = df[(df.index >= START_YEAR) & (df.index <= END_YEAR)]
    df = df.dropna()

    if df.empty:
        print(f"⚠️ Datos insuficientes para {ticker_symbol}")
        continue

    df["dividend_yield"] = df["dividendo"] / df["precio_promedio"]

    # ====================================
    # GRÁFICA
    # ====================================

    años = df.index.values
    x = np.arange(len(años))
    width = 0.35

    plt.figure(figsize=(13, 7))

    # Barras
    bars_precio = plt.bar(
        x - width / 2,
        df["precio_promedio"],
        width,
        label="Precio promedio anual",
        alpha=0.7
    )

    bars_div = plt.bar(
        x + width / 2,
        df["dividendo"],
        width,
        label="Dividendo anual",
        alpha=0.7
    )

    # Líneas min–max
    for i, año in enumerate(años):
        ymin = df.loc[año, "precio_min"]
        ymax = df.loc[año, "precio_max"]

        plt.vlines(
            x[i] - width / 2,
            ymin,
            ymax,
            color="gray",
            linewidth=1
        )

        # Etiqueta mínimo
        plt.annotate(
            f"${ymin:.2f}",
            (x[i] - width / 2, ymin),
            textcoords="offset points",
            xytext=(0, -12),
            ha="center",
            fontsize=8
        )

        # Etiqueta máximo
        plt.annotate(
            f"${ymax:.2f}",
            (x[i] - width / 2, ymax),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontsize=8
        )

    # Etiqueta precio promedio
    for bar in bars_precio:
        height = bar.get_height()
        plt.annotate(
            f"${height:.2f}",
            (bar.get_x() + bar.get_width() / 2, height),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontsize=9,
            weight="bold"
        )

    # Etiqueta dividendo + yield
    for i, bar in enumerate(bars_div):
        div = df.iloc[i]["dividendo"]
        yld = df.iloc[i]["dividend_yield"]

        plt.annotate(
            f"${div:.2f}\n({yld:.1%})",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontsize=9,
            weight="bold"
        )

    # ====================================
    # ESTÉTICA
    # ====================================

    plt.title(
        f"{ticker_symbol}\n"
        "Dividendo anual vs Precio promedio (mín–máx) y rendimiento por dividendo"
    )

    plt.xlabel("Año")
    plt.ylabel("MXN")
    plt.xticks(x, [str(a) for a in años])
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
