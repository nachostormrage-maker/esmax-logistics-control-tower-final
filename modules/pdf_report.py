import io
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generar_pdf_bytes(df, kpis):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # ============================================================
    # ESTILOS
    # ============================================================

    title = ParagraphStyle(
        "title",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#123B5D"),
        fontSize=20,
        leading=24
    )

    subtitle = ParagraphStyle(
        "subtitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#176B9C"),
        fontSize=13,
        leading=17
    )

    section = ParagraphStyle(
        "section",
        parent=styles["Heading2"],
        alignment=TA_LEFT,
        textColor=colors.HexColor("#123B5D"),
        fontSize=15,
        leading=19
    )

    body = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        alignment=TA_LEFT,
        leading=14,
        fontSize=10
    )

    small = ParagraphStyle(
        "small",
        parent=styles["Normal"],
        alignment=TA_LEFT,
        leading=12,
        fontSize=8
    )

    content = []

    # ============================================================
    # PORTADA
    # ============================================================

    content.append(Spacer(1, 45))

    content.append(
        Paragraph(
            "CCU",
            title
        )
    )

    content.append(
        Spacer(1, 10)
    )

    content.append(
        Paragraph(
            "Cadena de Suministro Predictiva",
            subtitle
        )
    )

    content.append(
        Paragraph(
            "Informe Ejecutivo de Supply Chain",
            subtitle
        )
    )

    content.append(
        Spacer(1, 35)
    )

    portada = Table([
        [
            Paragraph(
                "<b>Empresa analizada</b><br/>"
                "Compañía Cervecerías Unidas S.A. (CCU)",
                body
            )
        ],
        [
            Paragraph(
                "<b>Proyecto</b><br/>"
                "Sistema de apoyo a decisiones para inventario "
                "y planificación de la cadena de suministro",
                body
            )
        ],
        [
            Paragraph(
                "<b>Elaborado por</b><br/>"
                "Ignacio Álvarez",
                body
            )
        ],
        [
            Paragraph(
                "<b>Asignatura</b><br/>"
                "Evaluación de Proyectos para Cadena de Suministros",
                body
            )
        ],
        [
            Paragraph(
                "<b>Fecha</b><br/>"
                "Septiembre 2026",
                body
            )
        ]
    ], colWidths=[480])

    portada.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, -1),
            colors.HexColor("#F4F8FB")
        ),
        (
            "BOX",
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor("#D5E2EC")
        ),
        (
            "INNERGRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#E5E7EB")
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            14
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            14
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            10
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            10
        )
    ]))

    content.append(portada)

    content.append(
        Spacer(1, 35)
    )

    content.append(
        Paragraph(
            "Propuesta académica basada en datos simulados.",
            small
        )
    )

    # ============================================================
    # RESUMEN EJECUTIVO
    # ============================================================

    content.append(PageBreak())

    content.append(
        Paragraph(
            "1. Resumen Ejecutivo",
            section
        )
    )

    content.append(
        Spacer(1, 8)
    )

    content.append(
        Paragraph(
            """
            La propuesta consiste en implementar una herramienta de apoyo
            a decisiones para la cadena de suministro de Compañía Cervecerías
            Unidas S.A. (CCU), orientada a mejorar la planificación de demanda,
            gestión de inventarios y decisiones de reposición.
            <br/><br/>
            El sistema integra información histórica de demanda con herramientas
            de pronóstico, indicadores logísticos y modelos simplificados de
            optimización de inventario.
            <br/><br/>
            La finalidad es pasar desde una gestión principalmente reactiva
            hacia una gestión predictiva, donde la información histórica y las
            proyecciones permitan anticipar necesidades de abastecimiento.
            """,
            body
        )
    )

    content.append(
        Spacer(1, 15)
    )

    # ============================================================
    # KPIs
    # ============================================================

    fill_rate = float(
        kpis.get("fill_rate", 0)
    )

    mae = float(
        kpis.get("mae", 0)
    )

    inventario = float(
        kpis.get("inventario_prom", 0)
    )

    cobertura = float(
        kpis.get("cobertura_dias", 0)
    )

    valor_inventario = float(
        kpis.get("valor_inventario", 0)
    )

    content.append(
        Paragraph(
            "2. Indicadores Ejecutivos",
            section
        )
    )

    content.append(
        Spacer(1, 8)
    )

    def semaforo_fill(valor):

        if valor >= 0.95:
            return "ALTO"

        elif valor >= 0.85:
            return "MEDIO"

        return "BAJO"

    tabla_kpis = Table([
        [
            "Nivel de servicio",
            "Error demanda",
            "Inventario promedio"
        ],
        [
            f"{fill_rate:.2%}\n"
            f"Nivel: {semaforo_fill(fill_rate)}",

            f"{mae:.2f}\n"
            "MAE",

            f"{inventario:,.0f}\n"
            "unidades"
        ],
        [
            "Cobertura",
            "Valor inventario",
            "Modelo"
        ],
        [
            f"{cobertura:.1f} días",

            f"${valor_inventario:,.0f}",

            "Predictivo"
        ]
    ], colWidths=[160, 160, 160])

    tabla_kpis.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#123B5D")
        ),

        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            "BACKGROUND",
            (0, 1),
            (-1, 1),
            colors.HexColor("#EFF6FB")
        ),

        (
            "BACKGROUND",
            (0, 2),
            (-1, 2),
            colors.HexColor("#123B5D")
        ),

        (
            "TEXTCOLOR",
            (0, 2),
            (-1, 2),
            colors.white
        ),

        (
            "BACKGROUND",
            (0, 3),
            (-1, 3),
            colors.HexColor("#F8FAFC")
        ),

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#D5DEE6")
        ),

        (
            "ALIGN",
            (0, 0),
            (-1, -1),
            "CENTER"
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "FONTNAME",
            (0, 0),
            (-1, -1),
            "Helvetica-Bold"
        ),

        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            9
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            9
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            9
        )
    ]))

    content.append(
        tabla_kpis
    )

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            """
            <b>Lectura gerencial:</b> los indicadores permiten observar
            simultáneamente el nivel de servicio, la variabilidad de la demanda
            y la cantidad de inventario disponible. Esto facilita identificar
            posibles desviaciones antes de que se transformen en problemas
            operacionales.
            """,
            body
        )
    )

    # ============================================================
    # MODELO PREDICTIVO
    # ============================================================

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            "3. Modelo de Cadena de Suministro Predictiva",
            section
        )
    )

    content.append(
        Spacer(1, 8)
    )

    flujo = Table([[
        "Datos\nhistóricos",
        "→",
        "Forecast\nde demanda",
        "→",
        "Inventario",
        "→",
        "Optimización",
        "→",
        "Decisión"
    ]], colWidths=[
        70, 25, 80, 25, 70, 25, 80, 25, 70
    ])

    flujo.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0, 0),
            (-1, -1),
            colors.HexColor("#EAF3F8")
        ),

        (
            "BOX",
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor("#AFC4D3")
        ),

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#D5DEE6")
        ),

        (
            "ALIGN",
            (0, 0),
            (-1, -1),
            "CENTER"
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "FONTNAME",
            (0, 0),
            (-1, -1),
            "Helvetica-Bold"
        ),

        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            8
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            8
        )
    ]))

    content.append(
        flujo
    )

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            """
            El enfoque propuesto busca utilizar información histórica de
            demanda para generar una estimación futura y posteriormente
            relacionarla con los niveles de inventario, stock de seguridad
            y punto de reorden.
            <br/><br/>
            De esta manera, el sistema no solamente muestra información,
            sino que transforma los datos en señales de apoyo para la toma
            de decisiones logísticas.
            """,
            body
        )
    )

    # ============================================================
    # DECISIÓN DE INVENTARIO
    # ============================================================

    content.append(
        PageBreak()
    )

    content.append(
        Paragraph(
            "4. Decisión de Inventario",
            section
        )
    )

    optim = {}

    try:

        from modules.inventory_optimizer import (
            optimizar_inventario
        )

        optim = optimizar_inventario(df)

    except Exception:

        optim = {}

    eoq = float(
        optim.get("eoq", 0)
    )

    reorder_point = float(
        optim.get("reorder_point", 0)
    )

    stock_seguridad = float(
        optim.get("stock_seguridad", 0)
    )

    suggested_order = int(
        optim.get("suggested_order", 0)
    )

    riesgo = optim.get(
        "riesgo",
        "NO DETERMINADO"
    )

    lead_time = float(
        optim.get("lead_time", 0)
    )

    tabla_inventario = Table([
        [
            "Indicador",
            "Resultado"
        ],
        [
            "EOQ",
            f"{eoq:,.0f} unidades"
        ],
        [
            "Punto de reorden",
            f"{reorder_point:,.0f} unidades"
        ],
        [
            "Stock de seguridad",
            f"{stock_seguridad:,.0f} unidades"
        ],
        [
            "Lead time",
            f"{lead_time:.1f} días"
        ],
        [
            "Pedido sugerido",
            f"{suggested_order:,.0f} unidades"
        ],
        [
            "Riesgo operacional",
            riesgo
        ]
    ], colWidths=[240, 240])

    tabla_inventario.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#123B5D")
        ),

        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#D5DEE6")
        ),

        (
            "BACKGROUND",
            (0, 1),
            (0, -1),
            colors.HexColor("#F4F7F9")
        ),

        (
            "FONTNAME",
            (0, 0),
            (-1, -1),
            "Helvetica-Bold"
        ),

        (
            "ALIGN",
            (0, 0),
            (-1, -1),
            "CENTER"
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            8
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            8
        )
    ]))

    content.append(
        tabla_inventario
    )

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            """
            <b>Interpretación:</b> el modelo utiliza la demanda histórica,
            su variabilidad y el tiempo de abastecimiento para estimar el
            nivel de inventario necesario y generar una señal de reposición.
            <br/><br/>
            Los resultados corresponden a una simulación académica y no
            representan parámetros reales de operación de CCU.
            """,
            body
        )
    )

    # ============================================================
    # IMPACTO EN LA CADENA
    # ============================================================

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            "5. Impacto Esperado en la Cadena de Suministro",
            section
        )
    )

    content.append(
        Paragraph(
            """
            La oportunidad de mejora identificada se concentra en la
            planificación y eficiencia de la distribución y del inventario.
            <br/><br/>
            Una herramienta predictiva podría apoyar:
            <br/>
            • Anticipación de cambios en la demanda.<br/>
            • Planificación de inventarios.<br/>
            • Definición de stocks de seguridad.<br/>
            • Identificación de necesidades de reposición.<br/>
            • Reducción de decisiones reactivas.<br/>
            • Mejor utilización de recursos logísticos.<br/>
            • Apoyo a la planificación de distribución.
            """,
            body
        )
    )

    # ============================================================
    # LIMITACIONES
    # ============================================================

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            "6. Limitaciones del Modelo",
            section
        )
    )

    content.append(
        Paragraph(
            """
            Para efectos del proyecto académico se utilizan datos simulados.
            Por lo tanto, los resultados obtenidos no deben interpretarse como
            indicadores reales de CCU.
            <br/><br/>
            La implementación empresarial requeriría datos reales de ventas,
            inventarios, SKU, centros de distribución, rutas, costos,
            tiempos de abastecimiento y restricciones operacionales.
            <br/><br/>
            Asimismo, el modelo predictivo presentado corresponde a una
            aproximación académica y podría ser reemplazado posteriormente
            por modelos de mayor complejidad.
            """,
            body
        )
    )

    # ============================================================
    # CONCLUSIÓN
    # ============================================================

    content.append(
        Spacer(1, 15)
    )

    content.append(
        Paragraph(
            "7. Conclusión Ejecutiva",
            section
        )
    )

    content.append(
        Paragraph(
            """
            El análisis realizado permite identificar una oportunidad de
            mejora relacionada con la utilización de analítica predictiva
            para apoyar la gestión de la cadena de suministro de CCU.
            <br/><br/>
            La propuesta conecta demanda, forecast, inventario y reposición
            dentro de un mismo flujo de información. De esta manera, la
            organización podría disponer de una herramienta orientada a
            transformar información operacional en señales para la toma
            de decisiones.
            <br/><br/>
            La siguiente etapa del proyecto corresponde a evaluar la
            factibilidad técnica y económica de implementar una solución
            de estas características utilizando información real.
            """,
            body
        )
    )

    # ============================================================
    # PIE FINAL
    # ============================================================

    content.append(
        Spacer(1, 25)
    )

    content.append(
        Paragraph(
            "<b>CCU — Cadena de Suministro Predictiva</b>",
            title
        )
    )

    content.append(
        Spacer(1, 8)
    )

    content.append(
        Paragraph(
            "Ignacio Álvarez · Septiembre 2026",
            small
        )
    )

    # ============================================================
    # LAYOUT
    # ============================================================

    if os.path.exists("LAYOUT.png"):

        try:

            content.append(
                Spacer(1, 10)
            )

            content.append(
                RLImage(
                    "LAYOUT.png",
                    width=400,
                    height=90
                )
            )

        except Exception:

            pass

    # ============================================================
    # GENERAR PDF
    # ============================================================

    doc.build(content)

    buffer.seek(0)

    return buffer.read()
