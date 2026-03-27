import streamlit as st
import requests
from bs4 import BeautifulSoup
from st_copy_to_clipboard import st_copy_to_clipboard # Nueva librería

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="wide", page_title="Calculadora Color Insumos")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextArea textarea { font-family: monospace; color: #1e1e1e; font-size: 14px; }
    /* Estilo para que el botón de copiar resalte */
    .st-copy-to-clipboard button {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE BACKEND ---
@st.cache_data(ttl=600)
def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=3)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tasa_element = soup.find('div', id='dolar').find('strong')
            if tasa_element:
                return float(tasa_element.text.strip().replace(',', '.'))
        return 47.15
    except:
        return 47.15

def generar_mensaje(articulo, precio_usd, tasa_bcv, tasa_paralelo, abono_usd, abono_bs):
    monto_total_bs = precio_usd * tasa_bcv
    total_abonado_bs = (abono_usd * tasa_paralelo) + abono_bs
    pendiente_bs = monto_total_bs - total_abonado_bs
    tasa_p = tasa_paralelo if tasa_paralelo > 0 else 1
    pendiente_usd_p = pendiente_bs / tasa_p

    return f"""✨ *Resumen de Pago Mixto - {articulo}*
──────────────────────
💰 **Precio Total:** ${precio_usd:.2f} (Tasa BCV: {tasa_bcv:.2f})
💵 **Monto en Bs:** {monto_total_bs:.2f} Bs.
──────────────────────

📥 **Tus Abonos:**
💵 **Efectivo ($):** ${abono_usd:.2f} (Recibido a {tasa_paralelo:.2f})
📲 **Pago Móvil (Bs):** {abono_bs:.2f} Bs.
✅ **Total Abonado:** {total_abonado_bs:.2f} Bs.

──────────────────────
🛑 **SALDO PENDIENTE:**
👉 **En Bolívares:** {pendiente_bs:.2f} Bs.
👉 **En Divisas ($ Efectivo):** ${pendiente_usd_p:.2f} USD
──────────────────────

🏦 **Datos Pago Móvil:**
Venezuela (0102) | 04126901346 | V-20281424

*¿Confirmamos el pago para procesar tu pedido en Color Insumos?*"""

# --- LÓGICA DE LA APP ---
st.title("🎨 Calculadora de Pagos - Color Insumos")

tasa_auto = obtener_tasa_bcv()
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("📋 Datos de la Venta")
    articulo = st.text_input("Artículo / Servicio", value="DTF Textil 40cm")
    
    c1, c2 = st.columns(2)
    with c1:
        precio_usd = st.number_input("Precio ($ BCV)", min_value=0.0, value=15.0)
        tasa_bcv = st.number_input("Tasa BCV", value=tasa_auto)
    with c2:
        tasa_paralelo = st.number_input("Tasa Paralelo", value=60.0)
    
    st.markdown("---")
    st.subheader("💰 Abonos")
    a1, a2 = st.columns(2)
    with a1:
        abono_usd = st.number_input("Efectivo ($)", value=0.0)
    with a2:
        abono_bs = st.number_input("Pago Móvil (Bs)", value=0.0)

with col2:
    st.subheader("📝 Mensaje Final")
    resultado = generar_mensaje(articulo, precio_usd, tasa_bcv, tasa_paralelo, abono_usd, abono_bs)
    
    # Mostramos el texto formateado
    st.text_area("Vista previa:", value=resultado, height=380)
    
    # BOTÓN DE COPIADO PROFESIONAL
    st.markdown("### ↓ Haz clic abajo para copiar ↓")
    st_copy_to_clipboard(resultado, before_copy_label="📋 COPIAR MENSAJE", after_copy_label="✅ ¡COPIADO!")

st.caption("Color Insumos - San Francisco, Zulia.")