import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="wide", page_title="Calculadora de Pagos Mixtos - Color Insumos")

# --- FUNCIONES DE BACKEND (PYTHON) ---

@st.cache_data(ttl=3600)  # Caché de 1 hora para no saturar al BCV
def obtener_tasa_bcv_scraping():
    """
    Realiza web scraping en la página principal del BCV para obtener la tasa del Dólar.
    """
    url = "https://www.bcv.org.ve/"
    try:
        response = requests.get(url, verify=False, timeout=10) # Verify=False por problemas de SSL comunes en VN
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # El BCV guarda la tasa en un div con id 'dolar' y dentro de un strong
        tasa_bcv_element = soup.find('div', id='dolar').find('strong')
        
        if tasa_bcv_element:
            tasa_texto = tasa_bcv_element.text.strip()
            # Reemplazar coma por punto para convertir a float
            tasa_limpia = tasa_texto.replace(',', '.')
            return float(tasa_limpia)
        else:
            return 46.85  # Tasa de respaldo por si falla el scraping
            
    except Exception as e:
        st.error(f"Error al obtener la tasa del BCV: {e}")
        return 46.85  # Tasa de respaldo por si falla el scraping

def generar_mensaje_cotizacion(articulo, precio_usd, tasa_bcv, tasa_paralelo, abono_usd, abono_bs):
    """
    Calcula los saldos y genera la cadena de texto final para WhatsApp.
    """
    precio_total_bs = precio_usd * tasa_bcv
    total_abonado_bs = (abono_usd * tasa_paralelo) + abono_bs
    saldo_pendiente_bs = precio_total_bs - total_abonado_bs
    saldo_pendiente_usd_paralelo = saldo_pendiente_bs / tasa_paralelo
    
    mensaje = f"""✨ *Resumen de Pago Mixto - {articulo}*
──────────────────────
💰 **Precio Total:** ${precio_usd:.2f} (Tasa BCV: {tasa_bcv:.2f})
💵 **Monto en Bs:** {precio_total_bs:.2f} Bs.
──────────────────────

📥 **Tus Abonos:**
💵 **Efectivo ($):** ${abono_usd:.2f} (Recibido a {tasa_paralelo:.2f})
📲 **Pago Móvil (Bs):** {abono_bs:.2f} Bs.
✅ **Total Abonado:** {total_abonado_bs:.2f} Bs.

──────────────────────
🛑 **SALDO PENDIENTE:**
👉 **En Bolívares:** {saldo_pendiente_bs:.2f} Bs.
👉 **En Divisas ($ Efectivo):** ${saldo_pendiente_usd_paralelo:.2f} USD
──────────────────────

🏦 **Datos Pago Móvil:**
Venezuela (0102) | 04126901346 | V-20281424

*¿Confirmamos el pago para procesar tu pedido en Color Insumos?*"""
    return mensaje

# --- FRONTEND (ESTRUCTURA VISUAL EN STREAMLIT) ---

st.title("🎨 Calculadora de Cotizaciones y Pagos Mixtos")
st.markdown("---")

# Obtener tasa BCV automáticamente
tasa_bcv_real = obtener_tasa_bcv_scraping()

# Usar columnas para organizar el formulario y el resultado
col_formulario, col_resultado = st.columns([1, 1.2], gap="large")

with col_formulario:
    st.subheader("🛠️ Panel de Entrada (Datos de Venta)")
    
    with st.expander("📝 Datos del Artículo y Tasas", expanded=True):
        articulo_input = st.text_input("Nombre del Artículo", default="DTF Textil 40cm")
        precio_usd_input = st.number_input("Precio del Artículo ($ BCV)", min_value=1.0, value=15.0, step=0.1)
        
        # Muestra la tasa BCV obtenida automáticamente, pero permite editarla
        tasa_bcv_input = st.number_input("Tasa BCV (Hoy, automática)", value=tasa_bcv_real, step=0.01)
        tasa_paralelo_input = st.number_input("Tasa Dólar Paralelo (Efectivo)", value=60.00, step=0.1)

    with st.expander("💸 Abonos del Cliente", expanded=True):
        abono_usd_input = st.number_input("¿Cuánto abonó en $ efectivo?", min_value=0.0, value=0.0, step=1.0)
        abono_bs_input = st.number_input("¿Cuánto abonó en Bs (Pago Móvil)?", min_value=0.0, value=0.0, step=10.0)

with col_resultado:
    st.subheader("📲 Vista Previa del Mensaje para el Cliente")
    
    # Generar el mensaje final
    mensaje_final = generar_mensaje_cotizacion(
        articulo_input,
        precio_usd_input,
        tasa_bcv_input,
        tasa_paralelo_input,
        abono_usd_input,
        abono_bs_input
    )
    
    # Mostrar el mensaje formateado en un área de texto para que el usuario pueda verlo y copiarlo
    st.text_area("Copia este texto y pégalo en WhatsApp/Marketplace:", mensaje_final, height=500)
    
    # Botón de copiar al portapapeles (Streamlit native o JS hack)
    # Por simplicidad, usaremos el text_area, el usuario solo tiene que Ctrl+A y Ctrl+C.
    st.success("🎉 ¡Cotización generada exitosamente! Solo cópiala del cuadro de arriba.")
    st.info("💡 Consejo: Asegúrate de que el cliente entienda que el saldo pendiente en $ está calculado a tasa Paralelo, mientras que el precio original está a tasa BCV.")

st.markdown("---")
st.caption("Prototipo Visual para Color Insumos - Desarrollado en Python/Streamlit.")