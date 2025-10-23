"""
Módulo de procesamiento de datos
Contiene funciones para procesar archivos Excel y calcular sueldos
"""
import pandas as pd
import streamlit as st
import io
from datetime import datetime, timedelta
from calculations import calcular_horas_especiales, horas_a_horasminutos

def validar_archivo_excel(df):
    """
    Valida que el archivo Excel contenga las columnas necesarias
    
    Args:
        df (DataFrame): DataFrame del archivo Excel
        
    Returns:
        tuple: (es_valido, columnas_faltantes)
    """
    required_cols = ["Empleado", "Fecha", "Entrada", "Salida", "Descuento Inventario", "Descuento Caja", "Retiro"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    return len(missing_cols) == 0, missing_cols

def procesar_datos_excel(df, valor_por_hora, opcion_feriados, fechas_feriados, cantidad_feriados):
    """
    Procesa los datos del Excel y calcula los sueldos
    
    Args:
        df (DataFrame): DataFrame con los datos
        valor_por_hora (float): Valor por hora de trabajo
        opcion_feriados (str): Tipo de configuración de feriados (no usado, solo fechas específicas)
        fechas_feriados (set): Fechas completas específicas de feriados
        cantidad_feriados (int): No usado, mantener por compatibilidad
        
    Returns:
        tuple: (resultados, total_horas, total_sueldos)
    """
    resultados = []
    total_horas = 0
    total_sueldos = 0

    for idx, row in df.iterrows():
        try:
            resultado_fila = _procesar_fila(row, idx, valor_por_hora, fechas_feriados)
            
            if resultado_fila:
                resultados.append(resultado_fila["datos"])
                total_horas += resultado_fila["horas"]
                total_sueldos += resultado_fila["sueldo"]

        except Exception as e:
            st.error(f"❌ Error en la fila {idx+2}: {e}")

    return resultados, total_horas, total_sueldos

def _procesar_fila(row, idx, valor_por_hora, fechas_feriados):
    """
    Procesa una fila individual del Excel con lógica completa:
    - Horas normales × tarifa
    - Horas especiales (20:00-22:00) × tarifa × 1.3
    - Factor de feriado ×2 si aplica
    
    Args:
        row: Fila del DataFrame
        idx: Índice de la fila
        valor_por_hora: Valor por hora
        fechas_feriados: Fechas completas específicas de feriados
        
    Returns:
        dict: Resultado del procesamiento de la fila
    """
    fecha = pd.to_datetime(row["Fecha"])
    entrada = pd.to_datetime(str(row["Entrada"])).time()
    salida = pd.to_datetime(str(row["Salida"])).time()

    entrada_dt = datetime.combine(fecha, entrada)
    salida_dt = datetime.combine(fecha, salida)
    if salida_dt < entrada_dt:
        salida_dt += timedelta(days=1)

    # Calcular horas trabajadas en decimal
    horas_trabajadas_decimal = (salida_dt - entrada_dt).total_seconds() / 3600

    # Calcular horas especiales (20:00-22:00 con 30% extra)
    horas_normales, horas_especiales = calcular_horas_especiales(entrada_dt, salida_dt)
    
    # Comparar la fecha completa (año-mes-día) con las fechas de feriados seleccionadas
    es_feriado = fecha.date() in fechas_feriados
    
    # Factor de feriado: 2x si es feriado, 1x si no lo es
    factor_feriado = 2 if es_feriado else 1

    # Cálculo con horas normales y especiales
    sueldo_normal = horas_normales * valor_por_hora
    sueldo_especial = horas_especiales * valor_por_hora * 1.3  # 30% extra para horas especiales
    sueldo_bruto = (sueldo_normal + sueldo_especial) * factor_feriado

    # Aplicar descuentos
    descuento_inventario = row["Descuento Inventario"] if not pd.isnull(row["Descuento Inventario"]) else 0
    descuento_caja = row["Descuento Caja"] if not pd.isnull(row["Descuento Caja"]) else 0
    retiro = row["Retiro"] if not pd.isnull(row["Retiro"]) else 0

    sueldo_final = sueldo_bruto - descuento_inventario - descuento_caja - retiro

    datos_fila = {
        "Empleado": row["Empleado"],
        "Fecha": fecha.strftime("%Y-%m-%d"),
        "Entrada": entrada.strftime("%H:%M"),
        "Salida": salida.strftime("%H:%M"),
        "Feriado": "Sí" if es_feriado else "No",
        "Horas Trabajadas (h:mm)": horas_a_horasminutos(horas_trabajadas_decimal),
        "Horas Normales": horas_a_horasminutos(horas_normales),
        "Horas Especiales": horas_a_horasminutos(horas_especiales),
        "Descuento Inventario": descuento_inventario,
        "Descuento Caja": descuento_caja,
        "Retiro": retiro,
        "Sueldo Final": round(sueldo_final, 2)
    }

    return {
        "datos": datos_fila,
        "horas": horas_trabajadas_decimal,
        "sueldo": sueldo_final
    }

def mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora=None, fechas_feriados=None, nombre_archivo=None):
    """
    Muestra los resultados en la interfaz y proporciona descarga
    
    Args:
        resultados (list): Lista de resultados procesados
        total_horas (float): Total de horas trabajadas
        total_sueldos (float): Total de sueldos calculados
        valor_por_hora (float): Valor por hora utilizado en cálculos
        fechas_feriados (set): Fechas marcadas como feriados
        nombre_archivo (str): Nombre base para el archivo Excel (opcional)
    """
    df_result = pd.DataFrame(resultados)
    
    # Mensaje de éxito con estilo
    st.markdown("""
    <div class="custom-alert alert-success">
        <h3>✅ Cálculo completado exitosamente</h3>
        <p>Los sueldos han sido procesados correctamente. Revisa los resultados a continuación.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar tabla con estilo
    st.markdown("### 📊 Resultados del Cálculo")
    st.dataframe(df_result, use_container_width=True)

    # Resumen visual final con métricas mejoradas
    st.markdown("### 📈 Resumen General")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Registros</div>
            <div class="metric-value">{len(df_result)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Horas</div>
            <div class="metric-value">{horas_a_horasminutos(total_horas)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Sueldos</div>
            <div class="metric-value">${round(total_sueldos, 2):,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Descargar Excel final
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False)
    
    # Generar nombre del archivo dinámico
    if nombre_archivo:
        # Limpiar nombre del archivo (remover extensión .pdf si existe)
        nombre_base = nombre_archivo.replace('.pdf', '').replace('.PDF', '')
        nombre_excel = f"{nombre_base}_calculado.xlsx"
    else:
        nombre_excel = "sueldos_calculados.xlsx"
    
    st.download_button(
        "📥 Descargar Reporte Final en Excel",
        data=output.getvalue(),
        file_name=nombre_excel,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )