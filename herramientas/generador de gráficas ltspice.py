import os
import matplotlib.pyplot as plt
import pandas as pd

# ==============================================================================
# CONFIGURACIÓN DE USUARIO (Modifica estas variables)
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "BW LM348.txt")  # Ruta del archivo exportado de LTspice
PLOT_TITLE = (
    "Ancho de banda inversor OpAmp LF353  (simulación)"  # Título personalizable
)
# ============================================================================== 


def graficar_ltspice(ruta_archivo: str, titulo: str):
  """Lee un archivo de exportación de LTspice (.txt) y grafica todas las señales

  en función del tiempo.
  """
  if not os.path.exists(ruta_archivo):
    print(f"Error: No se encontró el archivo en la ruta '{ruta_archivo}'.")
    return

  # Carga de datos delimitados por espacios o tabuladores
  df = pd.read_csv(ruta_archivo, sep=r"\s+")

  # Identificación de columnas
  time_col = df.columns[0]
  signal_cols = df.columns[1:]

  tiempo = df[time_col].values
  unidad_tiempo = "s"

  # Conversión automática de escala de tiempo para legibilidad
  max_t = tiempo.max()
  if max_t < 1e-3:
    tiempo = tiempo * 1e6
    unidad_tiempo = "µs"
  elif max_t < 1.0:
    tiempo = tiempo * 1e3
    unidad_tiempo = "ms"

  # Estilo de la gráfica
  fig, ax = plt.subplots(figsize=(10, 5), dpi=120)

  # Graficado de cada nodo/señal presente en la exportación
  for col in signal_cols:
    ax.plot(tiempo, df[col], label=col, linewidth=1.8)

  # Formato y etiquetas del eje
  ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
  ax.set_xlabel(f"Tiempo [{unidad_tiempo}]", fontsize=11)
  ax.set_ylabel("Tensión [V]", fontsize=11)
  ax.grid(True, linestyle="--", alpha=0.6)
  ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="none")

  plt.tight_layout()
  plt.show()


if __name__ == "__main__":
  graficar_ltspice(FILE_PATH, PLOT_TITLE)