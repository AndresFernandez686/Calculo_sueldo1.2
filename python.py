import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

# Inicializar session_state
if "exit_app" not in st.session_state:
    st.session_state.exit_app = False

def calcular_horas_especiales(entrada_dt, salida_dt):
    inicio_especial = entrada_dt.replace(hour=20, minute=0, second=0)
    fin_especial = entrada_dt.replace(hour=22, minute=0, second=0)
    if salida_dt < entrada_dt:
        salida_dt += timedelta(days=1)
    inicio_interseccion = max(entrada_dt, inicio_especial)
    fin_interseccion = min(salida_dt, fin_especial)
    if inicio_interseccion >= fin_interseccion:
        return 0
    return (fin_interseccion - inicio_interseccion).total_seconds() / 3600

def horas_a_horasminutos(horas):
    horas_int = int(horas)
    minutos = int(round((horas - horas_int) * 60))
    if minutos >= 60:
        horas_int += minutos // 60
        minutos = minutos % 60
    return f"{horas_int}:{minutos:02d}"

st.set_page_config(page_title="Calculadora de Sueldos", page_icon="💼")

if st.session_state.exit_app:
    st.title("👋 Gracias por usar la Calculadora de Sueldos")
    st.success("La aplicación se ha cerrado correctamente. Puedes cerrar la pestaña.")
    st.stop()

st.title("💼 Calculadora de Sueldos - Feriados por Día del Mes")

st.markdown("**📄 Descarga la plantilla de Excel, complétala y vuelve a subirla aquí:**")
with open("plantilla_sueldos_feriados_dias.xlsx", "rb") as f:
    st.download_button("📥 Descargar Plantilla Excel", f, file_name="plantilla_sueldos_feriados_dias.xlsx")

valor_por_hora = st.number_input("💲 Ingrese el valor por hora:", min_value=0.0, value=11660.0)

dias_feriados_str = st.text_input("📅 Ingrese los días del mes que fueron feriados separados por comas (ej: 2, 15, 25):")
dias_feriados = set()
if dias_feriados_str:
    try:
        dias_lista = [int(d.strip()) for d in dias_feriados_str.split(",") if d.strip().isdigit()]
        dias_feriados = set(dias_lista)
        if len(dias_lista) != len(dias_feriados):
            st.warning("⚠️ Se han eliminado días feriados duplicados.")
    except:
        st.error("❌ Por favor ingresa solo números válidos separados por comas.")

uploaded_file = st.file_uploader("📤 Sube tu archivo Excel completado:", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    required_cols = ["Empleado", "Fecha", "Entrada", "Salida", "Descuento Inventario", "Descuento Caja", "Retiro"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ El archivo subido no contiene las siguientes columnas necesarias: {', '.join(missing_cols)}")
    else:
        resultados = []
        total_horas = 0
        total_sueldos = 0

        for idx, row in df.iterrows():
            try:
                fecha = pd.to_datetime(row["Fecha"])
                entrada = pd.to_datetime(str(row["Entrada"])).time()
                salida = pd.to_datetime(str(row["Salida"])).time()

                entrada_dt = datetime.combine(fecha, entrada)
                salida_dt = datetime.combine(fecha, salida)
                if salida_dt < entrada_dt:
                    salida_dt += timedelta(days=1)

                # ⚠️ Limitar la salida a las 22:00
                limite_salida = entrada_dt.replace(hour=22, minute=0, second=0)
                if salida_dt > limite_salida:
                    salida_dt = limite_salida

                horas_trabajadas = (salida_dt - entrada_dt).total_seconds() / 3600
                horas_especiales = calcular_horas_especiales(entrada_dt, salida_dt)
                horas_normales = horas_trabajadas - horas_especiales

                es_feriado = fecha.day in dias_feriados
                factor_feriado = 2 if es_feriado else 1

                sueldo_normal = horas_normales * valor_por_hora * factor_feriado
                recargo = horas_especiales * valor_por_hora * 0.30
                sueldo_especial = horas_especiales * valor_por_hora * factor_feriado + recargo
                sueldo_dia = sueldo_normal + sueldo_especial

                descuento_inventario = row["Descuento Inventario"] if not pd.isnull(row["Descuento Inventario"]) else 0
                descuento_caja = row["Descuento Caja"] if not pd.isnull(row["Descuento Caja"]) else 0
                retiro = row["Retiro"] if not pd.isnull(row["Retiro"]) else 0

                sueldo_final = sueldo_dia - descuento_inventario - descuento_caja - retiro

                resultados.append({
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
                })

                total_horas += horas_trabajadas
                total_sueldos += sueldo_final

            except Exception as e:
                st.error(f"❌ Error en la fila {idx+2}: {e}")

        df_result = pd.DataFrame(resultados)
        st.success("✅ Cálculo completado exitosamente.")
        st.dataframe(df_result)

        # Resumen visual final
        col1, col2 = st.columns(2)
        col1.metric("Total ⏱️ Horas Trabajadas", f"{horas_a_horasminutos(total_horas)} hs ({round(total_horas, 2)} dec)")
        col2.metric("💰 Total Sueldos Pagados", f"{round(total_sueldos, 2):,.0f} Gs.")

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

# Botón para salir de la app
st.markdown("---")
if st.button("🚪 Salir de la aplicación"):
    st.session_state.exit_app = True
    st.experimental_rerun()
