import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="WildIndex Dashboard",
    page_icon="🦁",
    layout="wide"
)

# Constantes
DB_PATH = "/app/data/db/wildindex.db"
IMAGE_ROOT = "/app/data/processed"

def get_connection():
    """Conecta a la base de datos SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        st.error(f"Error conectando a la DB: {e}")
        return None

def load_data(limit=100, category=None, min_conf=0.0):
    """Carga datos de la base de datos con filtros."""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    query = "SELECT * FROM processed_images WHERE 1=1"
    params = []

    if category and category != "Todos":
        query += " AND md_category = ?"
        params.append(category)
    
    if min_conf > 0:
        query += " AND md_confidence >= ?"
        params.append(min_conf)

    query += " ORDER BY capture_timestamp DESC LIMIT ?"
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# --- Sidebar ---
st.sidebar.title("🦁 WildIndex")
st.sidebar.header("Filtros")

# Filtro de Categoría
category_filter = st.sidebar.selectbox(
    "Categoría",
    ["Todos", "animal", "person", "vehicle", "empty"]
)

# Filtro de Confianza
conf_filter = st.sidebar.slider(
    "Confianza Mínima (MegaDetector)",
    min_value=0.0,
    max_value=1.0,
    value=0.2,
    step=0.05
)

# Límite de imágenes
limit_filter = st.sidebar.number_input("Límite de imágenes", min_value=10, max_value=1000, value=50)

if st.sidebar.button("🔄 Actualizar"):
    st.rerun()

# --- Main Content ---
st.title("📸 Galería de Imágenes")

# Cargar datos
df = load_data(limit=limit_filter, category=category_filter, min_conf=conf_filter)

if df.empty:
    st.info("No se encontraron imágenes con los filtros seleccionados.")
else:
    st.write(f"Mostrando las últimas **{len(df)}** imágenes procesadas.")

    # Grid de imágenes
    cols = st.columns(3)
    for idx, row in df.iterrows():
        col = cols[idx % 3]
        
        # Construir ruta de la imagen
        # La estructura en processed es: /app/data/processed/{category}/{filename}
        # Pero a veces el filename ya incluye la ruta relativa o solo el nombre.
        # Asumimos que row['file_name'] es solo el nombre.
        
        # Intentar deducir la ruta si no está explícita
        # En batch_processor.py guardamos: dest_folder = self.output_dir / category
        image_path = os.path.join(IMAGE_ROOT, row['md_category'], row['file_name'])
        
        with col:
            try:
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    st.image(img, use_container_width=True)
                    
                    # Metadata
                    st.caption(f"**{row['file_name']}**")
                    st.markdown(f"**Categoría:** `{row['md_category']}` ({row['md_confidence']:.2f})")
                    
                    if row['llava_caption']:
                        with st.expander("📝 Descripción LLaVA"):
                            st.write(row['llava_caption'])
                            
                    if row['species_prediction']:
                        st.markdown(f"🧬 **Especie:** {row['species_prediction']}")
                        
                else:
                    st.warning(f"Imagen no encontrada: {row['file_name']}")
            except Exception as e:
                st.error(f"Error cargando imagen: {e}")

    # Tabla de datos raw (opcional)
    with st.expander("📊 Ver datos crudos"):
        st.dataframe(df)
