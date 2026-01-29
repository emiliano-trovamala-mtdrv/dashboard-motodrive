# ═══════════════════════════════════════════════════════════════════
# DASHBOARD MOTODRIVE - BAJAJ
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
    """Convierte un número a formato de pesos mexicanos"""
    return f"${valor:,.0f}"

# ═══════════════════════════════════════════════════════════════════
# CARGAR DATOS
# ═══════════════════════════════════════════════════════════════════

st.sidebar.markdown("## 🏍️ MotoDrive")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Cargar Datos")

archivo = st.sidebar.file_uploader("Sube tu archivo Excel:", type=['xlsx'])

if archivo is not None:
    # Cargar el Excel
    df = pd.read_excel(archivo, sheet_name='Avance semanal', header=2)
    df.columns = ['COL0', 'COL1', 'COL2', 'CLIENT_NUM', 'clientName', 'sucursal', 
                  'asesor', 'zona', 'ESTATUS', 'objRefacc', 'objBgo', 'objAcc', 
                  'objTotal', 'resRefacc', 'pctRefacc', 'resBgo', 'pctBgo', 
                  'resAcc', 'pctAcc', 'resTotal', 'pctTotal', 'pedidos']
    
    df = df[df['CLIENT_NUM'].notna() & df['CLIENT_NUM'].astype(str).str.startswith('C')].copy()
    
    # Convertir a números
    for col in ['objRefacc', 'objBgo', 'objTotal', 'resRefacc', 'resBgo', 'resTotal', 'pedidos', 'zona']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    st.sidebar.success(f"✅ {len(df)} sucursales cargadas")
    
    # Selector de cliente
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtros")
    clientes = sorted(df['clientName'].unique())
    cliente = st.sidebar.selectbox("👤 Cliente:", clientes)
    
    # Filtrar por cliente
    df_cliente = df[df['clientName'] == cliente].copy()
    
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
    
    # Descuento
    if pct_total >= 100 and pct_refacc >= 100 and pct_bgo >= 100:
        descuento = 35
        color_desc = VERDE
    else:
        descuento = 20
        color_desc = AZUL
    
    # ═══════════════════════════════════════════════════════════════════
    # MOSTRAR DASHBOARD
    # ═══════════════════════════════════════════════════════════════════
    
    # Header
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
    
    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎯 Objetivo", formato_pesos(obj_total))
    c2.metric("💰 Resultado", formato_pesos(res_total))
    c3.metric("📊 Cumplimiento", f"{pct_total:.0f}%")
    c4.metric("📦 Pedidos", formato_pesos(pedidos))
    
    st.markdown("---")
    
    # Barras de progreso
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
    
    # Gráficas
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
            textinfo='label+percent',
            hovertemplate='%{label}: ' + formato_pesos(res_total) + '<extra></extra>'
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
    
    # Tabla de detalle
    st.markdown("### 📋 Detalle por Sucursal")
    
    df_tabla = df_cliente[['sucursal', 'objRefacc', 'resRefacc', 'objBgo', 'resBgo', 'objTotal', 'resTotal']].copy()
    df_tabla['% Cumpl.'] = (df_tabla['resTotal'] / df_tabla['objTotal'] * 100).fillna(0).round(0).astype(int).astype(str) + '%'
    
    # Formatear columnas como pesos
    df_tabla['objRefacc'] = df_tabla['objRefacc'].apply(formato_pesos)
    df_tabla['resRefacc'] = df_tabla['resRefacc'].apply(formato_pesos)
    df_tabla['objBgo'] = df_tabla['objBgo'].apply(formato_pesos)
    df_tabla['resBgo'] = df_tabla['resBgo'].apply(formato_pesos)
    df_tabla['objTotal'] = df_tabla['objTotal'].apply(formato_pesos)
    df_tabla['resTotal'] = df_tabla['resTotal'].apply(formato_pesos)
    
    df_tabla.columns = ['Sucursal', 'Obj Refacc', 'Res Refacc', 'Obj BGO', 'Res BGO', 'Obj Total', 'Res Total', '% Cumpl.']
    
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)
    
    # Nota
    st.markdown("---")
    st.info("📌 **Nota:** Para obtener el descuento del 35% es necesario cubrir el 100% del objetivo de cada categoría.")

else:
    # Pantalla de bienvenida
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>🏍️ Dashboard MotoDrive</h1>
        <p style="font-size: 18px; color: #64748b;">Sube tu archivo Excel en la barra lateral para comenzar</p>
        <p style="font-size: 14px; color: #94a3b8;">👈 Usa el botón "Browse files" a la izquierda</p>
    </div>
    """, unsafe_allow_html=True)