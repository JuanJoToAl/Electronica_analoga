import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

def graficar_salida_rectificador(csv_path, titulo="Señal de Salida: Rectificador de Onda Completa", output_pdf="grafica_salida_rectificador.pdf"):
    """
    Procesa el CSV de salida del osciloscopio, aplica formato SI en ejes
    y exporta la figura en formato vectorial (PDF) e imagen (PNG).
    """
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"Error al abrir el CSV: {e}")
        return

    col_tiempo = df.columns[0]   # 'in s'
    col_voltaje = df.columns[1]  # 'CH1 in V'

    tiempo = df[col_tiempo]
    voltaje = df[col_voltaje]

    # Configuración de lienzo técnico / IEEE
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    
    # Trazo de salida
    ax.plot(tiempo, voltaje, color='#1f77b4', linewidth=1.8, label=r'Salida CH1 ($V_{out}$)')
    
    # Formato de unidades con prefijos SI (ms, V)
    ax.xaxis.set_major_formatter(EngFormatter(unit='s'))
    ax.yaxis.set_major_formatter(EngFormatter(unit='V'))
    
    # Textos y etiquetas
    ax.set_title(titulo, fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Tiempo ($t$)', fontsize=11)
    ax.set_ylabel('Tensión ($V$)', fontsize=11)
    
    # Cuadrícula principal y secundaria
    ax.grid(True, which='major', color='#555555', linestyle='-', alpha=0.35)
    ax.minorticks_on()
    ax.grid(True, which='minor', color='#888888', linestyle=':', alpha=0.2)
    
    # Ejes de referencia en cero
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(0, color='black', linewidth=1, linestyle='--')
    
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_pdf, format='pdf')
    plt.savefig(output_pdf.replace('.pdf', '.png'), format='png', dpi=300)
    print(f"Gráfica guardada exitosamente en:\n - {output_pdf}\n - {output_pdf.replace('.pdf', '.png')}")
    plt.show()

if __name__ == "__main__":
    graficar_salida_rectificador('salida rectificador de onda completa.CSV')