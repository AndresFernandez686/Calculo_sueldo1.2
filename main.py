"""
Aplicación principal para cálculo de sueldos
Versión modularizada para mejor organización del código
"""
import streamlit as st
import pandas as pd
from ui_components import (
    mostrar_descarga_plantilla, 
    mostrar_input_valor_hora, 
    mostrar_input_porcentaje_extra,
    configurar_feriados, 
    mostrar_subida_archivo
)
from data_processor import (
    validar_archivo_excel, 
    procesar_datos_excel, 
    mostrar_resultados
)

# Función para cargar CSS
def load_css():
    """Carga los estilos CSS personalizados"""
    try:
        with open("styles.css", encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Archivo de estilos no encontrado. Usando estilos por defecto.")
    except UnicodeDecodeError:
        st.warning("Error de codificación en el archivo de estilos. Usando estilos por defecto.")

# Función para mostrar el header personalizado
def show_custom_header():
    """Muestra el header personalizado con HTML"""
    st.markdown("""
    <div class="main-container fade-in-up">
        <h1 class="main-title">
            Calculadora de Sueldos Profesional
        </h1>
        <div style="text-align: center; margin-bottom: 2rem;">
            <span class="badge badge-info">Sistema de Cálculo Avanzado</span>
            <span class="badge badge-success">Feriados por Día</span>
            <span class="badge badge-warning">Procesamiento Inteligente</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Inicializar session_state
if "exit_app" not in st.session_state:
    st.session_state.exit_app = False

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Sueldos Profesional", 
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cargar estilos CSS personalizados
load_css()

# Verificar si se debe salir de la app
if st.session_state.exit_app:
    st.markdown("""
    <div class="main-container">
        <div class="custom-alert alert-success">
            <h2>👋 Gracias por usar la Calculadora de Sueldos</h2>
            <p>La aplicación se ha cerrado correctamente. Puedes cerrar la pestaña.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Mostrar header personalizado
show_custom_header()

# Sección de descarga de plantilla
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Plantilla de Excel</div>', unsafe_allow_html=True)
mostrar_descarga_plantilla()
st.markdown('</div>', unsafe_allow_html=True)

# Sección de configuración
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Configuración</div>', unsafe_allow_html=True)

# Configuración en dos filas
# Primera fila: Valor por hora
col1, col2 = st.columns([1, 1])
with col1:
    valor_por_hora = mostrar_input_valor_hora()
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Valor por Hora</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">${valor_por_hora:,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Segunda fila: Porcentaje de horas extra
col3, col4 = st.columns([1, 1])
with col3:
    porcentaje_extra = mostrar_input_porcentaje_extra()
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Recargo Horas Extra</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{porcentaje_extra*100:.1f}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sección de feriados
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Configuración de Feriados</div>', unsafe_allow_html=True)
opcion_feriados, dias_feriados, cantidad_feriados = configurar_feriados()
st.markdown('</div>', unsafe_allow_html=True)

# Sección de subida de archivo
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Subir Archivo</div>', unsafe_allow_html=True)
uploaded_file, tipo_archivo = mostrar_subida_archivo()
st.markdown('</div>', unsafe_allow_html=True)

# Procesamiento de datos
if uploaded_file:
    st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Procesamiento de Datos</div>', unsafe_allow_html=True)
    
    if tipo_archivo == "excel":
        # Procesamiento tradicional de Excel
        st.markdown('<div class="custom-alert alert-info">Procesando archivo Excel...</div>', unsafe_allow_html=True)
        
        df = pd.read_excel(uploaded_file)
        es_valido, columnas_faltantes = validar_archivo_excel(df)

        if not es_valido:
            st.markdown(f'<div class="custom-alert alert-error">El archivo Excel no contiene las siguientes columnas necesarias: {", ".join(columnas_faltantes)}</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Calculando sueldos..."):
                resultado_procesamiento = procesar_datos_excel(
                    df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados, porcentaje_extra
                )
                
                # Desempaquetar resultados (manejo compatible con versión anterior)
                if len(resultado_procesamiento) == 3:
                    # Versión anterior sin detección de marcaciones incompletas
                    resultados, total_horas, total_sueldos = resultado_procesamiento
                    mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora, dias_feriados, porcentaje_extra)
                elif len(resultado_procesamiento) == 5:
                    # Nueva versión con detección de marcaciones incompletas
                    resultados, total_horas, total_sueldos, dias_incompletos, correcciones = resultado_procesamiento
                    
                    # Solo mostrar resultados si se procesaron datos (no hay días pendientes)
                    if resultados:
                        mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora, dias_feriados, porcentaje_extra)
                        
                        # Mostrar información sobre correcciones aplicadas si las hubo
                        if correcciones:
                            st.markdown(f"""
                            <div class="custom-alert alert-info">
                                <h4>Información de Correcciones</h4>
                                <p>Se aplicaron correcciones a {len(correcciones)} día(s) con marcaciones incompletas.</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    elif tipo_archivo == "pdf":
        # Procesamiento inteligente de PDF
        st.markdown('<div class="custom-alert alert-info">Procesando PDF de manera inteligente...</div>', unsafe_allow_html=True)
        
        from pdf_processor import procesar_pdf_a_dataframe, validar_datos_pdf
        
        with st.spinner("Procesando PDF de manera inteligente..."):
            # Procesar PDF a DataFrame
            df = procesar_pdf_a_dataframe(uploaded_file)
            
            if df.empty:
                st.markdown('<div class="custom-alert alert-error">No se pudieron extraer datos del PDF. Verifica que el archivo contenga información de asistencia.</div>', unsafe_allow_html=True)
            else:
                # Validar datos extraídos
                es_valido, errores = validar_datos_pdf(df)
                
                if not es_valido:
                    st.markdown('<div class="custom-alert alert-error">Errores en los datos extraídos del PDF:</div>', unsafe_allow_html=True)
                    for error in errores:
                        st.markdown(f'<div class="custom-alert alert-warning">• {error}</div>', unsafe_allow_html=True)
                else:
                    # Mostrar preview de datos extraídos
                    st.markdown('<div class="custom-alert alert-success">PDF procesado exitosamente. Datos extraídos:</div>', unsafe_allow_html=True)
                    st.dataframe(df.head())
                    
                    # Procesar con la lógica existente
                    with st.spinner("Calculando sueldos..."):
                        resultado_procesamiento = procesar_datos_excel(
                            df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados, porcentaje_extra
                        )
                        
                        # Desempaquetar resultados (manejo compatible con versión anterior)
                        if len(resultado_procesamiento) == 3:
                            # Versión anterior sin detección de marcaciones incompletas
                            resultados, total_horas, total_sueldos = resultado_procesamiento
                            mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora, dias_feriados, porcentaje_extra)
                        elif len(resultado_procesamiento) == 5:
                            # Nueva versión con detección de marcaciones incompletas
                            resultados, total_horas, total_sueldos, dias_incompletos, correcciones = resultado_procesamiento
                            
                            # Solo mostrar resultados si se procesaron datos (no hay días pendientes)
                            if resultados:
                                mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora, dias_feriados, porcentaje_extra)
                                
                                # Mostrar información sobre correcciones aplicadas si las hubo
                                if correcciones:
                                    st.markdown(f"""
                                    <div class="custom-alert alert-info">
                                        <h4>Información de Correcciones</h4>
                                        <p>Se aplicaron correcciones a {len(correcciones)} día(s) con marcaciones incompletas.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Botón para salir de la app
st.markdown("---")
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Salir de la aplicación", key="exit_button"):
        st.session_state.exit_app = True
        st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)