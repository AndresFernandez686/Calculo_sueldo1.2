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

def detectar_marcaciones_incompletas(df):
    """
    Detecta días donde faltan marcaciones de entrada o salida
    
    Args:
        df (DataFrame): DataFrame con los datos
        
    Returns:
        list: Lista de diccionarios con información de días incompletos
    """
    dias_incompletos = []
    
    for idx, row in df.iterrows():
        empleado = row["Empleado"]
        fecha = pd.to_datetime(row["Fecha"])
        entrada = row["Entrada"]
        salida = row["Salida"]
        
        # Verificar si entrada o salida están vacías, son NaN o contienen valores inválidos
        entrada_vacia = (pd.isnull(entrada) or 
                        str(entrada).strip() == "" or 
                        str(entrada).lower() in ['nan', 'nat', 'none', 'null'] or
                        entrada is None)
        
        salida_vacia = (pd.isnull(salida) or 
                       str(salida).strip() == "" or 
                       str(salida).lower() in ['nan', 'nat', 'none', 'null'] or
                       salida is None)
        
        if entrada_vacia or salida_vacia:
            tipo_faltante = []
            if entrada_vacia:
                tipo_faltante.append("Entrada")
            if salida_vacia:
                tipo_faltante.append("Salida")
            
            dias_incompletos.append({
                "indice": idx,
                "empleado": empleado,
                "fecha": fecha.strftime("%Y-%m-%d"),
                "fecha_formateada": fecha.strftime("%d/%m/%Y"),
                "entrada": entrada if not entrada_vacia else None,
                "salida": salida if not salida_vacia else None,
                "tipo_faltante": tipo_faltante,
                "descripcion_faltante": " y ".join(tipo_faltante)
            })
    
    return dias_incompletos

def mostrar_dias_incompletos(dias_incompletos):
    """
    Muestra los días con marcaciones incompletas y permite al usuario completarlos
    
    Args:
        dias_incompletos (list): Lista de días incompletos
        
    Returns:
        dict: Diccionario con las correcciones del usuario
    """
    if not dias_incompletos:
        return {}
    
    st.markdown("""
    <div class="custom-alert alert-warning">
        <h3>Marcaciones Incompletas Detectadas</h3>
        <p>Se encontraron días donde falta información de entrada o salida. Estos días no se incluirán en el cálculo hasta que proporciones la información faltante.</p>
    </div>
    """, unsafe_allow_html=True)
    
    correcciones = {}
    
    # Mostrar tabla de días incompletos
    st.markdown("### Días con Marcaciones Incompletas")
    
    # Crear DataFrame para mostrar
    df_incompletos = pd.DataFrame([{
        "Empleado": dia["empleado"],
        "Fecha": dia["fecha_formateada"],
        "Entrada": dia["entrada"] if dia["entrada"] else "FALTA",
        "Salida": dia["salida"] if dia["salida"] else "FALTA",
        "Información Faltante": dia["descripcion_faltante"]
    } for dia in dias_incompletos])
    
    st.dataframe(df_incompletos, use_container_width=True)
    
    # Permitir al usuario completar la información
    st.markdown("### Completar Información Faltante")
    st.markdown("Proporciona las horas faltantes para incluir estos días en el cálculo:")
    
    for i, dia in enumerate(dias_incompletos):
        with st.expander(f"{dia['empleado']} - {dia['fecha_formateada']} (Falta: {dia['descripcion_faltante']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                if "Entrada" in dia["tipo_faltante"]:
                    entrada_corregida = st.time_input(
                        f"Hora de Entrada",
                        key=f"entrada_{dia['indice']}",
                        help="Ingresa la hora de entrada para este día"
                    )
                    if entrada_corregida:
                        if dia["indice"] not in correcciones:
                            correcciones[dia["indice"]] = {}
                        correcciones[dia["indice"]]["entrada"] = entrada_corregida
                else:
                    st.info(f"Entrada ya registrada: {dia['entrada']}")
            
            with col2:
                if "Salida" in dia["tipo_faltante"]:
                    salida_corregida = st.time_input(
                        f"Hora de Salida",
                        key=f"salida_{dia['indice']}",
                        help="Ingresa la hora de salida para este día"
                    )
                    if salida_corregida:
                        if dia["indice"] not in correcciones:
                            correcciones[dia["indice"]] = {}
                        correcciones[dia["indice"]]["salida"] = salida_corregida
                else:
                    st.info(f"Salida ya registrada: {dia['salida']}")
    
    return correcciones

def aplicar_correcciones_dataframe(df, correcciones):
    """
    Aplica las correcciones proporcionadas por el usuario al DataFrame
    
    Args:
        df (DataFrame): DataFrame original
        correcciones (dict): Diccionario con las correcciones
        
    Returns:
        DataFrame: DataFrame corregido
    """
    df_corregido = df.copy()
    
    for indice, correccion in correcciones.items():
        if "entrada" in correccion:
            df_corregido.at[indice, "Entrada"] = correccion["entrada"]
        if "salida" in correccion:
            df_corregido.at[indice, "Salida"] = correccion["salida"]
    
    return df_corregido

def procesar_datos_excel(df, valor_por_hora, opcion_feriados, fechas_feriados, cantidad_feriados, porcentaje_extra=0.30):
    """
    Procesa los datos del Excel y calcula los sueldos
    
    Args:
        df (DataFrame): DataFrame con los datos
        valor_por_hora (float): Valor por hora de trabajo
        opcion_feriados (str): Tipo de configuración de feriados (no usado, solo fechas específicas)
        fechas_feriados (set): Fechas completas específicas de feriados
        cantidad_feriados (int): No usado, mantener por compatibilidad
        porcentaje_extra (float): Porcentaje de recargo para horas extra (como decimal, ej: 0.30 para 30%)
        
    Returns:
        tuple: (resultados, total_horas, total_sueldos, dias_incompletos, correcciones_aplicadas)
    """
    # Detectar marcaciones incompletas
    dias_incompletos = detectar_marcaciones_incompletas(df)
    
    # Si hay días incompletos, mostrar la interfaz para completarlos
    correcciones = {}
    if dias_incompletos:
        correcciones = mostrar_dias_incompletos(dias_incompletos)
        
        # Si no se han proporcionado todas las correcciones, detener el procesamiento
        dias_sin_corregir = []
        for dia in dias_incompletos:
            indice = dia["indice"]
            if indice not in correcciones:
                dias_sin_corregir.append(dia)
            else:
                # Verificar que se hayan proporcionado todas las correcciones necesarias
                correccion = correcciones[indice]
                if "Entrada" in dia["tipo_faltante"] and "entrada" not in correccion:
                    dias_sin_corregir.append(dia)
                if "Salida" in dia["tipo_faltante"] and "salida" not in correccion:
                    dias_sin_corregir.append(dia)
        
        if dias_sin_corregir:
            st.markdown(f"""
            <div class="custom-alert alert-info">
                <h4>⏳ Esperando Información Faltante</h4>
                <p>Hay {len(dias_sin_corregir)} día(s) que aún necesitan información de entrada o salida.</p>
                <p>El cálculo se realizará automáticamente cuando proporciones toda la información faltante.</p>
            </div>
            """, unsafe_allow_html=True)
            return [], 0, 0, dias_incompletos, {}
        
        # Aplicar correcciones al DataFrame
        if correcciones:
            df = aplicar_correcciones_dataframe(df, correcciones)
            st.markdown("""
            <div class="custom-alert alert-success">
                <h4>Correcciones Aplicadas</h4>
                <p>Se han aplicado las correcciones proporcionadas. Procediendo con el cálculo...</p>
            </div>
            """, unsafe_allow_html=True)
    
    resultados = []
    total_horas = 0
    total_sueldos = 0

    for idx, row in df.iterrows():
        try:
            resultado_fila = _procesar_fila(row, idx, valor_por_hora, fechas_feriados, porcentaje_extra)
            
            if resultado_fila:
                resultados.append(resultado_fila["datos"])
                total_horas += resultado_fila["horas"]
                total_sueldos += resultado_fila["sueldo"]

        except Exception as e:
            st.error(f"Error en la fila {idx+2}: {e}")

    return resultados, total_horas, total_sueldos, dias_incompletos, correcciones

def _procesar_fila(row, idx, valor_por_hora, fechas_feriados, porcentaje_extra=0.30):
    """
    Procesa una fila individual del Excel
    
    Args:
        row: Fila del DataFrame
        idx: Índice de la fila
        valor_por_hora: Valor por hora
        fechas_feriados: Fechas completas específicas de feriados
        porcentaje_extra: Porcentaje de recargo para horas extra (como decimal)
        
    Returns:
        dict: Resultado del procesamiento de la fila
    """
    try:
        fecha = pd.to_datetime(row["Fecha"])
        entrada = pd.to_datetime(str(row["Entrada"])).time()
        salida = pd.to_datetime(str(row["Salida"])).time()

        entrada_dt = datetime.combine(fecha, entrada)
        salida_dt = datetime.combine(fecha, salida)
        if salida_dt < entrada_dt:
            salida_dt += timedelta(days=1)

        # Limitar la salida a las 22:00
        limite_salida = entrada_dt.replace(hour=22, minute=0, second=0)
        if salida_dt > limite_salida:
            salida_dt = limite_salida

        horas_trabajadas = (salida_dt - entrada_dt).total_seconds() / 3600
        horas_especiales = calcular_horas_especiales(entrada_dt, salida_dt)
        horas_normales = horas_trabajadas - horas_especiales

        # Comparar la fecha completa (año-mes-día) con las fechas de feriados seleccionadas
        es_feriado = fecha.date() in fechas_feriados
        
        factor_feriado = 2 if es_feriado else 1

        sueldo_normal = horas_normales * valor_por_hora * factor_feriado
        recargo = horas_especiales * valor_por_hora * porcentaje_extra
        sueldo_especial = horas_especiales * valor_por_hora * factor_feriado + recargo
        sueldo_dia = sueldo_normal + sueldo_especial

        descuento_inventario = row["Descuento Inventario"] if not pd.isnull(row["Descuento Inventario"]) else 0
        descuento_caja = row["Descuento Caja"] if not pd.isnull(row["Descuento Caja"]) else 0
        retiro = row["Retiro"] if not pd.isnull(row["Retiro"]) else 0

        sueldo_final = sueldo_dia - descuento_inventario - descuento_caja - retiro

        datos_fila = {
            "Empleado": row["Empleado"],
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Entrada": entrada.strftime("%H:%M"),
            "Salida": salida.strftime("%H:%M"),
            "Feriado": "Sí" if es_feriado else "No",
            "Horas Trabajadas (h:mm)": horas_a_horasminutos(horas_trabajadas),
            "Horas Especiales": round(horas_especiales, 2),
            "Descuento Inventario": descuento_inventario,
            "Descuento Caja": descuento_caja,
            "Retiro": retiro,
            "Sueldo Final": round(sueldo_final, 2)
        }

        return {
            "datos": datos_fila,
            "horas": horas_trabajadas,
            "sueldo": sueldo_final
        }
    
    except Exception as e:
        # Si hay error en el procesamiento, devolver None para que se salte esta fila
        st.warning(f"Fila {idx+2} omitida debido a datos inválidos: {str(e)}")
        return None

    sueldo_final = sueldo_dia - descuento_inventario - descuento_caja - retiro

    datos_fila = {
        "Empleado": row["Empleado"],
        "Fecha": fecha.strftime("%Y-%m-%d"),
        "Entrada": entrada.strftime("%H:%M"),
        "Salida": salida.strftime("%H:%M"),
        "Feriado": "Sí" if es_feriado else "No",
        "Horas Trabajadas (h:mm)": horas_a_horasminutos(horas_trabajadas),
        "Horas Especiales": round(horas_especiales, 2),
        "Descuento Inventario": descuento_inventario,
        "Descuento Caja": descuento_caja,
        "Retiro": retiro,
        "Sueldo Final": round(sueldo_final, 2)
    }

    return {
        "datos": datos_fila,
        "horas": horas_trabajadas,
        "sueldo": sueldo_final
    }

def mostrar_resultados(resultados, total_horas, total_sueldos, valor_por_hora=None, fechas_feriados=None, porcentaje_extra=0.30):
    """
    Muestra los resultados en la interfaz y proporciona descarga
    
    Args:
        resultados (list): Lista de resultados procesados
        total_horas (float): Total de horas trabajadas
        total_sueldos (float): Total de sueldos calculados
        valor_por_hora (float): Valor por hora utilizado en cálculos
        fechas_feriados (set): Fechas marcadas como feriados
        porcentaje_extra (float): Porcentaje de recargo para horas extra
    """
    from ui_components import mostrar_verificacion_detallada
    
    df_result = pd.DataFrame(resultados)
    
    # Mensaje de éxito con estilo
    st.markdown("""
    <div class="custom-alert alert-success">
        <h3>Cálculo completado exitosamente</h3>
        <p>Los sueldos han sido procesados correctamente. Revisa los resultados a continuación.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar tabla con estilo
    st.markdown("### Resultados del Cálculo")
    st.dataframe(df_result, use_container_width=True)

    # Resumen visual final con métricas mejoradas
    st.markdown("### Resumen General")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Empleados</div>
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
    st.download_button(
        "📥 Descargar Reporte Final en Excel",
        data=output.getvalue(),
        file_name="sueldos_calculados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Mostrar verificación detallada
    if valor_por_hora and resultados:
        mostrar_verificacion_detallada(resultados, valor_por_hora, fechas_feriados, porcentaje_extra)