import os
import re
import matplotlib.pyplot as plt
import pandas as pd

# ==============================================================================
# CONFIGURACIÓN DE USUARIO (Modifica estas variables)
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "BW LM348.txt")  # Ruta del archivo exportado de LTspice
PLOT_TITLE = (
    "Ancho de banda inversor OpAmp LM348 (simulación)"  # Título personalizable
)
# ============================================================================== 


def graficar_ltspice(ruta_archivo: str, titulo: str):
  """Lee un análisis AC de LTspice y grafica magnitud y fase contra frecuencia."""
  if not os.path.exists(ruta_archivo):
    raise FileNotFoundError(
      f"No se encontró el archivo en la ruta '{ruta_archivo}'."
    )

  # LTspice exporta el símbolo de grados en Windows-1252.
  df = pd.read_csv(ruta_archivo, sep=r"\s+", encoding="cp1252")

  frecuencia = pd.to_numeric(df.iloc[:, 0], errors="coerce")
  if frecuencia.isna().any() or (frecuencia <= 0).any():
    raise ValueError("La primera columna debe contener frecuencias positivas.")

  # Una señal AC de LTspice tiene el formato (magnituddB,fase°).
  patron_ac = re.compile(
    r"\(\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)dB\s*,"
    r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:°|�)?\s*\)"
  )

  magnitudes = {}
  fases = {}
  for columna in df.columns[1:]:
    valores = df[columna].astype(str).map(patron_ac.fullmatch)
    if valores.isna().any():
      raise ValueError(
        f"No se pudo interpretar la señal AC '{columna}'. "
        "Se esperaba el formato '(magnituddB,fase°)'."
      )
    magnitudes[columna] = valores.map(lambda coincidencia: float(coincidencia.group(1)))
    fases[columna] = valores.map(lambda coincidencia: float(coincidencia.group(2)))

  (ax_magnitud, ax_fase) = plt.subplots(
    2, 1, figsize=(10, 7), dpi=120, sharex=True
  )[1]

  for columna in magnitudes:
    ax_magnitud.semilogx(
      frecuencia, magnitudes[columna], label=columna, linewidth=1.8
    )
    ax_fase.semilogx(
      frecuencia, fases[columna], label=columna, linewidth=1.8
    )

  ax_magnitud.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
  ax_magnitud.set_ylabel("Magnitud [dB]", fontsize=11)
  ax_fase.set_xlabel("Frecuencia [Hz]", fontsize=11)
  ax_fase.set_ylabel("Fase [°]", fontsize=11)
  for eje in (ax_magnitud, ax_fase):
    eje.grid(True, which="both", linestyle="--", alpha=0.6)
    eje.legend(loc="best", frameon=True, facecolor="white", edgecolor="none")

  plt.tight_layout()
  plt.show()


if __name__ == "__main__":
  graficar_ltspice(FILE_PATH, PLOT_TITLE)