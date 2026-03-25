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
    "FUNO11.MX",
    ##"FMTY14.MX",
    ##"FNOVA17.MX",
    ##"DANHOS13.MX",
    ##"FIBRAMQ12.MX",
    ##"FSHOP13.MX",
    ##"NEXT25.MX",
    ##"FINN13.MX"
]

START_YEAR = 2023
END_YEAR = datetime.today().year - 1  # descarta año actual incompleto

inflacion_anual = {
    2020: 0.036,
    2021: 0.072,
    2022: 0.079,
    2023: 0.047,
    2024: 0.045,
    2025: 0.040
}

# ====================================
# PROCESO POR FIBRA
# ====================================

for fibra in fibras:
    ticker = yf.Ticker(fibra)
    dividends = ticker.dividends

    if dividends.empty:
        print(f"\n⚠️ Sin dividendos para {fibra}")
        continue

    df = dividends.reset_index()
    df.columns = ["fecha", "dividendo"]
    df["fecha"] = df["fecha"].dt.tz_localize(None)
    df["año"] = df["fecha"].dt.year

    df = df[df["año"] <= END_YEAR]

    # ====================================
    # DIVIDENDO ANUAL
    # ====================================

    total_anual = df.groupby("año")["dividendo"].sum()
    crecimiento = total_anual.pct_change()

    total_anual_plot = total_anual[total_anual.index >= START_YEAR]
    crecimiento_plot = crecimiento[crecimiento.index >= START_YEAR]

    resultados = []

    for año in total_anual_plot.index:
        if año not in inflacion_anual:
            continue
        if pd.isna(crecimiento.loc[año]):
            continue

        resultados.append({
            "año": año,
            "dividendo": total_anual.loc[año],
            "crecimiento": crecimiento.loc[año],
            "inflacion": inflacion_anual[año],
            "gana": crecimiento.loc[año] > inflacion_anual[año]
        })

    if not resultados:
        continue

    df_result = pd.DataFrame(resultados)

    # ====================================
    # TRENDLINE
    # ====================================

    X = np.arange(len(total_anual_plot))
    y = total_anual_plot.values
    coef = np.polyfit(X, y, 1)
    trend = np.poly1d(coef)(X)

    # ====================================
    # SUBTÍTULO: CRECIMIENTO ACUMULADO VS INFLACIÓN
    # ====================================

    año_inicio = total_anual_plot.index.min()
    año_fin = total_anual_plot.index.max()

    crecimiento_acumulado = (
        total_anual_plot.loc[año_fin] /
        total_anual_plot.loc[año_inicio] - 1
    )

    inflacion_acumulada = 1
    for a in range(año_inicio, año_fin + 1):
        if a in inflacion_anual:
            inflacion_acumulada *= (1 + inflacion_anual[a])
    inflacion_acumulada -= 1

    if crecimiento_acumulado > inflacion_acumulada:
        conclusion = "El dividendo creció MÁS que la inflación en el periodo"
        color_sub = "green"
    else:
        conclusion = "El dividendo creció MENOS que la inflación en el periodo"
        color_sub = "red"

    subtitulo = (
        f"{conclusion}\n"
        f"Crec. Dividendo: {crecimiento_acumulado:.1%} | "
        f"Inflación acumulada: {inflacion_acumulada:.1%}"
    )

    # ====================================
    # GRÁFICA
    # ====================================

    plt.figure(figsize=(11, 6))

    max_y = total_anual_plot.max()
    plt.ylim(0, max_y * 1.35)

    for _, row in df_result.iterrows():
        color = "green" if row["gana"] else "red"

        plt.scatter(
            row["año"],
            row["dividendo"],
            color=color,
            s=80,
            zorder=3
        )

        etiqueta = (
            f"Div: ${row['dividendo']:.2f}\n"
            f"Δ vs ant: {row['crecimiento']:.1%}\n"
            f"Inflación: {row['inflacion']:.1%}"
        )

        plt.annotate(
            etiqueta,
            (row["año"], row["dividendo"]),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontsize=8,
            weight="bold"
        )

    plt.plot(
        total_anual_plot.index,
        total_anual_plot.values,
        alpha=0.5,
        label="Dividendo anual"
    )

    plt.plot(
        total_anual_plot.index,
        trend,
        linestyle="--",
        color="orange",
        label="Tendencia"
    )

    # ====================================
    # TÍTULO Y SUBTÍTULO
    # ====================================

    años_gana = df_result[df_result["gana"]]["año"].tolist()
    años_texto = ", ".join(str(a) for a in años_gana) if años_gana else "Ninguno"

    plt.title(
        f"{fibra}\n"
        f"Años donde el dividendo creció más que la inflación: {años_texto}",
        fontsize=12
    )

    plt.suptitle(
        subtitulo,
        fontsize=10,
        y=0.93,
        color=color_sub
    )

    plt.xlabel("Año")
    plt.ylabel("MXN por certificado")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    # 🔢 Forzar años enteros
    plt.xticks(
        total_anual_plot.index,
        [str(año) for año in total_anual_plot.index]
    )

    plt.tight_layout()
    plt.show()
