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
    st.markdown("### Valor por Hora")
    return st.number_input(
        "Ingrese el valor por hora en Guaraníes:", 
        min_value=0.0, 
        value=13937.0,
        step=100.0,
        format="%.0f",
        help="Este valor se aplicará a todas las horas trabajadas por los empleados"
    )

def mostrar_input_porcentaje_extra():
    """
    Muestra el input para configurar el porcentaje de horas extra
    
    Returns:
        float: Porcentaje de recargo para horas extra (como decimal)
    """
    st.markdown("### Porcentaje de Horas Extra (20:00-22:00)")
    
    porcentaje_ui = st.number_input(
        "Porcentaje de recargo para horas especiales:", 
        min_value=0.0, 
        max_value=200.0,
        value=30.0,
        step=5.0,
        format="%.1f",
        help="Porcentaje adicional que se paga por las horas trabajadas entre 20:00 y 22:00"
    )
    
    # Mostrar ejemplo de cálculo
    if porcentaje_ui > 0:
        st.info(f"**Ejemplo:** Si el valor por hora es $13,937 y trabaja 1 hora extra, cobrará: $13,937 + ${13937 * (porcentaje_ui/100):,.0f} = ${13937 * (1 + porcentaje_ui/100):,.0f}")
    
    # Convertir a decimal para cálculos internos
    return porcentaje_ui / 100.0

def mostrar_descarga_plantilla():
    """
    Muestra el botón de descarga de la plantilla Excel con estilo personalizado
    """
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>Descarga la plantilla de Excel</strong><br>
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
    Muestra la configuración de feriados con calendario visual mejorado
    
    Returns:
        tuple: (opcion_feriados, fechas_feriados, cantidad_feriados)
    """
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>Selecciona las fechas que fueron feriados</strong><br>
        Los días feriados reciben doble pago automáticamente.
    </div>
    """, unsafe_allow_html=True)
    
    # Solo mostrar el calendario, sin opciones
    opcion_feriados = "Seleccionar fechas específicas"
    fechas_feriados = _mostrar_calendario_feriados()
    cantidad_feriados = 0

    # Mostrar resumen de feriados seleccionados
    if fechas_feriados:
        st.markdown("### Feriados Seleccionados:")
        cols = st.columns(3)
        for i, fecha in enumerate(sorted(fechas_feriados)):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="custom-alert alert-success" style="margin: 0.2rem 0; padding: 0.5rem;">
                    <strong>{fecha.strftime("%d/%m/%Y")}</strong>
                </div>
                """, unsafe_allow_html=True)

    return opcion_feriados, fechas_feriados, cantidad_feriados

def _mostrar_calendario_feriados():
    """
    Muestra el calendario visual para seleccionar fechas específicas
    
    Returns:
        set: Conjunto de fechas completas (datetime.date) seleccionadas como feriados
    """
    # Selector de mes y año para el calendario
    col_mes, col_anio = st.columns(2)
    with col_mes:
        mes_seleccionado = st.selectbox(
            "Mes:",
            list(range(1, 13)),
            format_func=lambda x: datetime(2024, x, 1).strftime("%B"),
            index=datetime.now().month - 1
        )
    with col_anio:
        anio_seleccionado = st.selectbox(
            "Año:",
            list(range(2020, 2030)),
            index=list(range(2020, 2030)).index(datetime.now().year)
        )
    
    # Crear calendario visual
    cal = calendar.monthcalendar(anio_seleccionado, mes_seleccionado)
    
    st.markdown(f"**Calendario de {datetime(anio_seleccionado, mes_seleccionado, 1).strftime('%B %Y')}:**")
    st.markdown("Haz clic en los días que fueron feriados:")
    
    # Crear checkboxes para cada día del mes
    dias_mes = []
    for week in cal:
        for day in week:
            if day != 0:
                dias_mes.append(day)
    
    # Mostrar días en una grilla
    cols_por_fila = 7
    filas = [dias_mes[i:i + cols_por_fila] for i in range(0, len(dias_mes), cols_por_fila)]
    
    fechas_feriados_seleccionadas = []
    for fila in filas:
        cols = st.columns(7)
        for idx, dia in enumerate(fila):
            if idx < len(cols):
                with cols[idx]:
                    if st.checkbox(f"{dia}", key=f"dia_{dia}_{mes_seleccionado}_{anio_seleccionado}"):
                        # Crear fecha completa
                        fecha_completa = datetime(anio_seleccionado, mes_seleccionado, dia).date()
                        fechas_feriados_seleccionadas.append(fecha_completa)
    
    fechas_feriados = set(fechas_feriados_seleccionadas)
    
    if fechas_feriados:
        fechas_str = [fecha.strftime("%d/%m/%Y") for fecha in sorted(fechas_feriados)]
        st.success(f"Fechas feriados seleccionadas: {', '.join(fechas_str)}")
    
    return fechas_feriados

def mostrar_subida_archivo():
    """
    Muestra el widget de subida de archivo Excel o PDF con estilo mejorado
    
    Returns:
        tuple: (archivo_subido, tipo_archivo)
    """
    st.markdown("### Selecciona el tipo de archivo")
    
    # Selector de tipo de archivo con botones mejorados
    col1, col2 = st.columns(2)
    
    with col1:
        excel_selected = st.button("Archivo Excel", use_container_width=True, help="Datos estructurados tradicionales")
    
    with col2:
        pdf_selected = st.button("Archivo PDF", use_container_width=True, help="Procesamiento inteligente automático")
    
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
            <strong>Modo Excel Tradicional</strong><br>
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
            <strong>Modo Inteligente PDF Activado</strong><br>
            El sistema extraerá automáticamente la información de asistencia.
        </div>
        """, unsafe_allow_html=True)
        
        archivo = st.file_uploader(
            "Sube tu archivo PDF con datos de asistencia:",
            type=["pdf"],
            help="PDF con información de empleados y horarios. El sistema extraerá automáticamente nombres y horas.",
            key="pdf_uploader"
        )
        
        if archivo:
            st.markdown("""
            <div class="verification-container">
                <h4>Capacidades del Procesamiento Inteligente</h4>
                <div class="verification-step">Extrae automáticamente nombres de empleados</div>
                <div class="verification-step">Separa fechas y horas combinadas</div>
                <div class="verification-step">Detecta entrada y salida por contexto</div>
                <div class="verification-step">Agrupa datos por empleado/día</div>
                <div class="verification-step">Ignora columnas innecesarias</div>
            </div>
            """, unsafe_allow_html=True)
        
        return archivo, "pdf"

def mostrar_verificacion_detallada(resultados, valor_por_hora, fechas_feriados, porcentaje_extra=0.30):
    """
    Muestra un apartado de verificación detallada de cálculos
    
    Args:
        resultados: Lista de resultados de cálculos
        valor_por_hora: Valor por hora utilizado
        fechas_feriados: Set de fechas feriadas
        porcentaje_extra: Porcentaje de recargo para horas extra (como decimal)
    """
    if not resultados:
        return
    
    st.markdown("---")
    st.markdown("## **Verificación Detallada de Cálculos**")
    st.markdown("*Aquí puedes verificar paso a paso cómo se calculó cada día:*")
    
    # Selector de empleado y fecha para verificar
    empleados_disponibles = list(set([r["Empleado"] for r in resultados]))
    empleado_seleccionado = st.selectbox("Selecciona un empleado:", empleados_disponibles)
    
    # Filtrar resultados por empleado
    resultados_empleado = [r for r in resultados if r["Empleado"] == empleado_seleccionado]
    
    if resultados_empleado:
        fechas_disponibles = [r["Fecha"] for r in resultados_empleado]
        fecha_seleccionada = st.selectbox("Selecciona una fecha:", fechas_disponibles)
        
        # Encontrar el resultado específico
        resultado = next((r for r in resultados_empleado if r["Fecha"] == fecha_seleccionada), None)
        
        if resultado:
            _mostrar_calculo_detallado(resultado, valor_por_hora, fechas_feriados)

def _mostrar_calculo_detallado(resultado, valor_por_hora, fechas_feriados):
    """
    Muestra el cálculo detallado de un día específico usando lógica real
    """
    from datetime import datetime, timedelta
    from calculations import calcular_horas_especiales
    
    st.markdown("### **Desglose del Cálculo Real**")
    
    # Información básica
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Empleado", resultado["Empleado"])
    with col2:
        st.metric("Fecha", resultado["Fecha"])
    with col3:
        # Verificar si es feriado (corrigiendo el error)
        fecha_str = str(resultado["Fecha"])
        es_feriado = any(fecha_str in str(f) for f in fechas_feriados) if fechas_feriados else False
        st.metric("¿Feriado?", "Sí" if es_feriado else "No")
    
    # Horarios
    st.markdown("#### **Horarios Trabajados**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Entrada:** {resultado['Entrada']}")
    with col2:
        st.info(f"**Salida:** {resultado['Salida']}")
    with col3:
        st.info(f"**Total Horas:** {resultado.get('Horas Trabajadas (h:mm)', resultado.get('Horas Trabajadas', 'N/A'))}")
    
    # Calcular horas especiales usando la función REAL del sistema
    try:
        # Convertir entrada y salida a datetime para cálculo preciso
        fecha_resultado = str(resultado["Fecha"])
        if len(fecha_resultado) == 10:  # YYYY-MM-DD
            fecha_base = datetime.strptime(fecha_resultado, "%Y-%m-%d").date()
        else:  # Otros formatos
            fecha_base = datetime.now().date()
        
        entrada_str = str(resultado["Entrada"])
        salida_str = str(resultado["Salida"])
        
        # Parsear horas (formato HH:MM)
        entrada_dt = datetime.combine(fecha_base, datetime.strptime(entrada_str, "%H:%M").time())
        salida_dt = datetime.combine(fecha_base, datetime.strptime(salida_str, "%H:%M").time())
        
        # Si salida es menor que entrada, es del día siguiente
        if salida_dt < entrada_dt:
            salida_dt += timedelta(days=1)
        
        # Calcular horas especiales reales (20:00-22:00)
        horas_especiales_reales = calcular_horas_especiales(entrada_dt, salida_dt)
        
        # Calcular horas totales
        total_horas = (salida_dt - entrada_dt).total_seconds() / 3600
        horas_normales_reales = total_horas - horas_especiales_reales
        
        calculo_exitoso = True
        
    except Exception as e:
        # Fallback si hay problemas con el parsing
        calculo_exitoso = False
        # Buscar horas trabajadas con el nombre correcto de columna
        horas_str = resultado.get('Horas Trabajadas (h:mm)', resultado.get('Horas Trabajadas', '0:00'))
        if ':' in str(horas_str):
            try:
                h, m = str(horas_str).split(':')
                total_horas = float(h) + float(m) / 60
            except:
                total_horas = 0
        else:
            try:
                total_horas = float(horas_str)
            except:
                total_horas = 0
        
        # Estimación básica (no ideal, pero funcional)
        horas_especiales_reales = 0
        horas_normales_reales = total_horas
    
    # Desglose de cálculos
    st.markdown("#### **Análisis Detallado de Cálculos**")
    
    # Calcular componentes
    factor_feriado = 2.0 if es_feriado else 1.0
    
    # Cálculo preciso basado en el sistema real
    sueldo_normal = horas_normales_reales * valor_por_hora * factor_feriado
    # Cambiar 1.5 por 1 + porcentaje_extra para reflejar el porcentaje configurable  
    factor_extra = 1 + porcentaje_extra
    sueldo_especial = horas_especiales_reales * valor_por_hora * factor_feriado * factor_extra
    sueldo_bruto = sueldo_normal + sueldo_especial
    
    # Descuentos
    descuento_inv = resultado.get('Descuento Inventario', 0) or 0
    descuento_caja = resultado.get('Descuento Caja', 0) or 0
    retiro = resultado.get('Retiro', 0) or 0
    sueldo_final = sueldo_bruto - descuento_inv - descuento_caja - retiro
    
    # Mostrar cálculos paso a paso
    with st.expander("**Ver Cálculos Paso a Paso**", expanded=True):
        
        # Estado del cálculo
        if calculo_exitoso:
            st.success("**Cálculo basado en horarios reales del sistema**")
        else:
            st.warning("**Cálculo estimado** (no se pudieron analizar horarios precisos)")
        
        st.markdown("**Análisis de Horarios:**")
        st.code(f"""
Entrada original: {entrada_str}
Salida original: {salida_str}  
Total trabajado: {total_horas:.2f} horas = {int(total_horas)}h {int((total_horas % 1) * 60)}min
Horas normales: {horas_normales_reales:.2f} h
Horas especiales (20:00-22:00): {horas_especiales_reales:.2f} h
Factor feriado: {factor_feriado}x {'(DOBLE PAGO)' if es_feriado else '(día normal)'}
Valor hora base: ${valor_por_hora:,.0f}

DEBUG - Verificación manual:
   Desde {entrada_str} hasta {salida_str}
   Diferencia calculada: {total_horas:.4f} horas
        """)
        
        # Agregar verificación manual de horas
        if calculo_exitoso:
            diferencia_manual = (salida_dt - entrada_dt).total_seconds() / 3600
            st.code(f"""
VERIFICACIÓN MANUAL:
   Entrada: {entrada_dt.strftime('%Y-%m-%d %H:%M')}
   Salida:  {salida_dt.strftime('%Y-%m-%d %H:%M')}
   Diferencia: {diferencia_manual:.4f} horas = {int(diferencia_manual)}h {int((diferencia_manual % 1) * 60)}min
            """)
        
        st.markdown("**Cálculo de Sueldos:**")
        
        # Mostrar cálculo normal
        st.code(f"""
Sueldo Normal:
   {horas_normales_reales:.2f}h × ${valor_por_hora:,.0f} × {factor_feriado} = ${sueldo_normal:,.0f}
        """)
        
        # Mostrar cálculo especial solo si hay horas especiales
        if horas_especiales_reales > 0:
            st.code(f"""
Sueldo Especial (20:00-22:00 con {porcentaje_extra*100:.0f}% extra):
   {horas_especiales_reales:.2f}h × ${valor_por_hora:,.0f} × {factor_feriado} × {factor_extra:.2f} = ${sueldo_especial:,.0f}
            """)
        else:
            st.info("No hay horas especiales (20:00-22:00) en este día")
        
        st.code(f"""
Sueldo Bruto Total = ${sueldo_normal:,.0f} + ${sueldo_especial:,.0f} = ${sueldo_bruto:,.0f}
        """)
        
        # Descuentos si los hay
        if descuento_inv or descuento_caja or retiro:
            st.markdown("**Descuentos Aplicados:**")
            st.code(f"""
Descuento Inventario: ${descuento_inv:,.0f}
Descuento Caja: ${descuento_caja:,.0f}  
Retiro: ${retiro:,.0f}
Total descuentos: ${(descuento_inv + descuento_caja + retiro):,.0f}
            """)
        
        st.markdown("**Resultado Final:**")
        st.code(f"""
Sueldo Final = ${sueldo_bruto:,.0f} - ${(descuento_inv + descuento_caja + retiro):,.0f} = ${sueldo_final:,.0f}
        """)
    
    # Comparación con cálculo simple
    calculo_simple = total_horas * valor_por_hora
    diferencia = sueldo_final - calculo_simple
    
    st.markdown("#### **Comparación: Simple vs Real**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cálculo Simple", f"${calculo_simple:,.0f}", 
                 help=f"{total_horas:.2f}h × ${valor_por_hora:,.0f} = ${calculo_simple:,.0f}")
    with col2:
        st.metric("Cálculo Real", f"${sueldo_final:,.0f}")
    with col3:
        porcentaje = ((diferencia / calculo_simple) * 100) if calculo_simple > 0 else 0
        st.metric("Diferencia", f"${diferencia:,.0f}", delta=f"{porcentaje:+.1f}%")
    
    # Explicación detallada de la diferencia
    if abs(diferencia) > 1:  # Margen de $1 para evitar diferencias mínimas por redondeo
        st.markdown("#### **¿Por qué hay diferencia?**")
        
        factores_positivos = []
        factores_negativos = []
        
        if es_feriado:
            aumento_feriado = (total_horas * valor_por_hora * (factor_feriado - 1))
            factores_positivos.append(f"**Feriado (doble pago)**: +${aumento_feriado:,.0f}")
        
        if horas_especiales_reales > 0:
            aumento_especial = (horas_especiales_reales * valor_por_hora * factor_feriado * porcentaje_extra)
            factores_positivos.append(f"**Horas especiales** (20:00-22:00): +${aumento_especial:,.0f} ({horas_especiales_reales:.2f}h × {porcentaje_extra*100:.0f}% extra)")
        
        descuentos_total = descuento_inv + descuento_caja + retiro
        if descuentos_total > 0:
            factores_negativos.append(f"**Descuentos**: -${descuentos_total:,.0f}")
        
        # Mostrar factores
        for factor in factores_positivos:
            st.success(factor)
        for factor in factores_negativos:
            st.error(factor)
        
        if not factores_positivos and not factores_negativos:
            st.info("Las diferencias menores pueden deberse a redondeos en los cálculos.")
            
    else:
        st.info("**El cálculo simple coincide con el cálculo real** para este día.")
        
    # Mostrar ejemplo de tu escenario específico
    if horas_especiales_reales > 0 and es_feriado:
        st.markdown("---")
        st.markdown("#### **Ejemplo Detallado (como tu consulta)**")
        st.info(f"""
**Escenario:** {horas_normales_reales:.1f}h normales + {horas_especiales_reales:.1f}h especiales + feriado
        
• **Horas normales:** {horas_normales_reales:.1f}h × ${valor_por_hora:,.0f} × 2 (feriado) = ${sueldo_normal:,.0f}
• **Horas especiales:** {horas_especiales_reales:.1f}h × ${valor_por_hora:,.0f} × 2 (feriado) × {factor_extra:.2f} ({porcentaje_extra*100:.0f}% extra) = ${sueldo_especial:,.0f}
• **Total:** ${sueldo_bruto:,.0f}

**¡Exactamente como preguntaste!**
        """)