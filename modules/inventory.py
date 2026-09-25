# modules/inventory.py

import numpy as np
import pandas as pd


def calcular_kpis(df):
    """
    Calcula KPIs de la cadena de suministro.

    Los datos utilizados por la plataforma son simulados
    y tienen fines académicos.
    """

    res = {
        "fill_rate": 0.0,
        "mae": 0.0,
        "desviacion_demanda": 0.0,
        "inventario_prom": 0.0,
        "inventario_total": 0.0,
        "cobertura_dias": 0.0,
        "valor_inventario": 0.0,
        "riesgo_quiebre": 0.0,
        "nivel_servicio": 0.0
    }

    # ============================================================
    # VALIDACIÓN
    # ============================================================

    if df is None or df.empty:
        return res

    df = df.copy()

    # ============================================================
    # DEMANDA Y VENTAS
    # ============================================================

    if "demanda" in df.columns:

        demanda = pd.to_numeric(
            df["demanda"],
            errors="coerce"
        ).fillna(0)

    else:

        demanda = pd.Series(
            np.zeros(len(df))
        )

    if "ventas" in df.columns:

        ventas = pd.to_numeric(
            df["ventas"],
            errors="coerce"
        ).fillna(0)

    else:

        ventas = pd.Series(
            np.zeros(len(df))
        )

    # ============================================================
    # FILL RATE
    # ============================================================

    mask = demanda > 0

    if mask.any():

        fill_rate = (
            ventas[mask] /
            demanda[mask]
        ).mean()

        fill_rate = float(
            np.clip(
                fill_rate,
                0,
                1
            )
        )

    else:

        fill_rate = 0.0

    res["fill_rate"] = fill_rate

    # ============================================================
    # ERROR DE DEMANDA
    # ============================================================

    error = (
        demanda -
        ventas
    ).abs().mean()

    res["mae"] = float(error)

    res["desviacion_demanda"] = float(
        error
    )

    # ============================================================
    # INVENTARIO
    # ============================================================

    if "inventario" in df.columns:

        inventario = pd.to_numeric(
            df["inventario"],
            errors="coerce"
        ).fillna(0)

        res["inventario_prom"] = float(
            inventario.mean()
        )

        res["inventario_total"] = float(
            inventario.sum()
        )

    else:

        inventario = pd.Series(
            np.zeros(len(df))
        )

    # ============================================================
    # COBERTURA DE INVENTARIO
    # ============================================================

    demanda_promedio = float(
        demanda.mean()
    )

    inventario_promedio = float(
        inventario.mean()
    )

    if demanda_promedio > 0:

        cobertura = (
            inventario_promedio /
            demanda_promedio
        )

    else:

        cobertura = 0.0

    res["cobertura_dias"] = float(
        cobertura
    )

    # ============================================================
    # VALOR DEL INVENTARIO
    # ============================================================

    if "costo_unitario" in df.columns:

        costo = pd.to_numeric(
            df["costo_unitario"],
            errors="coerce"
        ).fillna(0)

        valor_inventario = (
            inventario *
            costo
        ).mean()

        res["valor_inventario"] = float(
            valor_inventario
        )

    # ============================================================
    # RIESGO DE QUIEBRE
    # ============================================================

    if "reorder_point" in df.columns:

        reorder_point = pd.to_numeric(
            df["reorder_point"],
            errors="coerce"
        ).fillna(0)

        quiebre = (
            inventario <
            reorder_point
        )

        if len(quiebre) > 0:

            riesgo = (
                quiebre.mean()
            )

        else:

            riesgo = 0.0

    else:

        riesgo = 0.0

    res["riesgo_quiebre"] = float(
        riesgo
    )

    # ============================================================
    # NIVEL DE SERVICIO
    # ============================================================

    res["nivel_servicio"] = (
        res["fill_rate"]
    )

    return res


# ================================================================
# CLASIFICACIÓN ABC
# ================================================================

def clasificacion_abc(df):
    """
    Clasificación ABC de productos según participación
    acumulada de la demanda.

    A = aproximadamente 80% del valor acumulado
    B = siguiente 15%
    C = resto
    """

    if df is None or df.empty:
        return pd.DataFrame()

    if "sku" not in df.columns:
        return pd.DataFrame()

    if "demanda" not in df.columns:
        return pd.DataFrame()

    # ============================================================
    # AGRUPAR DEMANDA POR PRODUCTO
    # ============================================================

    abc = (
        df.groupby("sku", as_index=False)
        ["demanda"]
        .sum()
    )

    abc = abc.sort_values(
        "demanda",
        ascending=False
    ).reset_index(
        drop=True
    )

    total = abc["demanda"].sum()

    if total <= 0:

        abc["participacion"] = 0.0
        abc["acumulado"] = 0.0
        abc["clasificacion"] = "C"

        return abc

    # ============================================================
    # PARTICIPACIÓN
    # ============================================================

    abc["participacion"] = (
        abc["demanda"] /
        total
    )

    abc["acumulado"] = (
        abc["participacion"]
        .cumsum()
    )

    # ============================================================
    # CLASIFICACIÓN
    # ============================================================

    def asignar_clase(valor):

        if valor <= 0.80:
            return "A"

        elif valor <= 0.95:
            return "B"

        else:
            return "C"

    abc["clasificacion"] = (
        abc["acumulado"]
        .apply(asignar_clase)
    )

    # ============================================================
    # FORMATO
    # ============================================================

    abc["participacion"] = (
        abc["participacion"]
        .round(4)
    )

    abc["acumulado"] = (
        abc["acumulado"]
        .round(4)
    )

    return abc
