# modules/forecast.py

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


def generar_forecast(df, horizonte=30):
    """
    Genera un pronóstico de demanda para la cadena de suministro.

    El modelo utiliza:
    - Tendencia histórica
    - Estacionalidad semanal
    - Promedio móvil
    - Regresión lineal

    Los datos utilizados son simulados y tienen fines académicos.
    """

    df = df.copy()

    # ============================================================
    # VALIDACIÓN
    # ============================================================

    if "demanda" not in df.columns:

        df["forecast"] = np.nan

        if "inventario" not in df.columns:
            df["inventario"] = 0

        return df

    # ============================================================
    # ORDENAR FECHAS
    # ============================================================

    if "fecha" in df.columns:

        df["fecha"] = pd.to_datetime(
            df["fecha"],
            errors="coerce"
        )

        df = (
            df.sort_values("fecha")
            .reset_index(drop=True)
        )

    # ============================================================
    # LIMPIEZA DE DEMANDA
    # ============================================================

    df["demanda"] = pd.to_numeric(
        df["demanda"],
        errors="coerce"
    )

    df["demanda"] = (
        df["demanda"]
        .interpolate()
        .fillna(
            df["demanda"].mean()
        )
    )

    # ============================================================
    # VARIABLES TEMPORALES
    # ============================================================

    df["t"] = np.arange(
        len(df)
    )

    if "fecha" in df.columns:

        df["dia_semana"] = (
            df["fecha"]
            .dt.dayofweek
        )

    else:

        df["dia_semana"] = (
            df["t"] % 7
        )

    # ============================================================
    # PROMEDIO MÓVIL
    # ============================================================

    df["media_movil_7"] = (
        df["demanda"]
        .rolling(
            window=7,
            min_periods=1
        )
        .mean()
    )

    df["media_movil_30"] = (
        df["demanda"]
        .rolling(
            window=30,
            min_periods=1
        )
        .mean()
    )

    # ============================================================
    # REGRESIÓN LINEAL
    # ============================================================

    X = df[
        [
            "t",
            "dia_semana",
            "media_movil_7"
        ]
    ]

    y = df["demanda"]

    model = LinearRegression()

    try:

        model.fit(
            X,
            y
        )

        prediccion = model.predict(
            X
        )

        df["forecast"] = prediccion

    except Exception:

        df["forecast"] = (
            df["media_movil_7"]
        )

    # ============================================================
    # CONTROL DE VALORES
    # ============================================================

    df["forecast"] = np.maximum(
        df["forecast"],
        0
    )

    # ============================================================
    # ERROR DEL MODELO
    # ============================================================

    try:

        mae = mean_absolute_error(
            df["demanda"],
            df["forecast"]
        )

    except Exception:

        mae = np.nan

    df["forecast_mae"] = mae

    # ============================================================
    # DEMANDA PROYECTADA
    # ============================================================

    ultima_demanda = (
        df["demanda"]
        .tail(7)
        .mean()
    )

    tendencia = (
        df["forecast"]
        .tail(7)
        .mean()
    )

    if not np.isfinite(tendencia):

        tendencia = ultima_demanda

    # ============================================================
    # FACTOR DE AJUSTE
    # ============================================================

    if ultima_demanda > 0:

        factor_ajuste = (
            tendencia /
            ultima_demanda
        )

    else:

        factor_ajuste = 1

    factor_ajuste = np.clip(
        factor_ajuste,
        0.85,
        1.15
    )

    # ============================================================
    # FORECAST FUTURO
    # ============================================================

    if "fecha" in df.columns:

        ultima_fecha = (
            df["fecha"]
            .max()
        )

        fechas_futuras = pd.date_range(
            start=ultima_fecha
            + pd.Timedelta(days=1),
            periods=horizonte,
            freq="D"
        )

        demanda_base = (
            df["demanda"]
            .tail(14)
            .mean()
        )

        valores_forecast = []

        for fecha in fechas_futuras:

            factor_semanal = 1.0

            # Fin de semana
            if fecha.dayofweek >= 5:
                factor_semanal = 1.08

            valor = (
                demanda_base
                * factor_ajuste
                * factor_semanal
            )

            # Pequeña tendencia temporal
            posicion = len(
                valores_forecast
            )

            valor *= (
                1
                + 0.002 * posicion
            )

            valores_forecast.append(
                max(
                    0,
                    valor
                )
            )

        forecast_futuro = pd.DataFrame({

            "fecha": fechas_futuras,

            "demanda": np.nan,

            "forecast": forecast_futuro
            if False else valores_forecast,

            "inventario": np.nan,

            "tipo": "PROYECCIÓN"

        })

    else:

        forecast_futuro = pd.DataFrame()

    # ============================================================
    # MARCAR HISTÓRICO
    # ============================================================

    df["tipo"] = "HISTÓRICO"

    # ============================================================
    # UNIR HISTÓRICO + FUTURO
    # ============================================================

    if not forecast_futuro.empty:

        columnas_base = [
            "fecha",
            "demanda",
            "forecast",
            "inventario",
            "tipo"
        ]

        historico = df[
            [
                c for c in columnas_base
                if c in df.columns
            ]
        ].copy()

        resultado = pd.concat(
            [
                historico,
                forecast_futuro
            ],
            ignore_index=True
        )

    else:

        resultado = df.copy()

    # ============================================================
    # RETORNAR RESULTADO
    # ============================================================

    return resultado
