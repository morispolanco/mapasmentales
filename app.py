import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, RegularPolygon
import matplotlib.colors as mcolors

def crear_mapa_mental(texto):
    lineas = texto.strip().split('\n')
    resultado = {}
    pila = [(0, resultado)]
    
    for linea in lineas:
        nivel = 0
        while linea.startswith('\t'):
            nivel += 1
            linea = linea[1:]
        texto_limpio = linea.strip()
        if not texto_limpio:
            continue
        while pila and pila[-1][0] >= nivel:
            pila.pop()
        if not pila:
            pila.append((0, resultado))
        padre = pila[-1][1]
        if texto_limpio.endswith(':'):
            clave = texto_limpio[:-1].strip()
            nuevo_dict = {}
            padre[clave] = nuevo_dict
            pila.append((nivel, nuevo_dict))
        else:
            if 'items' not in padre:
                padre['items'] = []
            padre['items'].append(texto_limpio)
    return resultado

def generar_colores(n):
    """Genera una lista de n colores distintos."""
    colores_base = list(mcolors.TABLEAU_COLORS.values())
    if n <= len(colores_base):
        return colores_base[:n]
    return [mcolors.hsv_to_rgb((i/n, 0.7, 0.9)) for i in range(n)]

def calcular_max_niveles(mapa, nivel=0):
    """Calcula el nivel máximo de anidamiento."""
    max_nivel = nivel
    for clave, valor in mapa.items():
        if clave != 'items' and isinstance(valor, dict):
            max_nivel = max(max_nivel, calcular_max_niveles(valor, nivel + 1))
    if 'items' in mapa:
        max_nivel = max(max_nivel, nivel + 1)
    return max_nivel

def contar_descendientes(mapa):
    """Cuenta el número total de descendientes (hijos + ítems) para ajustar el espaciado."""
    total = 0
    for clave, valor in mapa.items():
        if clave != 'items':
            total += 1 + contar_descendientes(valor)
    if 'items' in mapa:
        total += len(mapa['items'])
    return total

def dibujar_mapa_mental(mapa, ax, x=0, y=0, nivel=0, max_niveles=0, espaciado_horizontal=0):
    colores = generar_colores(max_niveles + 1)
    formas = [
        lambda x, y, s: Rectangle((x-s/2, y-s/2), s, s),  # Cuadrado
        lambda x, y, s: Circle((x, y), s/2),              # Círculo
        lambda x, y, s: RegularPolygon((x, y), 6, radius=s/2)  # Hexágono
    ]
    tamaño = 2
    espaciado_vertical = -3
    
    # Dibujar el nodo actual
    forma = formas[min(nivel, len(formas)-1)](x, y, tamaño)
    forma.set_facecolor(colores[nivel])
    forma.set_edgecolor('black')
    ax.add_patch(forma)
    
    clave = list(mapa.keys())[0] if nivel == 0 or 'items' not in mapa else ""
    if clave:
        ax.text(x, y, clave, ha='center', va='center', fontsize=10, wrap=True)
    
    # Calcular el número de descendientes para centrarlos
    num_descendientes = contar_descendientes(mapa)
    y_hijo = y + espaciado_vertical
    x_hijo_base = x - (num_descendientes - 1) * espaciado_horizontal / 2
    
    # Procesar hijos (subsecciones)
    i = 0
    for subclave, subvalor in mapa.items():
        if subclave != 'items':
            x_hijo = x_hijo_base + i * espaciado_horizontal
            ax.plot([x, x_hijo], [y-tamaño/2, y_hijo+tamaño/2], 'k-')
            sub_descendientes = contar_descendientes(subvalor)
            dibujar_mapa_mental(subvalor, ax, x_hijo, y_hijo, nivel + 1, max_niveles, espaciado_horizontal)
            i += sub_descendientes + 1
    
    # Dibujar ítems (hojas)
    if 'items' in mapa:
        for j, item in enumerate(mapa['items']):
            x_item = x_hijo_base + (i + j) * espaciado_horizontal
            forma_item = formas[min(nivel+1, len(formas)-1)](x_item, y_hijo, tamaño/1.5)
            forma_item.set_facecolor(colores[nivel + 1])
            forma_item.set_edgecolor('black')
            ax.add_patch(forma_item)
            ax.text(x_item, y_hijo, item, ha='center', va='center', fontsize=8)
            ax.plot([x, x_item], [y-tamaño/2, y_hijo+tamaño/2], 'k-')

# Interfaz con Streamlit
st.title("Árbol Genealógico - Mapa Mental")

texto_default = """
Tema principal:
	Sección 1:
		idea 1
		idea 2
	Sección 2:
		idea 3
	idea suelta
"""

texto_input = st.text_area("Ingresa tu lista estructurada con tabulaciones:", value=texto_default, height=200)

if st.button("Generar Árbol Genealógico"):
    if texto_input:
        try:
            mapa = crear_mapa_mental(texto_input)
            max_niveles = calcular_max_niveles(mapa)
            fig, ax = plt.subplots(figsize=(12, 8))  # Ajustar tamaño según necesidad
            espaciado_horizontal = 2.5  # Espaciado entre nodos en el mismo nivel
            dibujar_mapa_mental(mapa, ax, max_niveles=max_niveles, espaciado_horizontal=espaciado_horizontal)
            ax.set_aspect('equal')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error al procesar el texto: {str(e)}")
    else:
        st.warning("Por favor, ingresa un texto válido.")
