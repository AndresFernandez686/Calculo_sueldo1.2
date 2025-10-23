"""
Aplicación principal para cálculo de sueldos
Versión modularizada para mejor organización del código
"""
import streamlit as st
import pandas as pd
from ui_components import (
    mostrar_descarga_plantilla, 
    mostrar_input_valor_hora, 
    configurar_feriados, 
    mostrar_subida_archivo
)
from data_processor import (
    validar_archivo_excel, 
    procesar_datos_excel, 
    mostrar_resultados
)
from loading_components import (
    mostrar_loading_excel,
    mostrar_loading_pdf,
    mostrar_loading_calculos,
    mostrar_loading_validacion,
    loading_context
)

# Función para cargar CSS
def load_css():
    """Carga los estilos CSS personalizados"""
    try:
        with open("styles.css", encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(" Archivo de estilos no encontrado. Usando estilos por defecto.")
    except UnicodeDecodeError:
        st.warning(" Error de codificación en el archivo de estilos. Usando estilos por defecto.")

# Función para mostrar el header personalizado
def show_custom_header():
    """Muestra el header personalizado con HTML"""
    st.markdown("""
    <div class="main-container fade-in-up">
        <h1 class="main-title">
             Calculadora de Sueldos
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
    page_title="Calculadora de Sueldos", 
    page_icon="",
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
            
            <p>La aplicación se ha cerrado correctamente. Puedes cerrar la pestaña.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Mostrar header personalizado
show_custom_header()

# Sección de descarga de plantilla
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header"> Plantilla de Excel</div>', unsafe_allow_html=True)
mostrar_descarga_plantilla()
st.markdown('</div>', unsafe_allow_html=True)

# Sección de configuración
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header"> Configuración</div>', unsafe_allow_html=True)

# Input para valor por hora
col1, col2 = st.columns([1, 1])
with col1:
    valor_por_hora = mostrar_input_valor_hora()
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Valor por Hora</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">${valor_por_hora:,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sección de feriados
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header"> Configuración de Feriados</div>', unsafe_allow_html=True)
opcion_feriados, dias_feriados, cantidad_feriados = configurar_feriados()
st.markdown('</div>', unsafe_allow_html=True)

# Sección de subida de archivo
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
st.markdown('<div class="section-header"> Subir Archivo</div>', unsafe_allow_html=True)
uploaded_file, tipo_archivo = mostrar_subida_archivo()
st.markdown('</div>', unsafe_allow_html=True)

# Procesamiento de datos
if uploaded_file:
    st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"> Procesamiento de Datos</div>', unsafe_allow_html=True)
    
    if tipo_archivo == "excel":
        # Procesamiento tradicional de Excel
        # Mostrar loading mientras se lee el archivo
        loading_placeholder = st.empty()
        with loading_placeholder:
            mostrar_loading_excel()
        
        try:
            df = pd.read_excel(uploaded_file)
            loading_placeholder.empty()  # Limpiar loading
            
            # Mostrar loading de validación
            validation_placeholder = st.empty()
            with validation_placeholder:
                mostrar_loading_validacion("Validando estructura del archivo...")
            
            es_valido, columnas_faltantes = validar_archivo_excel(df)
            validation_placeholder.empty()  # Limpiar loading de validación

            if not es_valido:
                st.markdown(f'<div class="custom-alert alert-error">El archivo Excel no contiene las siguientes columnas necesarias: {", ".join(columnas_faltantes)}</div>', unsafe_allow_html=True)
            else:
                # NUEVA FUNCIONALIDAD: Detectar y corregir registros incompletos en Excel
                from pdf_processor import detectar_registros_incompletos, filtrar_registros_sin_asistencia
                from ui_components import mostrar_editor_registros_incompletos, aplicar_correcciones_a_dataframe
                
                # Primero, filtrar registros sin asistencia (sin entrada ni salida = no trabajó)
                df_con_asistencia, df_sin_asistencia = filtrar_registros_sin_asistencia(df)
                
                # Mostrar información de registros excluidos
                if not df_sin_asistencia.empty:
                    st.markdown(f"""
                    <div class="custom-alert alert-info">
                        ℹ️ <strong>{len(df_sin_asistencia)} registro(s) excluido(s) automáticamente</strong><br>
                        Empleados sin entrada ni salida (día libre o falta). No se incluirán en el cálculo.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(" Ver registros excluidos", expanded=False):
                        st.dataframe(df_sin_asistencia[['Empleado', 'Fecha']], use_container_width=True)
                
                # Ahora detectar registros que necesitan corrección (falta solo entrada o solo salida)
                df_incompletos_excel = detectar_registros_incompletos(df_con_asistencia)
                
                if not df_incompletos_excel.empty:
                    # Mostrar interfaz de corrección
                    correcciones_aplicadas_excel = mostrar_editor_registros_incompletos(df_incompletos_excel)
                    
                    if correcciones_aplicadas_excel:
                        # Aplicar correcciones al DataFrame
                        df_con_asistencia = aplicar_correcciones_a_dataframe(df_con_asistencia, df_incompletos_excel)
                        
                        st.success(f"✅ {len(df_incompletos_excel)} registro(s) corregido(s) exitosamente")
                        
                        # Limpiar session state de correcciones
                        if 'correcciones_horarios' in st.session_state:
                            del st.session_state.correcciones_horarios
                    else:
                        # Detener ejecución hasta que se apliquen las correcciones
                        st.warning(" Completa los datos faltantes y presiona 'Aplicar Correcciones' para continuar")
                        st.stop()
                
                # Usar el DataFrame con asistencia para los cálculos
                df = df_con_asistencia
                
                # Mostrar loading de cálculos
                calc_placeholder = st.empty()
                with calc_placeholder:
                    mostrar_loading_calculos()
                
                resultados, total_horas, total_sueldos = procesar_datos_excel(
                    df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados
                )
                calc_placeholder.empty()  # Limpiar loading de cálculos
                
                mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora, dias_feriados)
        except Exception as e:
            loading_placeholder.empty()
            st.error(f" Error al procesar el archivo: {str(e)}")
    
    elif tipo_archivo == "pdf":
        # Procesamiento inteligente de PDF (soporta múltiples archivos)
        from pdf_processor import procesar_pdf_a_dataframe, validar_datos_pdf
        
        # Verificar si uploaded_file es una lista (múltiples archivos) o un solo archivo
        archivos_pdf = uploaded_file if isinstance(uploaded_file, list) else [uploaded_file] if uploaded_file else []
        
        if not archivos_pdf:
            st.markdown('<div class="custom-alert alert-warning"> No se han cargado archivos PDF.</div>', unsafe_allow_html=True)
        else:
            # Mostrar loading de PDFs
            pdf_loading_placeholder = st.empty()
            with pdf_loading_placeholder:
                mostrar_loading_pdf(len(archivos_pdf))
            
            # Lista para almacenar todos los DataFrames y nombres de archivos
            dataframes_list = []
            nombres_archivos_pdf = []
            
            # Procesar cada PDF
            for idx, archivo_pdf in enumerate(archivos_pdf, 1):
                df_temp = procesar_pdf_a_dataframe(archivo_pdf)
                
                if df_temp.empty:
                    st.warning(f" No se pudieron extraer datos del PDF {idx}: {archivo_pdf.name}")
                else:
                    # Validar datos extraídos
                    validation_pdf_placeholder = st.empty()
                    with validation_pdf_placeholder:
                        mostrar_loading_validacion(f"Validando PDF {idx}...")
                    
                    es_valido, errores = validar_datos_pdf(df_temp)
                    validation_pdf_placeholder.empty()
                    
                    if not es_valido:
                        st.warning(f"Errores en PDF {idx} ({archivo_pdf.name}):")
                        for error in errores:
                            st.markdown(f'<div class="custom-alert alert-warning">• {error}</div>', unsafe_allow_html=True)
                    else:
                        st.success(f"✅ PDF {idx} procesado: {archivo_pdf.name} ({len(df_temp)} registros)")
                        dataframes_list.append(df_temp)
                        nombres_archivos_pdf.append(archivo_pdf.name)
            
            # Limpiar loading de PDFs
            pdf_loading_placeholder.empty()
            
            # Combinar todos los DataFrames
            if not dataframes_list:
                st.markdown('<div class="custom-alert alert-error">No se pudieron extraer datos de ningún PDF. Verifica que los archivos contengan información de asistencia.</div>', unsafe_allow_html=True)
            else:
                # Concatenar todos los DataFrames
                df_combinado = pd.concat(dataframes_list, ignore_index=True)
                
                # Asegurar que las fechas estén en formato datetime
                df_combinado['Fecha'] = pd.to_datetime(df_combinado['Fecha'], errors='coerce')
                
                # Ordenar por Fecha primero (ascendente) y luego por Empleado
                df_combinado = df_combinado.sort_values(['Fecha', 'Empleado'], ascending=[True, True])
                
                # Reiniciar el índice después de ordenar
                df_combinado = df_combinado.reset_index(drop=True)
                
                # Mostrar información de período combinado
                fecha_minima = df_combinado['Fecha'].min()
                fecha_maxima = df_combinado['Fecha'].max()
                st.markdown(f"""
                <div class="custom-alert alert-success">
                    ✅ <strong>PDFs combinados exitosamente</strong><br>
                    📅 Período: {fecha_minima.strftime('%d/%m/%Y')} - {fecha_maxima.strftime('%d/%m/%Y')}<br>
                    📊 Total de registros: {len(df_combinado)}
                </div>
                """, unsafe_allow_html=True)
                
                # NUEVA FUNCIONALIDAD: Detectar y corregir registros incompletos
                from pdf_processor import detectar_registros_incompletos, filtrar_registros_sin_asistencia
                from ui_components import mostrar_editor_registros_incompletos, aplicar_correcciones_a_dataframe
                
                # Primero, filtrar registros sin asistencia (sin entrada ni salida = no trabajó)
                df_con_asistencia, df_sin_asistencia = filtrar_registros_sin_asistencia(df_combinado)
                
                # Mostrar información de registros excluidos
                if not df_sin_asistencia.empty:
                    st.markdown(f"""
                    <div class="custom-alert alert-info">
                        ℹ️ <strong>{len(df_sin_asistencia)} registro(s) excluido(s) automáticamente</strong><br>
                        Empleados sin entrada ni salida (día libre o falta). No se incluirán en el cálculo.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(" Ver registros excluidos", expanded=False):
                        st.dataframe(df_sin_asistencia[['Empleado', 'Fecha']], use_container_width=True)
                
                # Ahora detectar registros que necesitan corrección (falta solo entrada o solo salida)
                df_incompletos = detectar_registros_incompletos(df_con_asistencia)
                
                if not df_incompletos.empty:
                    # Mostrar interfaz de corrección
                    correcciones_aplicadas = mostrar_editor_registros_incompletos(df_incompletos)
                    
                    if correcciones_aplicadas:
                        # Aplicar correcciones al DataFrame
                        df_con_asistencia = aplicar_correcciones_a_dataframe(df_con_asistencia, df_incompletos)
                        
                        st.success(f"✅ {len(df_incompletos)} registro(s) corregido(s) exitosamente")
                        
                        # Limpiar session state de correcciones
                        if 'correcciones_horarios' in st.session_state:
                            del st.session_state.correcciones_horarios
                    else:
                        # Detener ejecución hasta que se apliquen las correcciones
                        st.warning(" Completa los datos faltantes y presiona 'Aplicar Correcciones' para continuar")
                        st.stop()
                
                # Usar el DataFrame con asistencia para los cálculos
                df_combinado = df_con_asistencia
                
                # Procesar con la lógica existente
                calc_pdf_placeholder = st.empty()
                with calc_pdf_placeholder:
                    mostrar_loading_calculos()
                
                resultados, total_horas, total_sueldos = procesar_datos_excel(
                    df_combinado, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados
                )
                calc_pdf_placeholder.empty()  # Limpiar loading
                
                # Generar nombre para el archivo Excel (usar el primer PDF o combinar nombres)
                if len(nombres_archivos_pdf) == 1:
                    nombre_excel = nombres_archivos_pdf[0]
                elif len(nombres_archivos_pdf) > 1:
                    # Si hay múltiples PDFs, usar un nombre combinado
                    nombre_excel = f"combinado_{len(nombres_archivos_pdf)}_pdfs"
                else:
                    nombre_excel = None
                
                mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora, dias_feriados, nombre_excel)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Botón para salir de la app
st.markdown("---")
st.markdown('<div class="section-card fade-in-up">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button(" Salir", key="exit_button"):
        st.session_state.exit_app = True
        st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)
