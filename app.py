import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, RegularPolygon

def crear_mapa_mental(texto):
    lineas = texto.strip().split('\n')
    resultado = {}
    pila = [(0, resultado)]  # Pila inicial con nivel 0
    
    for linea in lineas:
        nivel = 0
        while linea.startswith('\t'):
            nivel += 1
            linea = linea[1:]
        texto_limpio = linea.strip()
        if not texto_limpio:
            continue
        
        # Asegurarse de que la pila no quede vacía
        while pila and pila[-1][0] >= nivel:
            pila.pop()
        
        # Si la pila está vacía, reiniciarla con el nivel raíz
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

def dibujar_mapa_mental(mapa, ax, x=0, y=0, nivel=0):
    colores = ['#FF9999', '#99CCFF', '#99FF99']  # Rojo, Azul, Verde
    formas = [
        lambda x, y, s: Rectangle((x-s/2, y-s/2), s, s),  # Cuadrado
        lambda x, y, s: Circle((x, y), s/2),              # Círculo
        lambda x, y, s: RegularPolygon((x, y), 6, s/2)    # Hexágono
    ]
    tamaño = 2
    espaciado_vertical = -3
    espaciado_horizontal = 5
    
    forma = formas[min(nivel, len(formas)-1)](x, y, tamaño)
    forma.set_facecolor(colores[min(nivel, len(colores)-1)])
    forma.set_edgecolor('black')
    ax.add_patch(forma)
    
    clave = list(mapa.keys())[0] if nivel == 0 or 'items' not in mapa else ""
    if clave:
        ax.text(x, y, clave, ha='center', va='center', fontsize=10, wrap=True)
    
    y_hijo = y + espaciado_vertical
    x_hijo_base = x - (len(mapa) - 1) * espaciado_horizontal / 2
    
    for i, (subclave, subvalor) in enumerate(mapa.items()):
        if subclave != 'items':
            x_hijo = x_hijo_base + i * espaciado_horizontal
            ax.plot([x, x_hijo], [y-tamaño/2, y_hijo+tamaño/2], 'k-')
            dibujar_mapa_mental(subvalor, ax, x_hijo, y_hijo, nivel + 1)
    
    if 'items' in mapa:
        for i, item in enumerate(mapa['items']):
            x_item = x + (i - len(mapa['items'])/2 + 0.5) * espaciado_horizontal
            y_item = y + espaciado_vertical
            forma_item = formas[min(nivel+1, len(formas)-1)](x_item, y_item, tamaño/1.5)
            forma_item.set_facecolor(colores[min(nivel+1, len(colores)-1)])
            forma_item.set_edgecolor('black')
            ax.add_patch(forma_item)
            ax.text(x_item, y_item, item, ha='center', va='center', fontsize=8)
            ax.plot([x, x_item], [y-tamaño/2, y_item+tamaño/2], 'k-')

# Interfaz con Streamlit
st.title("Generador de Mapas Mentales")

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

if st.button("Generar Mapa Mental"):
    if texto_input:
        try:
            mapa = crear_mapa_mental(texto_input)
            fig, ax = plt.subplots(figsize=(12, 8))
            dibujar_mapa_mental(mapa, ax)
            ax.set_aspect('equal')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error al procesar el texto: {str(e)}")
    else:
        st.warning("Por favor, ingresa un texto válido.")
