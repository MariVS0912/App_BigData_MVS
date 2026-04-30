import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Dashboard IoT", layout="wide")
st.title("📊 Dashboard de Control IoT")

# --- 1. Carga de archivo ---
file = st.file_uploader("Sube tu archivo CSV (iot_data.csv)", type=["csv"])

if file:
    # Cargar datos
    df = pd.read_csv(file)
    
    # Convertir columna de fecha a datetime (necesario para filtros y gráficas)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Vista previa de los datos
    with st.expander("Ver vista previa de los datos"):
        st.write(df.head())

    # --- 4. Filtros interactivos (En la barra lateral) ---
    st.sidebar.header("Filtros")
    
    # Filtro por device_id
    dispositivos = df['device_id'].unique()
    device_selected = st.sidebar.multiselect("Selecciona ID del Dispositivo", dispositivos, default=dispositivos)
    
    # Filtro por rango de fechas
    if 'timestamp' in df.columns:
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        date_range = st.sidebar.date_input("Rango de fechas", [min_date, max_date])

    # Aplicar filtros al DataFrame original
    df_filtered = df[df['device_id'].isin(device_selected)]
    if len(date_range) == 2:
        start, end = date_range
        df_filtered = df_filtered[(df_filtered['timestamp'].dt.date >= start) & (df_filtered['timestamp'].dt.date <= end)]

    # --- 2. Estadísticas básicas (Analítica Descriptiva) ---
    st.subheader("Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Promedio Temperatura", f"{df_filtered['temperature'].mean():.2f} °C")
    with col2:
        st.metric("Promedio Consumo Energético", f"{df_filtered['energy_consumption'].mean():.2f} kWh")
    with col3:
        st.metric("Máxima Vibración", f"{df_filtered['vibration'].max():.2f}")
    with col4:
        # Conteo de estados
        conteo_status = df_filtered['status'].value_counts()
        st.write("**Conteo de Estados:**")
        st.write(conteo_status)

    # --- 3. Visualizaciones ---
    st.subheader("Análisis Visual")
    col_a, col_b = st.columns(2)

    with col_a:
        # Gráfica 1: Serie de tiempo (Temperatura vs Tiempo)
        st.write("### Temperatura vs Tiempo")
        fig1, ax1 = plt.subplots()
        ax1.plot(df_filtered['timestamp'], df_filtered['temperature'], color='tab:red')
        ax1.set_ylabel("Temperatura")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        # Gráfica 2: Distribución (Histograma de consumo energético)
        st.write("### Distribución de Consumo Energético")
        fig2, ax2 = plt.subplots()
        ax2.hist(df_filtered['energy_consumption'], bins=20, color='skyblue', edgecolor='black')
        st.pyplot(fig2)

    with col_b:
        # Gráfica 3: Relación entre variables (Temperatura vs Consumo)
        st.write("### Temperatura vs Consumo Energético")
        fig3, ax3 = plt.subplots()
        ax3.scatter(df_filtered['temperature'], df_filtered['energy_consumption'], alpha=0.5)
        ax3.set_xlabel("Temperatura")
        ax3.set_ylabel("Consumo")
        st.pyplot(fig3)

    # --- 5. Sección de Insights (Interpretación) ---
    st.subheader("Insights y Alertas")
    
    avg_temp = df_filtered['temperature'].mean()
    if avg_temp > 30:
        st.warning(f"⚠️ **Advertencia:** La temperatura promedio es elevada ({avg_temp:.2f} °C).")
    else:
        st.success("✅ La temperatura promedio está en niveles normales.")

    if "FAIL" in df_filtered['status'].values:
        st.error("🚨 **Alerta:** Se han detectado registros con estado 'FAIL'. Revisar dispositivos de inmediato.")
    else:
        st.info("ℹ️ No se detectaron fallos en los registros actuales.")

else:
    st.info("Por favor, sube el archivo CSV para generar el tablero.")
