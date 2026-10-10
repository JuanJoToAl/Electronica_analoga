from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE USUARIO (Modifica estas variables)
# ==============================================================================
# Archivo principal (ej. Salida del rectificador o sujetador)
ARCHIVO_1 = "fuente dc salida.csv"

# Segundo archivo opcional (ej. Señal de entrada). Déjalo como None si no lo usas.
# ARCHIVO_2 = "entrada_transformador.csv"
ARCHIVO_2 = None 

# Título de la gráfica
TITULO_GRAFICA = "Respuesta Experimental - Rectificador de Onda Completa"
# ==============================================================================

def leer_datos_osciloscopio(ruta):
    """
    Lee el CSV del osciloscopio. Los osciloscopios (Rigol, Siglent, Tektronix) 
    a veces incluyen metadatos en las primeras líneas. Si tu archivo da error,
    puedes añadir el parámetro 'skiprows=2' (o las líneas que sobren) en read_csv.
    """
    try:
        # Cargamos el CSV. Se asume que la columna 0 es tiempo y la 1 es voltaje.
        df = pd.read_csv(ruta)
        # Limpieza de los nombres de las columnas por si hay espacios invisibles
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error al leer '{ruta}': {e}")
        return None

def graficar_senales():
    _, ax = plt.subplots(figsize=(10, 5), dpi=120)

    carpeta_script = Path(__file__).resolve().parent
    archivos = [ARCHIVO_1, ARCHIVO_2]
    # Colores clásicos: Amarillo/Naranja (Ch1 típico) y Azul/Cian (Ch2 típico)
    colores = ['#ff7f0e', '#1f77b4'] 
    
    hay_datos = False
    unidad_tiempo = "s"

    for i, archivo in enumerate(archivos):
        if not archivo:
            continue

        ruta_archivo = Path(archivo)
        if not ruta_archivo.is_absolute():
            ruta_archivo = carpeta_script / ruta_archivo

        if ruta_archivo.exists():
            df = leer_datos_osciloscopio(ruta_archivo)
            
            if df is not None and not df.empty:
                # Extraemos las dos primeras columnas dinámicamente
                col_t = df.columns[0]
                col_v = df.columns[1]
                
                tiempo = df[col_t].values
                voltaje = df[col_v].values
                
                # Auto-escalado de tiempo basado en el valor máximo absoluto
                max_t = max(abs(tiempo))
                if max_t < 1e-3:
                    tiempo = tiempo * 1e6
                    unidad_tiempo = "µs"
                elif max_t < 1.0:
                    tiempo = tiempo * 1e3
                    unidad_tiempo = "ms"
                    
                ax.plot(tiempo, voltaje, label=f"Señal {i+1}: {archivo}",
                        color=colores[i], linewidth=1.8, alpha=0.9)
                hay_datos = True
        else:
            print(f"Advertencia: No se encontró el archivo '{ruta_archivo}'.")

    if hay_datos:
        ax.set_title(TITULO_GRAFICA, fontsize=14, fontweight="bold", pad=12)
        ax.set_xlabel(f"Tiempo [{unidad_tiempo}]", fontsize=11)
        ax.set_ylabel("Tensión [V]", fontsize=11)
        
        # Estética de rejilla y leyenda
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="none")
        
        # Establece el eje Y en 0 visualmente si trabajamos con AC acoplada o rectificadores
        ax.axhline(0, color='black', linewidth=0.8, alpha=0.5)

        plt.tight_layout()
        plt.show()
    else:
        print("No se graficó nada. Verifica los nombres de los archivos y que estén en la misma carpeta que el script.")

if __name__ == "__main__":
    graficar_senales()