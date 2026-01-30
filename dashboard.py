# ═══════════════════════════════════════════════════════════════════
# DASHBOARD MOTODRIVE - BAJAJ
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datos import DATOS, CLIENTES
from io import BytesIO
from datetime import datetime

# Para PDF
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import tempfile
import os

# Configuración de la página
st.set_page_config(page_title="MotoDrive - Objetivos", page_icon="🏍️", layout="wide")

# Colores
ROJO = "#dc2626"
VERDE = "#22c55e"
AMARILLO = "#eab308"
NARANJA = "#f97316"
AZUL = "#3b82f6"

def color_semaforo(porcentaje):
    if porcentaje >= 100: return VERDE
    if porcentaje >= 70: return AMARILLO
    if porcentaje >= 50: return NARANJA
    return "#ef4444"

def formato_pesos(valor):
    return f"${valor:,.0f}"

# ═══════════════════════════════════════════════════════════════════
# FUNCIÓN PARA GENERAR PDF
# ═══════════════════════════════════════════════════════════════════

def generar_pdf(cliente, df_cliente, metricas):
    """Genera un PDF profesional del dashboard"""
    
    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ═══ HEADER ═══
    pdf.set_fill_color(220, 38, 38)  # Rojo
    pdf.rect(10, 10, 190, 30, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_xy(15, 15)
    pdf.cell(0, 10, 'MOTODRIVE - Dashboard de Objetivos', ln=True)
    
    pdf.set_font('Helvetica', '', 12)
    pdf.set_xy(15, 28)
    pdf.cell(0, 10, f'Cliente: {cliente} | {len(df_cliente)} sucursales | {datetime.now().strftime("%B %Y").title()}')
    
    # ═══ DESCUENTO ═══
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(160, 10, 40, 30, 'F')
    pdf.set_text_color(148, 163, 184)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_xy(160, 14)
    pdf.cell(40, 5, 'Descuento', align='C')
    
    if metricas['descuento'] == 35:
        pdf.set_text_color(34, 197, 94)  # Verde
    else:
        pdf.set_text_color(59, 130, 246)  # Azul
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_xy(160, 22)
    pdf.cell(40, 12, f"{metricas['descuento']}%", align='C')
    
    # ═══ KPIs ═══
    pdf.set_y(50)
    pdf.set_text_color(0, 0, 0)
    
    kpi_width = 45
    start_x = 12
    
    kpis = [
        ('Objetivo', formato_pesos(metricas['obj_total']), (59, 130, 246)),
        ('Resultado', formato_pesos(metricas['res_total']), (34, 197, 94) if metricas['pct_total'] >= 100 else (234, 179, 8)),
        ('Cumplimiento', f"{metricas['pct_total']:.0f}%", (34, 197, 94) if metricas['pct_total'] >= 100 else (234, 179, 8)),
        ('Pedidos', formato_pesos(metricas['pedidos']), (139, 92, 246))
    ]
    
    for i, (label, value, color) in enumerate(kpis):
        x = start_x + (i * 48)
        
        pdf.set_fill_color(241, 245, 249)
        pdf.rect(x, 50, kpi_width, 25, 'F')
        
        pdf.set_text_color(100, 116, 139)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_xy(x, 52)
        pdf.cell(kpi_width, 5, label, align='C')
        
        pdf.set_text_color(*color)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_xy(x, 60)
        pdf.cell(kpi_width, 10, value, align='C')
    
    # ═══ BARRAS DE AVANCE ═══
    pdf.set_y(85)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Avance por Categoria', ln=True)
    
    barras = [
        ('REFACCIONES', metricas['pct_refacc'], metricas['res_refacc'], metricas['obj_refacc']),
        ('BGO', metricas['pct_bgo'], metricas['res_bgo'], metricas['obj_bgo'])
    ]
    
    for nombre, pct, res, obj in barras:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 6, nombre)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(80, 6, f'{formato_pesos(res)} / {formato_pesos(obj)}')
        
        if pct >= 100:
            r, g, b = 34, 197, 94
        elif pct >= 70:
            r, g, b = 234, 179, 8
        elif pct >= 50:
            r, g, b = 249, 115, 22
        else:
            r, g, b = 239, 68, 68
        
        pdf.set_text_color(r, g, b)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(30, 6, f'{pct:.0f}%', align='R', ln=True)
        
        pdf.set_fill_color(226, 232, 240)
        pdf.rect(12, pdf.get_y(), 186, 6, 'F')
        
        pdf.set_fill_color(r, g, b)
        barra_ancho = min(pct, 100) / 100 * 186
        pdf.rect(12, pdf.get_y(), barra_ancho, 6, 'F')
        
        pdf.set_y(pdf.get_y() + 10)
    
    # ═══ GRÁFICAS CON MATPLOTLIB ═══
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Visualizaciones', ln=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Gráfica de barras
        fig1, ax1 = plt.subplots(figsize=(5, 3.5))
        categorias = ['REFACC', 'BGO']
        objetivos = [metricas['obj_refacc'], metricas['obj_bgo']]
        resultados = [metricas['res_refacc'], metricas['res_bgo']]
        
        x = range(len(categorias))
        width = 0.35
        
        bars1 = ax1.bar([i - width/2 for i in x], objetivos, width, label='Objetivo', color='#3b82f6')
        bars2 = ax1.bar([i + width/2 for i in x], resultados, width, label='Resultado', 
                        color=[color_semaforo(metricas['pct_refacc']), color_semaforo(metricas['pct_bgo'])])
        
        ax1.set_ylabel('Pesos')
        ax1.set_title('Objetivo vs Resultado')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categorias)
        ax1.legend()
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        img_barras = os.path.join(tmpdir, 'barras.png')
        fig1.savefig(img_barras, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig1)
        
        # Gráfica de dona
        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        alcanzado = metricas['res_total']
        pendiente = max(0, metricas['obj_total'] - metricas['res_total'])
        
        sizes = [alcanzado, pendiente]
        colors_pie = ['#22c55e', '#e2e8f0']
        
        wedges, texts, autotexts = ax2.pie(sizes, colors=colors_pie, autopct='%1.0f%%',
                                            startangle=90, pctdistance=0.85,
                                            wedgeprops=dict(width=0.4))
        
        ax2.text(0, 0, f'{metricas["pct_total"]:.0f}%', ha='center', va='center', fontsize=20, fontweight='bold')
        ax2.set_title('Cumplimiento Global')
        ax2.legend(['Alcanzado', 'Pendiente'], loc='lower center', bbox_to_anchor=(0.5, -0.1))
        
        plt.tight_layout()
        img_dona = os.path.join(tmpdir, 'dona.png')
        fig2.savefig(img_dona, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig2)
        
        # Insertar gráficas
        y_graficas = pdf.get_y()
        pdf.image(img_barras, x=10, y=y_graficas, w=95)
        pdf.image(img_dona, x=105, y=y_graficas, w=95)
    
    # ═══ TABLA DE SUCURSALES ═══
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Detalle por Sucursal', ln=True)
    
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)
    
    col_widths = [50, 25, 25, 22, 22, 25, 25, 16]
    headers = ['Sucursal', 'Obj Refacc', 'Res Refacc', 'Obj BGO', 'Res BGO', 'Obj Total', 'Res Total', '% Cumpl']
    
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        pdf.cell(width, 8, header, border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 7)
    
    for _, row in df_cliente.iterrows():
        pct = (row['resTotal'] / row['objTotal'] * 100) if row['objTotal'] > 0 else 0
        
        sucursal_text = str(row['sucursal'])[:28]
        pdf.cell(col_widths[0], 6, sucursal_text, border=1)
        pdf.cell(col_widths[1], 6, formato_pesos(row['objRefacc']), border=1, align='R')
        pdf.cell(col_widths[2], 6, formato_pesos(row['resRefacc']), border=1, align='R')
        pdf.cell(col_widths[3], 6, formato_pesos(row['objBgo']), border=1, align='R')
        pdf.cell(col_widths[4], 6, formato_pesos(row['resBgo']), border=1, align='R')
        pdf.cell(col_widths[5], 6, formato_pesos(row['objTotal']), border=1, align='R')
        pdf.cell(col_widths[6], 6, formato_pesos(row['resTotal']), border=1, align='R')
        pdf.cell(col_widths[7], 6, f'{pct:.0f}%', border=1, align='C')
        pdf.ln()
    
    # ═══ NOTA ═══
    pdf.set_y(-40)
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(10, pdf.get_y(), 190, 20, 'F')
    pdf.set_text_color(100, 116, 139)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_xy(15, pdf.get_y() + 5)
    pdf.multi_cell(180, 5, 'Nota: Para obtener el descuento del 35% es necesario cubrir el 100% del objetivo de cada categoria, incluyendo manejo de Excellon al 100%.')
    
    return bytes(pdf.output())

# ═══════════════════════════════════════════════════════════════════
# CARGAR DATOS
# ═══════════════════════════════════════════════════════════════════

df = pd.DataFrame(DATOS)

# ═══════════════════════════════════════════════════════════════════
# LEER CLIENTE DESDE URL O SELECTOR
# ═══════════════════════════════════════════════════════════════════

params = st.query_params
cliente_url = params.get("cliente", None)

st.sidebar.markdown("## 🏍️ MotoDrive")
st.sidebar.markdown("---")

if cliente_url and cliente_url in CLIENTES:
    cliente = cliente_url
    st.sidebar.success(f"👤 Cliente: **{cliente}**")
else:
    st.sidebar.markdown("### 🔍 Seleccionar Cliente")
    cliente = st.sidebar.selectbox("👤 Cliente:", CLIENTES)

df_cliente = df[df['clientName'] == cliente].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **{len(df_cliente)}** sucursales")

# ═══════════════════════════════════════════════════════════════════
# CALCULAR MÉTRICAS
# ═══════════════════════════════════════════════════════════════════

obj_refacc = df_cliente['objRefacc'].sum()
obj_bgo = df_cliente['objBgo'].sum()
obj_total = df_cliente['objTotal'].sum()
res_refacc = df_cliente['resRefacc'].sum()
res_bgo = df_cliente['resBgo'].sum()
res_total = df_cliente['resTotal'].sum()
pedidos = df_cliente['pedidos'].sum()

pct_refacc = (res_refacc / obj_refacc * 100) if obj_refacc > 0 else 0
pct_bgo = (res_bgo / obj_bgo * 100) if obj_bgo > 0 else 0
pct_total = (res_total / obj_total * 100) if obj_total > 0 else 0

if pct_total >= 100 and pct_refacc >= 100 and pct_bgo >= 100:
    descuento = 35
    color_desc = VERDE
else:
    descuento = 20
    color_desc = AZUL

metricas = {
    'obj_refacc': obj_refacc, 'obj_bgo': obj_bgo, 'obj_total': obj_total,
    'res_refacc': res_refacc, 'res_bgo': res_bgo, 'res_total': res_total,
    'pct_refacc': pct_refacc, 'pct_bgo': pct_bgo, 'pct_total': pct_total,
    'pedidos': pedidos, 'descuento': descuento
}

# ═══════════════════════════════════════════════════════════════════
# MOSTRAR DASHBOARD
# ═══════════════════════════════════════════════════════════════════

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {ROJO}, #991b1b); padding: 20px; border-radius: 15px;">
        <h1 style="color: white; margin: 0;">🏍️ MOTODRIVE - Dashboard de Objetivos</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Cliente: <b>{cliente}</b> | {len(df_cliente)} sucursales</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div style="background: #1e293b; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid {color_desc};">
        <p style="color: #94a3b8; margin: 0; font-size: 14px;">Descuento</p>
        <p style="color: {color_desc}; margin: 0; font-size: 48px; font-weight: 800;">{descuento}%</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🎯 Objetivo", formato_pesos(obj_total))
c2.metric("💰 Resultado", formato_pesos(res_total))
c3.metric("📊 Cumplimiento", f"{pct_total:.0f}%")
c4.metric("📦 Pedidos", formato_pesos(pedidos))

st.markdown("---")

st.markdown("### 📊 Avance por Categoría")

for nombre, pct, obj, res in [("REFACCIONES", pct_refacc, obj_refacc, res_refacc), 
                               ("BGO", pct_bgo, obj_bgo, res_bgo)]:
    color = color_semaforo(pct)
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between;">
            <span><b>{nombre}</b></span>
            <span style="color: #64748b;">{formato_pesos(res)} / {formato_pesos(obj)}</span>
            <span style="color: {color}; font-weight: 700;">{pct:.0f}%</span>
        </div>
        <div style="background: #e2e8f0; border-radius: 10px; height: 25px; overflow: hidden;">
            <div style="background: {color}; width: {min(pct, 100)}%; height: 100%; border-radius: 10px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📈 Visualizaciones")

col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_barras = go.Figure()
    fig_barras.add_trace(go.Bar(
        name='Objetivo', 
        x=['REFACC', 'BGO'], 
        y=[obj_refacc, obj_bgo], 
        marker_color=AZUL,
        text=[formato_pesos(obj_refacc), formato_pesos(obj_bgo)],
        textposition='outside'
    ))
    fig_barras.add_trace(go.Bar(
        name='Resultado', 
        x=['REFACC', 'BGO'], 
        y=[res_refacc, res_bgo], 
        marker_color=[color_semaforo(pct_refacc), color_semaforo(pct_bgo)],
        text=[formato_pesos(res_refacc), formato_pesos(res_bgo)],
        textposition='outside'
    ))
    fig_barras.update_layout(
        title="Objetivo vs Resultado",
        barmode='group',
        height=400,
        yaxis=dict(tickformat="$,.0f")
    )
    st.plotly_chart(fig_barras, use_container_width=True)

with col_g2:
    fig_dona = go.Figure(data=[go.Pie(
        labels=['Alcanzado', 'Pendiente'],
        values=[res_total, max(0, obj_total - res_total)],
        hole=0.6,
        marker_colors=[VERDE, '#e2e8f0'],
        textinfo='label+percent'
    )])
    fig_dona.update_layout(
        title="Cumplimiento Global",
        height=400,
        annotations=[dict(
            text=f"{pct_total:.0f}%",
            x=0.5, y=0.5,
            font_size=36,
            showarrow=False
        )]
    )
    st.plotly_chart(fig_dona, use_container_width=True)

st.markdown("---")

st.markdown("### 📋 Detalle por Sucursal")

df_tabla = df_cliente[['sucursal', 'objRefacc', 'resRefacc', 'objBgo', 'resBgo', 'objTotal', 'resTotal']].copy()
pct_cumpl = df_tabla.apply(lambda row: (row['resTotal'] / row['objTotal'] * 100) if row['objTotal'] > 0 else 0, axis=1)
df_tabla['% Cumpl.'] = pct_cumpl.round(0).astype(int).astype(str) + '%'

df_display = df_tabla.copy()
df_display['objRefacc'] = df_display['objRefacc'].apply(formato_pesos)
df_display['resRefacc'] = df_display['resRefacc'].apply(formato_pesos)
df_display['objBgo'] = df_display['objBgo'].apply(formato_pesos)
df_display['resBgo'] = df_display['resBgo'].apply(formato_pesos)
df_display['objTotal'] = df_display['objTotal'].apply(formato_pesos)
df_display['resTotal'] = df_display['resTotal'].apply(formato_pesos)

df_display.columns = ['Sucursal', 'Obj Refacc', 'Res Refacc', 'Obj BGO', 'Res BGO', 'Obj Total', 'Res Total', '% Cumpl.']

st.dataframe(df_display, use_container_width=True, hide_index=True)

st.markdown("---")
st.info("📌 **Nota:** Para obtener el descuento del 35% es necesario cubrir el 100% del objetivo de cada categoría, incluyendo manejo de Excellon al 100%.")

# ═══════════════════════════════════════════════════════════════════
# BOTÓN DE DESCARGA PDF
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### 📥 Descargar Reporte")

if st.button("📄 Generar PDF", type="primary"):
    with st.spinner("Generando PDF..."):
        try:
            pdf_bytes = generar_pdf(cliente, df_cliente, metricas)
            
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_bytes,
                file_name=f"Reporte_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            st.success("✅ PDF generado correctamente. Haz clic en 'Descargar PDF'")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

