"""
🧭 Postales de Viaje — Tu viaje contado en palabras
Aplicación Streamlit con estética de cuaderno de viaje

Instalación:
    pip install streamlit wordcloud matplotlib pandas Pillow numpy

Ejecución:
    streamlit run wordcloud_app.py

Imagen de portada (opcional):
    Coloca un archivo llamado  portada.jpg  en la misma carpeta que este script.
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import io
import os
import base64
from collections import Counter
from wordcloud import WordCloud, STOPWORDS

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Postales de Viaje",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# IMAGEN DE PORTADA (portada.jpg)
# ─────────────────────────────────────────────
RUTA_PORTADA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portada.jpg")


def cargar_portada_base64():
    """Devuelve la imagen portada.jpg en base64, o None si no existe."""
    if os.path.exists(RUTA_PORTADA):
        with open(RUTA_PORTADA, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


PORTADA_B64 = cargar_portada_base64()

if PORTADA_B64:
    HEADER_BG = (
        "linear-gradient(105deg, rgba(11,60,73,0.88) 0%, rgba(11,60,73,0.55) 55%, rgba(231,111,81,0.35) 100%), "
        f"url('data:image/jpeg;base64,{PORTADA_B64}')"
    )
else:
    HEADER_BG = "linear-gradient(115deg, #0b3c49 0%, #0f766e 55%, #e76f51 130%)"

# ─────────────────────────────────────────────
# ESTILOS — cuaderno de viaje / postal vintage
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general: papel crema */
    .stApp {
        background-color: #fbf6ec;
        background-image: radial-gradient(#efe4cc 1px, transparent 1px);
        background-size: 22px 22px;
    }

    /* Sidebar: arena cálida */
    [data-testid="stSidebar"] {
        background-color: #f3e9d2 !important;
        border-right: 2px dashed #d9c9a3;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0b3c49 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
    }
    [data-testid="stSidebar"] label {
        color: #3d5a62 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] p {
        color: #5c6f73 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #d9c9a3 !important;
        margin: 16px 0 !important;
    }

    /* Inputs */
    textarea, input[type="text"] {
        background-color: #fffdf7 !important;
        border: 1.5px solid #d9c9a3 !important;
        border-radius: 10px !important;
        color: #1c2b2e !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
    }
    textarea:focus, input[type="text"]:focus {
        border-color: #0f766e !important;
        box-shadow: 0 0 0 3px rgba(15,118,110,0.18) !important;
    }

    /* Selectbox */
    [data-baseweb="select"] > div {
        background: #fffdf7 !important;
        border: 1.5px solid #d9c9a3 !important;
        border-radius: 10px !important;
        color: #1c2b2e !important;
        font-size: 0.9rem !important;
    }

    /* Títulos */
    h1 {
        font-family: 'Inter', sans-serif !important;
        color: #0b3c49 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    h2, h3 {
        font-family: 'Inter', sans-serif !important;
        color: #0f4c5c !important;
        font-weight: 600 !important;
    }
    p, li {
        color: #3b4a4d !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
    }

    /* Botón principal — coral */
    .stButton > button {
        background: #e76f51 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.6px !important;
        padding: 0.65rem 1.4rem !important;
        width: 100% !important;
        box-shadow: 0 3px 0 #b9503a !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #d95f41 !important;
        transform: translateY(1px);
        box-shadow: 0 2px 0 #b9503a !important;
    }

    /* Botón descarga — verde azulado */
    [data-testid="stDownloadButton"] button {
        background: #0f766e !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        box-shadow: 0 3px 0 #0a524c !important;
        transition: background 0.2s, transform 0.15s !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #0b5f58 !important;
        transform: translateY(1px);
    }

    /* Métricas — estilo "sello" */
    [data-testid="metric-container"] {
        background: #fffdf7;
        border: 1.5px dashed #d9c9a3;
        border-bottom: 4px solid #e76f51;
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 4px 10px rgba(11,60,73,0.06);
    }
    [data-testid="metric-container"] label {
        color: #7a8a8c !important;
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #0b3c49 !important;
        font-weight: 700 !important;
        font-size: 1.55rem !important;
    }

    /* Header con portada */
    .header-card {
        position: relative;
        border-radius: 18px;
        padding: 56px 44px;
        margin-bottom: 26px;
        box-shadow: 0 10px 28px rgba(11,60,73,0.22);
        overflow: hidden;
        background-size: cover;
        background-position: center;
    }
    .header-card h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 2.2rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.35);
    }
    .header-card p {
        color: #fde9d9 !important;
        margin: 8px 0 0 0;
        font-size: 1.02rem !important;
    }
    .header-sello {
        display: inline-block;
        border: 2px solid #ffd9c7;
        color: #ffd9c7;
        border-radius: 6px;
        padding: 2px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 14px;
        transform: rotate(-2deg);
    }

    /* Sección card — tarjeta postal */
    .section-card {
        background: #fffdf7;
        border: 1.5px solid #eadfc4;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(11,60,73,0.05);
    }

    /* Barras de frecuencia */
    .freq-row {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 7px 14px;
        margin: 4px 0;
        background: #fffdf7;
        border: 1px solid #eadfc4;
        border-radius: 10px;
        transition: background 0.15s, transform 0.15s;
    }
    .freq-row:hover { background: #fdf1de; transform: translateX(3px); }

    .freq-bar {
        height: 9px;
        background: linear-gradient(90deg, #0f766e, #e76f51);
        border-radius: 6px;
        display: inline-block;
        vertical-align: middle;
    }

    /* Tag de ranking */
    .rank-tag {
        background: #0b3c49;
        border-radius: 6px;
        padding: 1px 8px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #fde9d9;
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
        background: #fdf6e6;
        border: 1px solid #eadfc4;
        border-left: 4px solid #e76f51;
        border-radius: 10px;
        margin-bottom: 8px;
    }

    /* Uso tags */
    .uso-tag {
        display: inline-block;
        background: #e3f1ef;
        border: 1px solid #b9dcd7;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #0b4f49;
        margin: 4px 3px;
    }

    /* Expander */
    div[data-testid="stExpander"] {
        border: 1.5px solid #eadfc4 !important;
        border-radius: 12px !important;
        background: #fffdf7 !important;
    }

    hr { border-color: #eadfc4 !important; }

    /* Nube container — marco de postal */
    .wc-container {
        background: #fffdf7;
        border: 1.5px solid #eadfc4;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 6px 16px rgba(11,60,73,0.08);
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
    "Atardecer costero":    ["#0b3c49","#0f766e","#e76f51","#f4a261","#e9c46a","#2a9d8f","#264653"],
    "Escala de grises":     ["#111827","#1f2937","#374151","#4b5563","#6b7280","#9ca3af","#d1d5db"],
    "Azul corporativo":     ["#1e3a5f","#1d4ed8","#2563eb","#3b82f6","#60a5fa","#93c5fd","#0f2942"],
    "Verde institucional":  ["#064e3b","#065f46","#047857","#059669","#10b981","#34d399","#6ee7b7"],
    "Gris azulado":         ["#0f172a","#1e293b","#334155","#475569","#64748b","#94a3b8","#cbd5e1"],
    "Terracota":            ["#7c2d12","#9a3412","#c2410c","#ea580c","#f97316","#fb923c","#fdba74"],
    "Índigo profundo":      ["#1e1b4b","#312e81","#3730a3","#4338ca","#4f46e5","#6366f1","#818cf8"],
    "Monocromático negro":  ["#000000","#111111","#222222","#444444","#666666","#888888","#aaaaaa"],
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
    st.markdown("## 🧭 Postales de Viaje")
    st.divider()

    # ── Fuente ──
    st.markdown("### FUENTE DE TEXTO")
    fuente = st.radio("fuente", ["✍️ Escribir / Pegar", "📂 Subir archivo"],
                      label_visibility="collapsed")
    texto_input = ""

    if fuente == "✍️ Escribir / Pegar":
        texto_input = st.text_area(
            "Texto:", height=190,
            placeholder="Pega aquí tu diario de viaje, reseñas de hoteles, cartas o comentarios de otros viajeros...")

        with st.expander("Cargar texto de ejemplo"):
            ejemplos = {
                "Inteligencia Artificial": """
                La inteligencia artificial es una disciplina de la informática orientada a desarrollar
                sistemas capaces de ejecutar tareas que requieren capacidades cognitivas humanas.
                El aprendizaje automático, las redes neuronales profundas y el procesamiento del
                lenguaje natural constituyen los pilares técnicos de los sistemas modernos de
                inteligencia artificial. Los modelos de lenguaje de gran escala, la visión
                computacional y la robótica autónoma representan aplicaciones de vanguardia.
                La inteligencia artificial transforma sectores como la salud, la educación,
                la manufactura, las finanzas y el transporte, generando eficiencias significativas.
                """,
                "Colombia": """
                Colombia es una nación situada en el extremo noroccidental de América del Sur,
                reconocida por su excepcional biodiversidad, riqueza cultural y diversidad de paisajes.
                Bogotá es la capital y principal centro económico, seguida de Medellín, Cali y
                Barranquilla como ciudades de relevancia nacional. El café colombiano goza de
                reconocimiento internacional por su calidad y perfil aromático. La floricultura
                colombiana abastece mercados globales con alta competitividad. El país alberga
                ecosistemas del Amazonas, los Andes, el Caribe y el Pacífico, constituyéndose
                como uno de los territorios con mayor biodiversidad del planeta.
                """,
                "Tecnología 4.0": """
                La cuarta revolución industrial redefine los modelos productivos mediante la
                convergencia de tecnologías digitales avanzadas. El Internet de las cosas,
                la inteligencia artificial, el análisis de grandes datos, la robótica colaborativa
                y la automatización inteligente son pilares estratégicos de la industria moderna.
                Las fábricas inteligentes integran sensores, conectividad y analítica para
                optimizar procesos en tiempo real. La manufactura aditiva, los gemelos digitales
                y la realidad aumentada transforman la ingeniería de producción. La computación
                en la nube y la ciberseguridad son habilitadores fundamentales de la
                transformación digital empresarial.
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
                col_txt = st.selectbox("Columna de texto:", df_csv.columns.tolist())
                texto_input = " ".join(df_csv[col_txt].dropna().astype(str).tolist())
            st.success(f"Archivo cargado — {len(texto_input):,} caracteres")

    st.divider()

    # ── Procesamiento ──
    st.markdown("### PROCESAMIENTO")
    idioma         = st.selectbox("Stopwords:", ["Español", "Inglés", "Ambos", "Ninguno"])
    min_longitud   = st.slider("Longitud mínima de palabra", 2, 8, 3)
    palabras_extra = st.text_input("Excluir palabras adicionales:",
                                   placeholder="ej: también, así, aquí")

    st.divider()

    # ── Apariencia ──
    st.markdown("### APARIENCIA")
    paleta_sel  = st.selectbox("Paleta:", list(PALETAS.keys()))
    fondo_sel   = st.radio("Fondo:", ["Blanco", "Negro"], horizontal=True)
    fondo_color = "white" if fondo_sel == "Blanco" else "black"
    forma_sel   = st.selectbox("Forma:", list(FORMAS.keys()))
    max_words   = st.slider("Máximo de palabras:", 20, 200, 80)

    st.divider()
    generar = st.button("GENERAR NUBE  ↗", use_container_width=True)


# ─────────────────────────────────────────────
# CONTENIDO PRINCIPAL
# ─────────────────────────────────────────────

# Header con imagen portada.jpg
st.markdown(f"""
<div class="header-card" style="background-image: {HEADER_BG};">
    <span class="header-sello">✈ Correo aéreo</span>
    <h1>🧭 Postales de Viaje</h1>
    <p>Tu viaje contado en palabras: descubre qué fue lo que más te marcó del camino</p>
</div>
""", unsafe_allow_html=True)

# ── Pantalla de bienvenida ──
if not generar or not texto_input.strip():
    col_izq, col_der = st.columns([3, 2], gap="large")

    with col_izq:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Acerca de esta herramienta")
        st.markdown("""
        **Postales de Viaje** convierte tus diarios, reseñas y mensajes de viaje en una
        **nube de palabras**: los términos que más repetiste (un sabor, un lugar, una emoción)
        aparecen en mayor tamaño, revelando de un vistazo qué fue lo que realmente
        definió tu experiencia.
        """)

        for icono, titulo, desc in [
            ("🧭", "Brújula de recuerdos", "Descubre qué palabras dominan la historia de tu viaje."),
            ("🧳", "Equipaje liviano", "Deja fuera las palabras vacías (*stopwords*) en español e inglés y quédate con lo esencial."),
            ("🖼️", "Postal a tu estilo", "Elige paleta, forma y cantidad de palabras para tu recuerdo visual."),
            ("✉️", "Envía tu postal", "Descarga la imagen en alta resolución y la tabla de frecuencias en CSV."),
        ]:
            st.markdown(
                f'<div class="info-item">'
                f'<span style="font-size:1.3rem; flex-shrink:0;">{icono}</span>'
                f'<div><strong style="color:#0b3c49;">{titulo}</strong>'
                f'<p style="margin:2px 0 0 0; color:#6b7a7c !important; font-size:0.88rem;">{desc}</p></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("#### Cómo armar tu postal")
        for i, paso in enumerate([
            "Pega o sube tu diario de viaje, reseñas o cartas en el panel lateral.",
            "Configura el idioma de *stopwords*, la paleta y el número de palabras.",
            "Haz clic en **GENERAR NUBE ↗**.",
            "Descarga tu postal en PNG o la tabla de frecuencias en CSV.",
        ], 1):
            st.markdown(f"**{i}.** {paso}")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_der:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### ¿Para qué viajeros?")
        for caso in [
            "📓 Diarios personales de viaje",
            "⭐ Reseñas de hoteles y tours",
            "🗺️ Opiniones sobre destinos",
            "📸 Pies de foto de álbumes",
            "💌 Cartas y postales escritas",
            "🎒 Encuestas a viajeros y mochileros",
            "🏛️ Comentarios sobre museos y sitios turísticos",
        ]:
            st.markdown(
                f'<span class="uso-tag">{caso}</span>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card" style="margin-top:16px;">', unsafe_allow_html=True)
        st.markdown("### Paletas disponibles")
        for nombre in PALETAS.keys():
            st.markdown(
                f'<div style="padding:5px 0; border-bottom:1px dashed #eadfc4;">'
                f'<span style="color:#3b4a4d; font-size:0.88rem; font-weight:500;">{nombre}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    if not texto_input.strip() and generar:
        st.warning("Ingresa un texto en el panel lateral antes de generar la nube.")
    st.stop()


# ─────────────────────────────────────────────
# PROCESAMIENTO
# ─────────────────────────────────────────────
stopwords_set = obtener_stopwords(idioma) if idioma != "Ninguno" else set()
if palabras_extra.strip():
    stopwords_set |= {p.strip().lower() for p in palabras_extra.split(",") if p.strip()}

texto_limpio = limpiar_texto(texto_input, stopwords_set, min_longitud)

if not texto_limpio.strip():
    st.error("El texto resultante está vacío. Reduce la longitud mínima o cambia la configuración de stopwords.")
    st.stop()

df_freq        = contar_palabras(texto_limpio)
total_palabras = len(texto_limpio.split())
vocabulario    = len(df_freq)

# ── Métricas ──
m1, m2, m3, m4 = st.columns(4)
m1.metric("Palabras procesadas",     f"{total_palabras:,}")
m2.metric("Vocabulario único",       f"{vocabulario:,}")
m3.metric("Término más frecuente",   df_freq.iloc[0]["Palabra"] if not df_freq.empty else "—")
m4.metric("Frecuencia máxima",       int(df_freq.iloc[0]["Frecuencia"]) if not df_freq.empty else 0)

st.markdown("<br>", unsafe_allow_html=True)

# ── Nube ──
with st.spinner("Generando nube de palabras..."):
    fig_wc = generar_wordcloud(
        texto_limpio, paleta_sel, max_words, fondo_color,
        FORMAS[forma_sel], ancho=1000, alto=520,
    )

st.markdown('<div class="wc-container">', unsafe_allow_html=True)
st.markdown(f"**Tu postal** &nbsp;·&nbsp; Paleta: *{paleta_sel}* &nbsp;·&nbsp; Fondo: *{fondo_sel}* &nbsp;·&nbsp; {max_words} palabras máx.")
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
    st.markdown("### Frecuencia léxica — Top 20")
    top20    = df_freq.head(20)
    max_freq = top20["Frecuencia"].max()

    for rank, (_, row) in enumerate(top20.iterrows(), 1):
        p = row["Palabra"]
        f = int(row["Frecuencia"])
        barra_w = max(12, int((f / max_freq) * 210))
        st.markdown(
            f'<div class="freq-row">'
            f'<span class="rank-tag">#{rank:02d}</span>'
            f'<span style="font-weight:600; color:#0b3c49; min-width:130px; font-size:0.93rem;">{p}</span>'
            f'<div class="freq-bar" style="width:{barra_w}px; opacity:{0.55 + 0.45*(f/max_freq):.2f};"></div>'
            f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:0.88rem; '
            f'color:#3b4a4d; min-width:28px; text-align:right; font-weight:500;">{f}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

with col_tabla:
    st.markdown("### Tabla de frecuencias")
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

with st.expander("Ver texto procesado (tras eliminación de stopwords)"):
    preview = texto_limpio[:2500] + ("..." if len(texto_limpio) > 2500 else "")
    st.markdown(
        f'<p style="font-family:IBM Plex Mono,monospace; font-size:0.85rem; '
        f'color:#3b4a4d; background:#fdf6e6; padding:16px; border-radius:10px; '
        f'border:1px dashed #d9c9a3; line-height:1.8;">{preview}</p>',
        unsafe_allow_html=True,
    )

plt.close("all")
