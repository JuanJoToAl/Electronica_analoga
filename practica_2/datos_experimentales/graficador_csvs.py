from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE USUARIO (Modifica estas variables)
# ==============================================================================
# Archivo principal (ej. Salida del rectificador o sujetador)
ARCHIVO_1 = "salida sujetador 3VDC.csv"

# Segundo archivo opcional (ej. Señal de entrada). Déjalo como None si no lo usas.
# ARCHIVO_2 = "entrada_transformador.csv"
ARCHIVO_2 = "entrada sujetador 12vpp.csv"

# Título de la gráfica
TITULO_GRAFICA = "Respuesta Experimental - Sujetador 3VDC"
ALINEAR_SENALES = True
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
        if len(df.columns) < 2:
            raise ValueError("el archivo debe contener al menos dos columnas")

        # Evita que texto, filas vacías o metadatos mal interpretados desplacen
        # las muestras al convertirlas en coordenadas para la gráfica.
        df = df.iloc[:, :2].copy()
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors="coerce")
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors="coerce")
        df = df.dropna().sort_values(df.columns[0])
        return df
    except Exception as e:
        print(f"Error al leer '{ruta}': {e}")
        return None


def estimar_desplazamiento_temporal(tiempo_referencia, voltaje_referencia,
                                    tiempo_objetivo, voltaje_objetivo):
    """Estima el desplazamiento del objetivo respecto a la referencia.

    Devuelve un desplazamiento en segundos que se suma al tiempo del objetivo.
    Un valor positivo desplaza el objetivo hacia la derecha.
    """
    inicio = max(tiempo_referencia.min(), tiempo_objetivo.min())
    fin = min(tiempo_referencia.max(), tiempo_objetivo.max())
    if inicio >= fin:
        raise ValueError("las señales no tienen un intervalo de tiempo común")

    pasos = [np.median(np.diff(tiempo_referencia)),
             np.median(np.diff(tiempo_objetivo))]
    paso = max(pasos)
    cantidad = int((fin - inicio) / paso) + 1
    if cantidad < 3:
        raise ValueError("no hay suficientes muestras para alinear las señales")

    tiempo_comun = np.linspace(inicio, fin, cantidad)
    referencia = np.interp(
        tiempo_comun, tiempo_referencia, voltaje_referencia
    )
    objetivo = np.interp(tiempo_comun, tiempo_objetivo, voltaje_objetivo)

    # El rectificador produce |Vin|. Probar esta forma evita que la
    # correlación falle aunque las capturas provengan de circuitos distintos.
    referencias = [referencia, np.abs(referencia)]
    mejor_correlacion = -np.inf
    mejor_desplazamiento = 0
    # Evita que una señal periódica coincida con un ciclo lejano usando un
    # solapamiento pequeño. La alineación está pensada para desfases de captura
    # y exige que al menos el 75 % de la ventana permanezca superpuesta.
    minimo_solapamiento = max(3, int(cantidad * 0.75))

    for referencia_transformada in referencias:
        ref = referencia_transformada - referencia_transformada.mean()
        for desplazamiento in range(-cantidad + minimo_solapamiento,
                                   cantidad - minimo_solapamiento + 1):
            if desplazamiento >= 0:
                ref_solapada = ref[:cantidad - desplazamiento]
                obj_solapado = objetivo[desplazamiento:]
            else:
                ref_solapada = ref[-desplazamiento:]
                obj_solapado = objetivo[:cantidad + desplazamiento]

            obj_solapado = obj_solapado - obj_solapado.mean()
            denominador = (np.linalg.norm(ref_solapada)
                           * np.linalg.norm(obj_solapado))
            if denominador == 0:
                continue

            correlacion = np.dot(ref_solapada, obj_solapado) / denominador
            misma_correlacion = (
                np.isfinite(mejor_correlacion)
                and abs(correlacion - mejor_correlacion) <= 1e-6
            )
            if (correlacion > mejor_correlacion
                    or (misma_correlacion
                        and abs(desplazamiento)
                        < abs(mejor_desplazamiento))):
                mejor_correlacion = correlacion
                mejor_desplazamiento = desplazamiento

    if not np.isfinite(mejor_correlacion):
        raise ValueError("no se pudo calcular una correlación válida")

    # La correlación compara referencia[t] con objetivo[t + desplazamiento].
    # Para que ambas muestras queden en la misma coordenada, el eje del
    # objetivo debe trasladarse en la dirección contraria.
    return -mejor_desplazamiento * paso


def graficar_senales():
    _, ax = plt.subplots(figsize=(10, 5), dpi=120)

    carpeta_script = Path(__file__).resolve().parent
    archivos = [ARCHIVO_1, ARCHIVO_2]
    # Colores clásicos: Amarillo/Naranja (Ch1 típico) y Azul/Cian (Ch2 típico)
    colores = ['#ff7f0e', '#1f77b4'] 
    
    hay_datos = False
    senales = []

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

                senales.append(
                    (
                        df[col_t].to_numpy(dtype=float),
                        df[col_v].to_numpy(dtype=float),
                        Path(archivo).stem,
                        colores[i],
                    )
                )
        else:
            print(f"Advertencia: No se encontró el archivo '{ruta_archivo}'.")

    if senales:
        # La unidad y el factor deben ser comunes: aplicar el auto-escalado
        # dentro del bucle deformaba la posición horizontal de cada señal.
        max_t = max(max(abs(tiempo)) for tiempo, _, _, _ in senales)
        if max_t < 1e-3:
            factor_tiempo, unidad_tiempo = 1e6, "µs"
        elif max_t < 1.0:
            factor_tiempo, unidad_tiempo = 1e3, "ms"
        else:
            factor_tiempo, unidad_tiempo = 1.0, "s"

        if ALINEAR_SENALES and len(senales) > 1:
            tiempo_referencia, voltaje_referencia, _, _ = senales[0]
            for indice in range(1, len(senales)):
                tiempo_objetivo, voltaje_objetivo, nombre, color = senales[indice]
                try:
                    desplazamiento = estimar_desplazamiento_temporal(
                        tiempo_referencia,
                        voltaje_referencia,
                        tiempo_objetivo,
                        voltaje_objetivo,
                    )
                    senales[indice] = (
                        tiempo_objetivo + desplazamiento,
                        voltaje_objetivo,
                        nombre,
                        color,
                    )
                    print(
                        f"Alineación aplicada a '{nombre}': "
                        f"{desplazamiento * 1e6:.2f} µs"
                    )
                except ValueError as error:
                    print(f"Advertencia: no se pudo alinear '{nombre}': {error}")

        for i, (tiempo, voltaje, nombre, color) in enumerate(senales):
            ax.plot(
                tiempo * factor_tiempo,
                voltaje,
                label=f"Señal {i + 1}: {nombre}",
                color=color,
                linewidth=1.8,
                alpha=0.9,
            )
        hay_datos = True

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