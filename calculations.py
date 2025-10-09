"""
Módulo de cálculos para la aplicación de sueldos
Contiene funciones para cálculo de horas y conversiones
"""
from datetime import datetime, timedelta

def calcular_horas_especiales(entrada_dt, salida_dt):
    """
    Calcula las horas especiales trabajadas entre 20:00 y 22:00
    
    Args:
        entrada_dt (datetime): Hora de entrada
        salida_dt (datetime): Hora de salida
    
    Returns:
        float: Horas especiales trabajadas
    """
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
    """
    Convierte horas decimales a formato horas:minutos
    
    Args:
        horas (float): Horas en formato decimal
    
    Returns:
        str: Horas en formato "HH:MM"
    """
    horas_int = int(horas)
    minutos = int(round((horas - horas_int) * 60))
    if minutos >= 60:
        horas_int += minutos // 60
        minutos = minutos % 60
    return f"{horas_int}:{minutos:02d}"