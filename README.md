# 💼 Sistema de Cálculo de Sueldos - Streamlit

Sistema profesional para el cálculo automatizado de sueldos de empleados con soporte para archivos Excel y PDF. Desarrollado con Streamlit para una interfaz web moderna e intuitiva.

## 🚀 Características Principales

### ✨ Procesamiento Dual de Archivos
- **📊 Modo Excel**: Procesamiento tradicional con plantilla estructurada
- **🤖 Modo PDF Inteligente**: Extracción automática de datos usando IA

### 💰 Cálculos Avanzados
- **Horas normales**: Cálculo estándar por hora trabajada
- **Horas especiales**: Recargo configurable para horario 20:00-22:00 (default 30%)
- **Feriados**: Doble pago automático para días festivos
- **Descuentos**: Inventario, caja y retiros personalizados

### 🎯 Funciones Inteligentes
- **Detección de marcaciones incompletas**: Identifica y permite corregir días con datos faltantes
- **Verificación detallada**: Análisis paso a paso de cada cálculo
- **Calendario visual**: Selección intuitiva de fechas feriadas
- **Configuración flexible**: Porcentajes de recargo personalizables

## 📋 Requisitos

- Python 3.8+
- Streamlit
- pandas
- pdfplumber (para procesamiento PDF)
- openpyxl (para archivos Excel)

## 🔧 Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/AndresFernandez686/Calculo_sueldo1.2.git
cd Calculo_sueldo1.2
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**:
```bash
streamlit run main.py
```

## 📖 Guía de Uso

### 1. Configuración Inicial
1. **Valor por hora**: Establecer el valor base en Guaraníes
2. **Porcentaje horas extra**: Configurar recargo para horario 20:00-22:00
3. **Feriados**: Seleccionar fechas usando el calendario visual

### 2. Procesamiento de Datos

#### Modo Excel
1. Descargar la plantilla Excel incluida
2. Completar con datos de empleados:
   - Empleado, Fecha, Entrada, Salida
   - Descuento Inventario, Descuento Caja, Retiro
3. Subir archivo completado

#### Modo PDF Inteligente
1. Subir PDF con datos de asistencia
2. El sistema extrae automáticamente:
   - Nombres de empleados
   - Fechas y horarios
   - Entrada y salida por contexto

### 3. Corrección de Datos
- **Marcaciones incompletas**: El sistema detecta días con datos faltantes
- **Corrección manual**: Interface para completar horas faltantes
- **Validación**: Verificación antes del cálculo final

### 4. Resultados
- **Tabla detallada**: Todos los cálculos por empleado/día
- **Resumen general**: Totales de horas y sueldos
- **Verificación paso a paso**: Análisis detallado de cualquier día

## 🏗️ Arquitectura del Proyecto

```
├── main.py                 # Aplicación principal Streamlit
├── calculations.py         # Lógica de cálculos de sueldos
├── data_processor.py       # Procesamiento de datos Excel
├── pdf_processor.py        # Procesamiento inteligente PDF
├── smart_parser.py         # Parser avanzado para PDF
├── ui_components.py        # Componentes de interfaz
├── styles.css             # Estilos personalizados
├── plantilla_sueldos_feriados_dias.xlsx  # Plantilla Excel
└── requirements.txt        # Dependencias Python
```

## 🔍 Funciones Técnicas Destacadas

### Detección Inteligente PDF
- **Extracción de nombres**: Reconocimiento automático de empleados
- **Parsing de fechas**: Manejo de múltiples formatos
- **Detección de horarios**: Identificación de entrada/salida por contexto
- **Agrupación inteligente**: Consolidación por empleado/día

### Validación de Datos
- **Marcaciones incompletas**: Algoritmo de detección de datos faltantes
- **Corrección interactiva**: Interface para completar información
- **Verificación cruzada**: Validación de consistencia de datos

### Cálculos Precisos
- **Horas especiales**: Cálculo exacto para rango 20:00-22:00
- **Factores configurables**: Porcentajes personalizables
- **Manejo de feriados**: Aplicación automática de doble pago
- **Descuentos múltiples**: Soporte para varios tipos de deducciones

## ⚙️ Configuración Avanzada

### Personalización de Recargos
```python
# En ui_components.py
porcentaje_extra = mostrar_input_porcentaje_extra()  # 0-200%
```

### Modificación de Horarios Especiales
```python
# En calculations.py
def calcular_horas_especiales(entrada, salida):
    # Modificar rango de horas especiales aquí
    hora_inicio_especial = 20  # 8:00 PM
    hora_fin_especial = 22     # 10:00 PM
```

## 🐛 Resolución de Problemas

### Error: "No se encontró la plantilla"
- Verificar que `plantilla_sueldos_feriados_dias.xlsx` esté en el directorio raíz

### Error de procesamiento PDF
- Instalar pdfplumber: `pip install pdfplumber`
- Verificar que el PDF contenga texto extraíble

### Marcaciones incompletas
- Usar la interface de corrección manual
- Verificar formato de horas (HH:MM)

## 🤝 Contribuciones

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Andrés Fernández** - [GitHub](https://github.com/AndresFernandez686)

## 🙏 Agradecimientos

- Comunidad Streamlit por la excelente framework
- Usuarios beta por feedback y testing
- Contribuidores del proyecto

---

⭐ **¡Si este proyecto te es útil, considera darle una estrella!** ⭐