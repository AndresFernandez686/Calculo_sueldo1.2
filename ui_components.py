"""
Módulo de componentes de interfaz de usuario
Contiene funciones para crear elementos de la UI
"""
import streamlit as st
import calendar
from datetime import datetime

def mostrar_input_valor_hora():
    """
    Muestra el input para el valor por hora con estilo mejorado
    
    Returns:
        float: Valor por hora ingresado
    """
    st.markdown("### 💲 Valor por Hora")
    return st.number_input(
        "Ingrese el valor por hora:", 
        min_value=0.0, 
        value=13937.0,
        step=100.0,
        format="%.0f",
        help="Este valor se aplicará a todas las horas trabajadas por los empleados"
    )

def mostrar_descarga_plantilla():
    """
    Muestra el botón de descarga de la plantilla Excel con estilo personalizado
    """
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>📄 Descarga la plantilla de Excel</strong><br>
        Completa la plantilla con los datos de tus empleados y súbela para calcular automáticamente los sueldos.
    </div>
    """, unsafe_allow_html=True)
    
    with open("plantilla_sueldos_feriados_dias.xlsx", "rb") as f:
        st.download_button(
            "Descargar Plantilla Excel", 
            f, 
            file_name="plantilla_sueldos_feriados_dias.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Descarga la plantilla oficial para cargar datos de empleados"
        )

def configurar_feriados():
    """
    Muestra la configuración de feriados de forma simple
    
    Returns:
        tuple: (opcion_feriados, fechas_feriados, cantidad_feriados)
    """
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>📅 Selecciona hasta 3 fechas de feriados</strong><br>
        Los días feriados reciben doble pago automáticamente.
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session state para feriados si no existe
    if 'feriados_list' not in st.session_state:
        st.session_state.feriados_list = []
    
    # Mostrar selector de fecha simple
    st.markdown("### � Agregar Fecha de Feriado")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fecha_seleccionada = st.date_input(
            "Selecciona una fecha:",
            value=datetime.now(),
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31),
            help="Haz clic para abrir el calendario y seleccionar una fecha",
            key="date_picker_feriado"
        )
    
    with col2:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("➕ Agregar", use_container_width=True):
            if len(st.session_state.feriados_list) >= 3:
                st.error("⚠️ Máximo 3 fechas de feriados permitidas")
            elif fecha_seleccionada in st.session_state.feriados_list:
                st.warning("⚠️ Esta fecha ya está agregada")
            else:
                st.session_state.feriados_list.append(fecha_seleccionada)
                st.success(f"✅ Feriado agregado: {fecha_seleccionada.strftime('%d/%m/%Y')}")
    
    # Mostrar feriados seleccionados con opción de eliminar
    if st.session_state.feriados_list:
        st.markdown("### 📋 Feriados Seleccionados:")
        
        for idx, fecha in enumerate(sorted(st.session_state.feriados_list)):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="custom-alert alert-success" style="margin: 0.2rem 0; padding: 0.8rem;">
                    <strong>🎉 {fecha.strftime('%d/%m/%Y - %A')}</strong>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"delete_{idx}", help="Eliminar este feriado"):
                    st.session_state.feriados_list.remove(fecha)
                    st.rerun()
        
        # Botón para limpiar todos
        if st.button("🗑️ Limpiar Todos", help="Eliminar todas las fechas de feriados"):
            st.session_state.feriados_list = []
            st.rerun()
    
    # Convertir lista a set para compatibilidad con el resto del código
    fechas_feriados = set(st.session_state.feriados_list)
    opcion_feriados = "📆 Seleccionar fechas específicas"
    cantidad_feriados = len(fechas_feriados)
    
    return opcion_feriados, fechas_feriados, cantidad_feriados

def mostrar_subida_archivo():
    """
    Muestra el widget de subida de archivo Excel o PDF con estilo mejorado
    
    Returns:
        tuple: (archivo_subido, tipo_archivo) o (lista_archivos, tipo_archivo) para PDFs
    """
    st.markdown("### 📤 Selecciona el tipo de archivo")
    
    # Selector de tipo de archivo con botones mejorados
    col1, col2 = st.columns(2)
    
    with col1:
        excel_selected = st.button("📊 Archivo Excel", use_container_width=True, help="Datos estructurados tradicionales")
    
    with col2:
        pdf_selected = st.button("📄 Archivos PDF (Hasta 2)", use_container_width=True, help="Procesamiento inteligente automático - Períodos quincenales")
    
    # Mantener selección en session state
    if excel_selected:
        st.session_state.file_type = "excel"
    elif pdf_selected:
        st.session_state.file_type = "pdf"
    
    # Valor por defecto
    if "file_type" not in st.session_state:
        st.session_state.file_type = "excel"
    
    tipo_archivo = st.session_state.file_type
    
    if tipo_archivo == "excel":
        st.markdown("""
        <div class="custom-alert alert-info">
            <strong>📊 Modo Excel Tradicional</strong><br>
            Sube tu archivo Excel completado con todos los datos de empleados.
        </div>
        """, unsafe_allow_html=True)
        
        archivo = st.file_uploader(
            "Sube tu archivo Excel completado:",
            type=["xlsx"],
            help="Archivo Excel con columnas: Empleado, Fecha, Entrada, Salida, Descuento Inventario, Descuento Caja, Retiro",
            key="excel_uploader"
        )
        return archivo, "excel"
    
    else:  # PDF
        st.markdown("""
        <div class="custom-alert alert-warning">
            <strong>🤖 Modo Inteligente PDF Activado - Períodos Quincenales</strong><br>
            Sube hasta 2 PDFs (uno por cada quincena). El sistema los ordenará automáticamente por fecha.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="custom-alert alert-info">
            <strong>💡 Tip:</strong> No importa el orden en que subas los PDFs (primera o segunda quincena). 
            El sistema detectará las fechas y las ordenará automáticamente.
        </div>
        """, unsafe_allow_html=True)
        
        # Subida de archivos múltiples
        archivos = st.file_uploader(
            "Sube tus archivos PDF (máximo 2 quincenas):",
            type=["pdf"],
            accept_multiple_files=True,
            help="PDFs con información de empleados y horarios. Ejemplo: 1-15 octubre y 16-31 octubre",
            key="pdf_uploader"
        )
        
        # Validar que no se suban más de 2 archivos
        if archivos and len(archivos) > 2:
            st.error("⚠️ Máximo 2 archivos PDF permitidos (uno por cada quincena)")
            return None, "pdf"
        
        # Mostrar información de archivos subidos
        if archivos:
            st.markdown("### 📋 Archivos Cargados:")
            for idx, archivo in enumerate(archivos, 1):
                st.success(f"✅ PDF {idx}: {archivo.name}")
        
        return archivos, "pdf"


def mostrar_editor_registros_incompletos(df_incompletos):
    """
    Muestra una interfaz para completar registros con entrada o salida faltante.
    NOTA: Solo muestra registros donde falta UNO de los dos datos.
    Si faltan ambos, se excluyen automáticamente (no trabajó ese día).
    
    Args:
        df_incompletos: DataFrame con registros incompletos (falta solo entrada o solo salida)
        
    Returns:
        bool: True si se aplicaron correcciones, False si aún están pendientes
    """
    import pandas as pd
    from datetime import datetime
    
    if df_incompletos.empty:
        return df_incompletos
    
    st.markdown("""
    <div class="custom-alert alert-warning">
        <strong>⚠️ Registros Incompletos Detectados</strong><br>
        Algunos empleados marcaron entrada pero no salida (o viceversa). 
        Completa los datos faltantes para calcular las horas trabajadas.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🛠️ Completar Datos Faltantes")
    
    st.markdown("""
    <div class="custom-alert alert-info">
        💡 <strong>Nota:</strong> Los registros sin entrada NI salida se excluyen automáticamente 
        (empleado no trabajó ese día: falta o día libre).
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session_state para las correcciones si no existe
    if 'correcciones_horarios' not in st.session_state:
        st.session_state.correcciones_horarios = {}
    
    # Mostrar cada registro incompleto
    for idx, row in df_incompletos.iterrows():
        with st.expander(
            f"👤 {row['Empleado']} - 📅 {row['Fecha']} - ⚠️ Falta: {row['Dato_Faltante']}", 
            expanded=True
        ):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # Input para Entrada (considerar 0:00 como faltante)
                entrada_actual = str(row['Entrada']).strip()
                entrada_es_valida = (
                    pd.notna(row['Entrada']) and 
                    entrada_actual != '' and 
                    entrada_actual not in ['0:00', '00:00', 'nan']
                )
                
                if 'Entrada' in row['Dato_Faltante']:
                    # Necesita completar entrada
                    st.markdown("🕐 **Hora de Entrada** ⚠️ *Faltante*")
                    if entrada_actual in ['0:00', '00:00']:
                        st.caption(f"Valor actual: {entrada_actual} (inválido)")
                    entrada_key = f"entrada_{idx}"
                    entrada_corregida = st.time_input(
                        "Ingresa la hora de entrada:",
                        value=datetime.strptime("08:00", "%H:%M").time(),
                        key=entrada_key,
                        help="Hora aproximada en que el empleado ingresó"
                    )
                    st.session_state.correcciones_horarios[f"{idx}_entrada"] = entrada_corregida.strftime("%H:%M")
                else:
                    # Ya tiene entrada válida
                    st.markdown(f"🕐 **Hora de Entrada:** {entrada_actual} ✅")
            
            with col2:
                # Input para Salida (considerar 0:00 como faltante)
                salida_actual = str(row['Salida']).strip()
                salida_es_valida = (
                    pd.notna(row['Salida']) and 
                    salida_actual != '' and 
                    salida_actual not in ['0:00', '00:00', 'nan']
                )
                
                if 'Salida' in row['Dato_Faltante']:
                    # Necesita completar salida
                    st.markdown("🕔 **Hora de Salida** ⚠️ *Faltante*")
                    if salida_actual in ['0:00', '00:00']:
                        st.caption(f"Valor actual: {salida_actual} (inválido)")
                    salida_key = f"salida_{idx}"
                    salida_corregida = st.time_input(
                        "Ingresa la hora de salida:",
                        value=datetime.strptime("17:00", "%H:%M").time(),
                        key=salida_key,
                        help="Hora aproximada en que el empleado salió"
                    )
                    st.session_state.correcciones_horarios[f"{idx}_salida"] = salida_corregida.strftime("%H:%M")
                else:
                    # Ya tiene salida
                    st.markdown(f"🕔 **Hora de Salida:** {salida_actual} ✅")
            
            with col3:
                st.markdown("**Estado**")
                if f"{idx}_entrada" in st.session_state.correcciones_horarios or f"{idx}_salida" in st.session_state.correcciones_horarios:
                    st.success("✅ Listo")
                else:
                    st.warning("⏳ Pendiente")
    
    # Botón para aplicar correcciones
    st.markdown("---")
    if st.button("✅ Aplicar Correcciones y Continuar", type="primary", use_container_width=True):
        return True
    
    return False


def aplicar_correcciones_a_dataframe(df_original, df_incompletos):
    """
    Aplica las correcciones manuales al DataFrame original
    
    Args:
        df_original: DataFrame original con todos los datos
        df_incompletos: DataFrame con registros incompletos
        
    Returns:
        DataFrame: DataFrame corregido
    """
    import pandas as pd
    
    df_corregido = df_original.copy()
    
    if 'correcciones_horarios' not in st.session_state:
        return df_corregido
    
    # Aplicar correcciones
    for idx in df_incompletos.index:
        if f"{idx}_entrada" in st.session_state.correcciones_horarios:
            df_corregido.at[idx, 'Entrada'] = st.session_state.correcciones_horarios[f"{idx}_entrada"]
        
        if f"{idx}_salida" in st.session_state.correcciones_horarios:
            df_corregido.at[idx, 'Salida'] = st.session_state.correcciones_horarios[f"{idx}_salida"]
    
    return df_corregido
