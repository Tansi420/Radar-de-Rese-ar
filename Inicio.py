"""
📡 Radar de Reseñas — Qué dicen realmente tus clientes
Aplicación Streamlit: convierte reseñas y comentarios en un mapa visual de palabras

Instalación:
    pip install streamlit wordcloud matplotlib pandas Pillow numpy

Ejecución:
    streamlit run wordcloud_app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import io
from collections import Counter
from wordcloud import WordCloud, STOPWORDS

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Radar de Reseñas",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS — crema cálido, verde petróleo y coral
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general crema */
    .stApp {
        background-color: #fbf7f0;
    }

    /* Sidebar verde petróleo */
    [data-testid="stSidebar"] {
        background-color: #12343b !important;
        border-right: 4px solid #e4572e;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f4a259 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #e8efe9 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] p {
        color: #cfdcd6 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.14) !important;
        margin: 16px 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] div {
        color: #e8efe9 !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary * {
        color: #f4a259 !important;
    }

    /* Inputs */
    textarea, input[type="text"] {
        background-color: #fffdf9 !important;
        border: 1px solid #e3d6c0 !important;
        border-radius: 12px !important;
        color: #1d2b2f !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
    }
    textarea:focus, input[type="text"]:focus {
        border-color: #e4572e !important;
        box-shadow: 0 0 0 3px rgba(228,87,46,0.20) !important;
    }

    /* Selectbox */
    [data-baseweb="select"] > div {
        background: #fffdf9 !important;
        border: 1px solid #e3d6c0 !important;
        border-radius: 12px !important;
        font-size: 0.9rem !important;
    }
    [data-baseweb="select"] * {
        color: #1d2b2f !important;
    }

    /* Títulos */
    h1 {
        font-family: 'Inter', sans-serif !important;
        color: #12343b !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    h2, h3 {
        font-family: 'Inter', sans-serif !important;
        color: #12343b !important;
        font-weight: 600 !important;
    }
    p, li {
        color: #3b4a4e !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
    }

    /* Botón principal — coral */
    .stButton > button {
        background: #e4572e !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.6px !important;
        padding: 0.6rem 1.4rem !important;
        width: 100% !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease !important;
    }
    .stButton > button:hover {
        background: #c9441f !important;
        box-shadow: 0 6px 18px rgba(228,87,46,0.35) !important;
        transform: translateY(-1px);
    }

    /* Botón descarga — verde petróleo */
    [data-testid="stDownloadButton"] button {
        background: #12343b !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: background 0.2s !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #2a9d8f !important;
    }

    /* Métricas */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #eadfce;
        border-bottom: 4px solid #2a9d8f;
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 4px 14px rgba(18,52,59,0.07);
    }
    [data-testid="metric-container"] label {
        color: #7a8a8d !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e4572e !important;
        font-weight: 700 !important;
        font-size: 1.55rem !important;
    }

    /* Header */
    .header-card {
        background: linear-gradient(120deg, #12343b 0%, #1d5560 100%);
        border-radius: 20px;
        padding: 30px 38px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(18,52,59,0.22);
        border-bottom: 5px solid #e4572e;
    }

    /* Sección card */
    .section-card {
        background: #ffffff;
        border: 1px solid #eadfce;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(18,52,59,0.06);
    }

    /* Barras de frecuencia */
    .freq-row {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 7px 14px;
        margin: 4px 0;
        background: #fffdf9;
        border: 1px solid #f1e8d8;
        border-radius: 12px;
        transition: background 0.15s;
    }
    .freq-row:hover { background: #fdf0dc; }

    .freq-bar {
        height: 10px;
        background: linear-gradient(90deg, #e4572e, #f4a259);
        border-radius: 999px;
        display: inline-block;
        vertical-align: middle;
    }

    /* Tag de ranking */
    .rank-tag {
        background: #12343b;
        border-radius: 999px;
        padding: 1px 9px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #f4a259;
        font-family: 'IBM Plex Mono', monospace;
        min-width: 36px;
        text-align: center;
    }

    /* Welcome items */
    .info-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 16px;
        background: #fffdf9;
        border: 1px solid #eadfce;
        border-left: 4px solid #2a9d8f;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* Uso cards */
    .uso-tag {
        display: inline-block;
        background: #fdf0dc;
        border: 1px solid #f4d9b0;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #7a3b14;
        margin: 4px 3px;
    }

    /* Expander */
    div[data-testid="stExpander"] {
        border: 1px solid #eadfce !important;
        border-radius: 12px !important;
        background: #ffffff !important;
    }

    hr { border-color: #eadfce !important; }

    /* Nube container */
    .wc-container {
        background: #ffffff;
        border: 1px solid #eadfce;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 14px rgba(18,52,59,0.07);
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STOPWORDS
# ─────────────────────────────────────────────
STOPWORDS_ES = {
    "de","la","el","en","y","a","los","del","se","las","un","por","con","no","una","su",
    "para","es","al","lo","como","mas","pero","sus","le","ya","o","este","si","porque",
    "esta","entre","cuando","muy","sin","sobre","tambien","me","hasta","hay","donde",
    "quien","desde","nos","durante","ni","contra","ese","eso","ante","bajo","tras",
    "que","fue","son","han","ha","ser","era","estan","siendo","sido","he","has","hemos",
    "habian","tiene","tienen","hacer","puede","pueden","asi","tan","parte","todo","todos",
    "todas","cada","otro","otra","otros","otras","mismo","misma","nuestro","nuestra",
    "ellos","ellas","nosotros","les","esa","esos","esas","aquel","aquella","aquellos",
}

def obtener_stopwords(idioma):
    sw = set(STOPWORDS)
    if idioma in ("Español", "Ambos"):
        sw |= STOPWORDS_ES
    return sw


# ─────────────────────────────────────────────
# PALETAS
# ─────────────────────────────────────────────
PALETAS = {
    "Atardecer":        ["#7f1d1d","#b91c1c","#e4572e","#f08a4b","#f5a65b","#d97706","#92400e"],
    "Océano":           ["#0b3c49","#12606f","#1a8a96","#2a9d8f","#4fb6b0","#7fcdc7","#0f2942"],
    "Bosque":           ["#064e3b","#065f46","#047857","#059669","#10b981","#34d399","#6ee7b7"],
    "Uva":              ["#3b0764","#581c87","#6b21a8","#7e22ce","#9333ea","#a855f7","#c084fc"],
    "Café de origen":   ["#3e2723","#4e342e","#5d4037","#6d4c41","#8d6e63","#a1887f","#bcaaa4"],
    "Coral y marino":   ["#12343b","#e4572e","#2a9d8f","#f4a259","#5b8e7d","#bc4b51","#8b5e3c"],
    "Tinta":            ["#0b132b","#1c2541","#3a506b","#5bc0be","#6fffe9","#3a506b","#1c2541"],
}

FORMAS = {
    "Rectángulo": None,
    "Círculo":    "circle",
}

def crear_mascara(forma, size=500):
    if forma == "circle":
        y, x = np.ogrid[:size, :size]
        cx, cy = size // 2, size // 2
        mascara = np.ones((size, size), dtype=np.uint8) * 255
        mascara[(x - cx)**2 + (y - cy)**2 <= (size // 2 - 12)**2] = 0
        return mascara
    return None


# ─────────────────────────────────────────────
# FUNCIONES CORE
# ─────────────────────────────────────────────
def limpiar_texto(texto, stopwords, min_longitud):
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+", "", texto)
    texto = re.sub(r"[^a-záéíóúüñàâèêîôùûäëïöü\s]", " ", texto, flags=re.UNICODE)
    palabras = [p for p in texto.split() if p not in stopwords and len(p) >= min_longitud]
    return " ".join(palabras)


def contar_palabras(texto_limpio):
    return pd.DataFrame(Counter(texto_limpio.split()).most_common(50),
                        columns=["Palabra", "Frecuencia"])


def generar_wordcloud(texto_limpio, paleta_nombre, max_words, fondo, forma, ancho=1000, alto=520):
    import random
    colores = PALETAS[paleta_nombre]

    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        rng = random_state or random.Random()
        return colores[rng.randint(0, len(colores) - 1)]

    mascara = crear_mascara(forma, size=min(ancho, alto))
    wc = WordCloud(
        width=ancho, height=alto, max_words=max_words,
        background_color=fondo, color_func=color_func,
        mask=mascara, collocations=False,
        min_font_size=11, max_font_size=120,
        prefer_horizontal=0.75, relative_scaling=0.5, margin=5,
    ).generate(texto_limpio)

    fig, ax = plt.subplots(figsize=(ancho / 100, alto / 100))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_facecolor(fondo)
    plt.tight_layout(pad=0)
    return fig


def fig_a_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📡 Radar de Reseñas")
    st.divider()

    # ── Fuente ──
    st.markdown("### FUENTE DE COMENTARIOS")
    fuente = st.radio("fuente", ["✍️ Escribir / Pegar", "📂 Subir archivo"],
                      label_visibility="collapsed")
    texto_input = ""

    if fuente == "✍️ Escribir / Pegar":
        texto_input = st.text_area(
            "Texto:", height=190,
            placeholder="Pega aquí reseñas de Google Maps, TripAdvisor, encuestas de satisfacción, comentarios de redes...")

        with st.expander("Cargar reseñas de ejemplo"):
            ejemplos = {
                "Restaurante": """
                La comida estuvo deliciosa y el servicio fue excelente. El mesero fue muy amable
                y atento, aunque la espera por la mesa fue larga. Los platos llegaron calientes y
                con una presentación hermosa. El ambiente es acogedor y tranquilo, ideal para
                una cena en pareja. Los precios son justos para la calidad de la comida. La
                carne estaba en su punto y el postre fue increíble. Volveremos pronto, recomendado
                por el sabor y la atención. Lo único malo fue el ruido de la música.
                """,
                "Hotel boutique": """
                La habitación estaba limpia, cómoda y con una vista espectacular. El personal de
                recepción fue amable y siempre dispuesto a ayudar. El desayuno es variado y
                abundante, con frutas frescas y café delicioso. La ubicación es perfecta, cerca de
                restaurantes y del centro histórico. El wifi es lento y el aire acondicionado hacía
                ruido por la noche. La piscina es hermosa y tranquila. Excelente experiencia,
                limpieza impecable y una atención muy cálida durante toda la estancia.
                """,
                "Tienda en línea": """
                El pedido llegó rápido y bien empacado. El producto es de buena calidad y tal como
                se ve en las fotos. La atención al cliente respondió pronto y resolvió mi duda sin
                problemas. El envío tardó un poco más de lo prometido pero la entrega fue segura.
                El precio es competitivo y la talla fue la correcta. Recomiendo la tienda por la
                confianza y la rapidez. El proceso de pago fue sencillo, aunque la página es lenta
                y la devolución parece complicada.
                """,
            }
            ejemplo_sel = st.selectbox("Ejemplo:", list(ejemplos.keys()),
                                       label_visibility="collapsed")
            if st.button("Cargar texto seleccionado"):
                st.session_state["texto_ejemplo"] = ejemplos[ejemplo_sel]
                st.rerun()

        if "texto_ejemplo" in st.session_state and not texto_input:
            texto_input = st.session_state["texto_ejemplo"]

    else:
        archivo = st.file_uploader("Archivo:", type=["txt", "csv"],
                                   label_visibility="collapsed")
        if archivo:
            if archivo.name.endswith(".txt"):
                texto_input = archivo.read().decode("utf-8", errors="ignore")
            elif archivo.name.endswith(".csv"):
                df_csv = pd.read_csv(archivo)
                col_txt = st.selectbox("Columna de reseñas:", df_csv.columns.tolist())
                texto_input = " ".join(df_csv[col_txt].dropna().astype(str).tolist())
            st.success(f"Archivo cargado — {len(texto_input):,} caracteres")

    st.divider()

    # ── Procesamiento ──
    st.markdown("### FILTROS")
    idioma         = st.selectbox("Stopwords:", ["Español", "Inglés", "Ambos", "Ninguno"])
    min_longitud   = st.slider("Longitud mínima de palabra", 2, 8, 3)
    palabras_extra = st.text_input("Excluir palabras adicionales:",
                                   placeholder="ej: restaurante, lugar, sitio")

    st.divider()

    # ── Apariencia ──
    st.markdown("### ESTILO DEL RADAR")
    paleta_sel  = st.selectbox("Paleta:", list(PALETAS.keys()))
    fondo_sel   = st.radio("Fondo:", ["Blanco", "Negro"], horizontal=True)
    fondo_color = "white" if fondo_sel == "Blanco" else "black"
    forma_sel   = st.selectbox("Forma:", list(FORMAS.keys()))
    max_words   = st.slider("Máximo de palabras:", 20, 200, 80)

    st.divider()
    generar = st.button("ESCANEAR RESEÑAS  ↗", use_container_width=True)


# ─────────────────────────────────────────────
# CONTENIDO PRINCIPAL
# ─────────────────────────────────────────────

# Header
st.markdown("""
<div class="header-card">
    <h1 style="margin:0; font-size:1.9rem; color:#ffffff !important;">📡 Radar de Reseñas</h1>
    <p style="margin:6px 0 0 0; color:#cfe3de !important; font-size:0.97rem;">
        Descubre qué elogian y de qué se quejan tus clientes: de cientos de comentarios a un mapa visual en segundos
    </p>
</div>
""", unsafe_allow_html=True)

# ── Pantalla de bienvenida ──
if not generar or not texto_input.strip():
    col_izq, col_der = st.columns([3, 2], gap="large")

    with col_izq:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### ¿Cómo funciona el radar?")
        st.markdown("""
        Leer cientos de reseñas una por una es imposible. El **Radar de Reseñas** las junta todas
        y hace crecer las palabras que más repiten tus clientes: si "lento" aparece enorme,
        ya sabes dónde está el problema; si lo hace "delicioso", sabes qué te hace especial.
        """)

        for icono, titulo, desc in [
            ("📊", "Termómetro de opiniones", "Identifica los temas que más mencionan tus clientes, para bien o para mal."),
            ("🔍", "Limpieza de ruido", "Elimina palabras vacías (*stopwords*) en español e inglés para quedarte con lo importante."),
            ("🎨", "Radar a tu estilo", "Elige paleta, forma y cantidad de palabras para tu informe o presentación."),
            ("⬇️", "Listo para compartir", "Descarga la imagen en alta resolución y la tabla de frecuencias en CSV."),
        ]:
            st.markdown(
                f'<div class="info-item">'
                f'<span style="font-size:1.3rem; flex-shrink:0;">{icono}</span>'
                f'<div><strong style="color:#12343b;">{titulo}</strong>'
                f'<p style="margin:2px 0 0 0; color:#7a8a8d !important; font-size:0.88rem;">{desc}</p></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("#### Instrucciones")
        for i, paso in enumerate([
            "Pega tus reseñas o sube un archivo con los comentarios en el panel lateral.",
            "Ajusta los filtros: idioma de *stopwords*, palabras a excluir y estilo del radar.",
            "Haz clic en **ESCANEAR RESEÑAS ↗**.",
            "Descarga la imagen PNG o la tabla CSV para tu reporte.",
        ], 1):
            st.markdown(f"**{i}.** {paso}")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_der:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Ideal para")
        for caso in [
            "🍽️ Restaurantes y cafeterías",
            "🏨 Hoteles y alojamientos turísticos",
            "🛍️ Tiendas físicas y en línea",
            "📱 Comentarios en redes sociales",
            "📋 Encuestas de satisfacción",
            "🎟️ Eventos y experiencias turísticas",
            "💼 Reportes de servicio al cliente",
        ]:
            st.markdown(
                f'<span class="uso-tag">{caso}</span>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card" style="margin-top:16px;">', unsafe_allow_html=True)
        st.markdown("### Paletas del radar")
        for nombre in PALETAS.keys():
            st.markdown(
                f'<div style="padding:5px 0; border-bottom:1px solid #f1e8d8;">'
                f'<span style="color:#12343b; font-size:0.88rem; font-weight:500;">{nombre}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    if not texto_input.strip() and generar:
        st.warning("Pega o sube algunas reseñas en el panel lateral antes de escanear.")
    st.stop()


# ─────────────────────────────────────────────
# PROCESAMIENTO
# ─────────────────────────────────────────────
stopwords_set = obtener_stopwords(idioma) if idioma != "Ninguno" else set()
if palabras_extra.strip():
    stopwords_set |= {p.strip().lower() for p in palabras_extra.split(",") if p.strip()}

texto_limpio = limpiar_texto(texto_input, stopwords_set, min_longitud)

if not texto_limpio.strip():
    st.error("No quedaron palabras tras el filtrado. Reduce la longitud mínima o cambia la configuración de stopwords.")
    st.stop()

df_freq        = contar_palabras(texto_limpio)
total_palabras = len(texto_limpio.split())
vocabulario    = len(df_freq)

# ── Métricas ──
m1, m2, m3, m4 = st.columns(4)
m1.metric("Palabras analizadas",     f"{total_palabras:,}")
m2.metric("Términos distintos",      f"{vocabulario:,}")
m3.metric("Tema más mencionado",     df_freq.iloc[0]["Palabra"] if not df_freq.empty else "—")
m4.metric("Menciones máximas",       int(df_freq.iloc[0]["Frecuencia"]) if not df_freq.empty else 0)

st.markdown("<br>", unsafe_allow_html=True)

# ── Nube ──
with st.spinner("Escaneando reseñas..."):
    fig_wc = generar_wordcloud(
        texto_limpio, paleta_sel, max_words, fondo_color,
        FORMAS[forma_sel], ancho=1000, alto=520,
    )

st.markdown('<div class="wc-container">', unsafe_allow_html=True)
st.markdown(f"**Mapa de opiniones** &nbsp;·&nbsp; Paleta: *{paleta_sel}* &nbsp;·&nbsp; Fondo: *{fondo_sel}* &nbsp;·&nbsp; {max_words} palabras máx.")
st.pyplot(fig_wc, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

img_bytes = fig_a_bytes(fig_wc)
st.download_button(
    "⬇️ Descargar imagen PNG",
    data=img_bytes, file_name="wordcloud.png", mime="image/png",
    use_container_width=True,
)

st.divider()

# ── Análisis ──
col_freq, col_tabla = st.columns([3, 2], gap="large")

with col_freq:
    st.markdown("### Lo que más dicen tus clientes — Top 20")
    top20    = df_freq.head(20)
    max_freq = top20["Frecuencia"].max()

    for rank, (_, row) in enumerate(top20.iterrows(), 1):
        p = row["Palabra"]
        f = int(row["Frecuencia"])
        barra_w = max(12, int((f / max_freq) * 210))
        st.markdown(
            f'<div class="freq-row">'
            f'<span class="rank-tag">#{rank:02d}</span>'
            f'<span style="font-weight:600; color:#12343b; min-width:130px; font-size:0.93rem;">{p}</span>'
            f'<div class="freq-bar" style="width:{barra_w}px; opacity:{0.5 + 0.5*(f/max_freq):.2f};"></div>'
            f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:0.88rem; '
            f'color:#3b4a4e; min-width:28px; text-align:right; font-weight:500;">{f}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

with col_tabla:
    st.markdown("### Tabla de menciones")
    st.dataframe(
        df_freq.head(30).style
               .background_gradient(subset=["Frecuencia"], cmap="Oranges")
               .format({"Frecuencia": "{:,}"}),
        use_container_width=True, height=500,
    )
    csv_bytes = df_freq.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Exportar tabla (.csv)",
        data=csv_bytes, file_name="frecuencias.csv", mime="text/csv",
        use_container_width=True,
    )

st.divider()

with st.expander("Ver reseñas procesadas (tras eliminación de stopwords)"):
    preview = texto_limpio[:2500] + ("..." if len(texto_limpio) > 2500 else "")
    st.markdown(
        f'<p style="font-family:IBM Plex Mono,monospace; font-size:0.85rem; '
        f'color:#3b4a4e; background:#fffdf9; padding:16px; border-radius:12px; '
        f'border:1px solid #eadfce; line-height:1.8;">{preview}</p>',
        unsafe_allow_html=True,
    )

plt.close("all")
