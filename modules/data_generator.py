# modules/data_generator.py

import pandas as pd
import numpy as np


def generar_dataset_esmax(dias=180):
    """
    Generador de datos simulados para la demostración
    CCU Predictive Supply Chain.

    Los datos son ficticios y tienen fines académicos.
    No representan información operacional real de CCU.
    """

    np.random.seed(42)

    # ============================================================
    # FECHAS
    # ============================================================

    fechas = pd.date_range(
        start="2026-01-01",
        periods=dias,
        freq="D"
    )

    # ============================================================
    # CATÁLOGO SIMULADO DE CCU
    # ============================================================

    productos = [
        "Cerveza",
        "Bebida Gaseosa",
        "Agua",
        "Bebida Energética",
        "Bebida Isotónica",
        "Néctar",
        "Vino"
    ]

    centros = [
        "CD Santiago",
        "CD Valparaíso",
        "CD Concepción",
        "CD Temuco"
    ]

    # ============================================================
    # GENERACIÓN DE PRODUCTOS
    # ============================================================

    sku = np.random.choice(
        productos,
        size=dias,
        p=[
            0.25,  # Cerveza
            0.20,  # Gaseosa
            0.15,  # Agua
            0.12,  # Energética
            0.10,  # Isotónica
            0.08,  # Néctar
            0.10   # Vino
        ]
    )

    centro_distribucion = np.random.choice(
        centros,
        size=dias
    )

    # ============================================================
    # ESTACIONALIDAD
    # ============================================================

    dia = np.arange(dias)

    estacionalidad = (
        1
        + 0.12 * np.sin(2 * np.pi * dia / 30)
        + 0.08 * np.sin(2 * np.pi * dia / 7)
    )

    # Aumento progresivo de demanda
    tendencia = 1 + (dia / dias) * 0.08

    # ============================================================
    # DEMANDA
    # ============================================================

    demanda_base = np.random.normal(
        1000,
        180,
        dias
    )

    demanda = (
        demanda_base
        * estacionalidad
        * tendencia
    )

    demanda = np.clip(
        demanda.astype(int),
        300,
        None
    )

    # ============================================================
    # VENTAS
    # ============================================================

    # Simulación de cumplimiento de demanda.
    # Algunos días existe una pequeña pérdida por
    # restricciones de inventario o disponibilidad.

    nivel_servicio = np.random.normal(
        0.95,
        0.025,
        dias
    )

    nivel_servicio = np.clip(
        nivel_servicio,
        0.85,
        1.00
    )

    ventas = (
        demanda * nivel_servicio
    ).astype(int)

    # ============================================================
    # INVENTARIO
    # ============================================================

    inventario = np.zeros(dias)

    inventario[0] = np.random.randint(
        5000,
        9000
    )

    for i in range(1, dias):

        entradas = np.random.randint(
            700,
            1800
        )

        inventario[i] = (
            inventario[i - 1]
            + entradas
            - ventas[i - 1]
        )

        # Evitar inventarios negativos
        inventario[i] = max(
            inventario[i],
            np.random.randint(2500, 4500)
        )

    inventario = inventario.astype(int)

    # ============================================================
    # LEAD TIME
    # ============================================================

    lead_time = np.random.randint(
        1,
        6,
        dias
    )

    # ============================================================
    # COSTO UNITARIO SIMULADO
    # ============================================================

    costo_unitario = np.random.randint(
        500,
        2500,
        dias
    )

    # ============================================================
    # CAPACIDAD DE TRANSPORTE
    # ============================================================

    capacidad_transporte = np.random.randint(
        80,
        121,
        dias
    )

    # ============================================================
    # DISTANCIA DE DISTRIBUCIÓN
    # ============================================================

    distancia_km = np.random.randint(
        30,
        500,
        dias
    )

    # ============================================================
    # COSTO DE TRANSPORTE
    # ============================================================

    costo_transporte = (
        distancia_km
        * np.random.uniform(
            2.5,
            4.5,
            dias
        )
    )

    costo_transporte = (
        costo_transporte.round(0)
        .astype(int)
    )

    # ============================================================
    # NIVEL DE SERVICIO
    # ============================================================

    fill_rate = ventas / demanda

    # ============================================================
    # STOCK DE SEGURIDAD
    # ============================================================

    stock_seguridad = (
        demanda
        * 0.20
    ).astype(int)

    # ============================================================
    # PUNTO DE REORDEN
    # ============================================================

    reorder_point = (
        demanda * lead_time
        + stock_seguridad
    )

    reorder_point = (
        reorder_point
        .astype(int)
    )

    # ============================================================
    # UTILIZACIÓN DE TRANSPORTE
    # ============================================================

    utilizacion_transporte = np.clip(
        np.random.normal(
            88,
            8,
            dias
        ),
        60,
        110
    )

    # ============================================================
    # QUIEBRE DE STOCK
    # ============================================================

    riesgo_quiebre = np.where(
        inventario < reorder_point,
        "ALTO",
        np.where(
            inventario < reorder_point * 1.25,
            "MEDIO",
            "BAJO"
        )
    )

    # ============================================================
    # DATAFRAME
    # ============================================================

    df = pd.DataFrame({

        "fecha": fechas,

        "sku": sku,

        "centro_distribucion": centro_distribucion,

        "demanda": demanda,

        "ventas": ventas,

        "inventario": inventario,

        "lead_time": lead_time,

        "costo_unitario": costo_unitario,

        "capacidad_transporte": capacidad_transporte,

        "distancia_km": distancia_km,

        "costo_transporte": costo_transporte,

        "fill_rate": fill_rate,

        "stock_seguridad": stock_seguridad,

        "reorder_point": reorder_point,

        "utilizacion_transporte": utilizacion_transporte,

        "riesgo_quiebre": riesgo_quiebre
    })

    # ============================================================
    # VALIDACIÓN
    # ============================================================

    lengths = {
        col: df[col].shape[0]
        for col in df.columns
    }

    if len(set(lengths.values())) != 1:

        raise ValueError(
            f"Inconsistent column lengths detected: {lengths}"
        )

    return df
