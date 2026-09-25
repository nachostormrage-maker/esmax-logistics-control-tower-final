# modules/inventory_optimizer.py

import numpy as np
import pandas as pd


def optimizar_inventario(df=None):
    """
    Motor de optimización de inventario.

    Utiliza la demanda histórica disponible para estimar:

    - Demanda diaria
    - Demanda anualizada
    - Desviación estándar
    - Stock de seguridad
    - Punto de reorden
    - EOQ
    - Inventario actual
    - Pedido sugerido
    - Cobertura de inventario
    - Riesgo operacional

    Los datos utilizados por la plataforma son simulados
    y tienen fines académicos.
    """

    # ============================================================
    # VALORES BASE
    # ============================================================

    costo_pedir = 45000
    costo_mantener = 3300

    lead_time_default = 5
    dias_trabajo = 300

    nivel_servicio_z = 1.65

    # ============================================================
    # VALIDACIÓN
    # ============================================================

    if df is None or df.empty:

        return {
            "eoq": 0.0,
            "reorder_point": 0.0,
            "stock_seguridad": 0.0,
            "suggested_order": 0,
            "riesgo": "BAJO",
            "demanda_diaria": 0.0,
            "demanda_anual": 0.0,
            "inventario_actual": 0.0,
            "cobertura_dias": 0.0
        }

    df = df.copy()

    # ============================================================
    # DEMANDA
    # ============================================================

    if "demanda" in df.columns:

        demanda = pd.to_numeric(
            df["demanda"],
            errors="coerce"
        ).dropna()

    else:

        demanda = pd.Series(
            [0]
        )

    if demanda.empty:

        demanda = pd.Series(
            [0]
        )

    demanda_promedio = float(
        demanda.mean()
    )

    # ============================================================
    # DEMANDA DIARIA
    # ============================================================

    demanda_diaria = demanda_promedio

    # ============================================================
    # DEMANDA ANUALIZADA
    # ============================================================

    demanda_anual = (
        demanda_diaria *
        dias_trabajo
    )

    # ============================================================
    # VARIABILIDAD DE DEMANDA
    # ============================================================

    if len(demanda) > 1:

        desviacion_demanda = float(
            demanda.std()
        )

    else:

        desviacion_demanda = 0.0

    # ============================================================
    # LEAD TIME
    # ============================================================

    if "lead_time" in df.columns:

        lead_time = pd.to_numeric(
            df["lead_time"],
            errors="coerce"
        ).dropna()

        if not lead_time.empty:

            lead_time_promedio = float(
                lead_time.mean()
            )

        else:

            lead_time_promedio = (
                lead_time_default
            )

    else:

        lead_time_promedio = (
            lead_time_default
        )

    # ============================================================
    # STOCK DE SEGURIDAD
    # ============================================================

    stock_seguridad = (
        nivel_servicio_z
        * desviacion_demanda
        * np.sqrt(
            lead_time_promedio
        )
    )

    # ============================================================
    # PUNTO DE REORDEN
    # ============================================================

    reorder_point = (
        demanda_diaria
        * lead_time_promedio
        + stock_seguridad
    )

    # ============================================================
    # EOQ
    # ============================================================

    if costo_mantener > 0:

        eoq = np.sqrt(
            (
                2
                * demanda_anual
                * costo_pedir
            )
            / costo_mantener
        )

    else:

        eoq = 0.0

    # ============================================================
    # INVENTARIO ACTUAL
    # ============================================================

    if "inventario" in df.columns:

        inventario = pd.to_numeric(
            df["inventario"],
            errors="coerce"
        ).dropna()

        if not inventario.empty:

            inventario_actual = float(
                inventario.iloc[-1]
            )

        else:

            inventario_actual = 0.0

    else:

        inventario_actual = 0.0

    # ============================================================
    # COBERTURA DE INVENTARIO
    # ============================================================

    if demanda_diaria > 0:

        cobertura_dias = (
            inventario_actual /
            demanda_diaria
        )

    else:

        cobertura_dias = 0.0

    # ============================================================
    # PEDIDO SUGERIDO
    # ============================================================

    if inventario_actual < reorder_point:

        # Llevar inventario hacia EOQ
        pedido_base = (
            eoq -
            inventario_actual
        )

        # Si EOQ no es suficiente,
        # asegurar al menos el punto de reorden
        pedido_minimo = (
            reorder_point -
            inventario_actual
        )

        suggested_order = max(
            pedido_base,
            pedido_minimo,
            0
        )

    else:

        suggested_order = 0

    suggested_order = int(
        round(
            suggested_order
        )
    )

    # ============================================================
    # RIESGO OPERACIONAL
    # ============================================================

    if inventario_actual <= (
        demanda_diaria
        * lead_time_promedio
    ):

        riesgo = "ALTO"

    elif inventario_actual < reorder_point:

        riesgo = "MEDIO"

    else:

        riesgo = "BAJO"

    # ============================================================
    # RETORNO
    # ============================================================

    return {

        "eoq": float(
            eoq
        ),

        "reorder_point": float(
            reorder_point
        ),

        "stock_seguridad": float(
            stock_seguridad
        ),

        "suggested_order": int(
            suggested_order
        ),

        "riesgo": riesgo,

        "demanda_diaria": float(
            demanda_diaria
        ),

        "demanda_anual": float(
            demanda_anual
        ),

        "inventario_actual": float(
            inventario_actual
        ),

        "cobertura_dias": float(
            cobertura_dias
        ),

        "lead_time": float(
            lead_time_promedio
        ),

        "desviacion_demanda": float(
            desviacion_demanda
        )
    }
