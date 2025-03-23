import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, RegularPolygon
import matplotlib.colors as mcolors

def crear_mapa_mental(texto):
    lineas = texto.strip().split('\n')
    resultado = {'_etiqueta': '1'}  # Raíz como diccionario desde el inicio
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
            nuevo_dict = {'_original': clave}
            padre[clave] = nuevo_dict
            pila.append((nivel, nuevo_dict))
        else:
            if 'items' not in padre:
                padre['items'] = []
            padre['items'].append({'_original': texto_limpio})
    return resultado

def generar_colores(n):
    colores_base = list(mcolors.TABLEAU_COLORS.values())
    if n <= len(colores_base):
        return colores_base[:n]
    return [mcolors.hsv_to_rgb((i/n, 0.7, 0.9)) for i in range(n)]

def calcular_max_niveles(mapa, nivel=0):
    max_nivel = nivel
    for clave, valor in mapa.items():
        if clave not in ['_etiqueta', '_original', 'items'] and isinstance(valor, dict):
            max_nivel = max(max_nivel, calcular_max_niveles(valor, nivel + 1))
    if 'items' in mapa:
        max_nivel = max(max_nivel, nivel + 1)
    return max_nivel

def contar_descendientes(mapa):
    total = 0
    for clave, valor in mapa.items():
        if clave not in ['_etiqueta', '_original', 'items']:
            total += 1 + contar_descendientes(valor)
    if 'items' in mapa:
        total += len(mapa['items'])
    return total

def asignar_etiquetas(mapa, prefijo="1"):
    mapa['_etiqueta'] = prefijo
    i = 0
    for clave, valor in list(mapa.items()):  # Usar list para evitar RuntimeError
        if clave not in ['_etiqueta', '_original', 'items'] and isinstance(valor, dict):
            letra = chr(65 + i)  # A, B, C, ...
            nueva_etiqueta = f"{prefijo}{letra}"
            valor['_etiqueta'] = nueva_etiqueta
            asignar_etiquetas(valor, nueva_etiqueta)
            i += 1
    if 'items' in mapa:
        for j, item in enumerate(mapa['items']):
            nueva_etiqueta = f"{prefijo}{j+1}"
            item['_etiqueta'] = nueva_etiqueta

def dibujar_mapa_mental(mapa, ax, x=0, y=0, nivel=0, max_niveles=0, espaciado_vertical=0):
    colores = generar_colores(max_niveles + 1)
    formas = [
        lambda x, y, s: Rectangle((x-s/2, y-s/2), s, s),
        lambda x, y, s: Circle((x, y), s/2),
        lambda x, y, s: RegularPolygon((x, y), 6, radius=s/2)
    ]
    tamaño = 2
    espaciado_horizontal = 4
    
    # Dibujar el nodo actual
    forma = formas[min(nivel, len(formas)-1)](x, y, tamaño)
    forma.set_facecolor(colores[nivel])
    forma.set_edgecolor('black')
    ax.add_patch(forma)
    
    etiqueta = mapa.get('_etiqueta', '')
    ax.text(x, y, etiqueta, ha='center', va='center', fontsize=10, wrap=True)
    
    # Calcular el número de descendientes para centrarlos verticalmente
    num_descendientes = contar_descendientes(mapa)
    x_hijo = x + espaciado_horizontal
    y_hijo_base = y - (num_descendientes - 1) * espaciado_vertical / 2
    
    # Procesar hijos (subsecciones)
    i = 0
    for subclave, subvalor in mapa.items():
        if subclave not in ['_etiqueta', '_original', 'items'] and isinstance(subvalor, dict):
            y_hijo = y_hijo_base + i * espaciado_vertical
            ax.plot([x+tamaño/2, x_hijo-tamaño/2], [y, y_hijo], 'k-')
            sub_descendientes = contar_descendientes(subvalor)
            dibujar_mapa_mental(subvalor, ax, x_hijo, y_hijo, nivel + 1, max_niveles, espaciado_vertical)
            i += sub_descendientes + 1
    
    # Dibujar ítems (hojas)
    if 'items' in mapa:
        for j, item in enumerate(mapa['items']):
            y_item = y_hijo_base + (i + j) * espaciado_vertical
            forma_item = formas[min(nivel+1, len(formas)-1)](x_hijo, y_item, tamaño/1.5)
            forma_item.set_facecolor(colores[nivel + 1])
            forma_item.set_edgecolor('black')
            ax.add_patch(forma_item)
            ax.text(x_hijo, y_item, item['_etiqueta'], ha='center', va='center', fontsize=8)
            ax.plot([x+tamaño/2, x_hijo-tamaño/2], [y, y_item], 'k-')

# Interfaz con Streamlit
st.title("Árbol Genealógico Horizontal - Mapa Mental (Números y Letras)")

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
            asignar_etiquetas(mapa)  # Asignar etiquetas después de crear el mapa
            fig, ax = plt.subplots(figsize=(12, 8))
            espaciado_vertical = 2.5
            dibujar_mapa_mental(mapa, ax, max_niveles=max_niveles, espaciado_vertical=espaciado_vertical)
            ax.set_aspect('equal')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error al procesar el texto: {str(e)}")
    else:
        st.warning("Por favor, ingresa un texto válido.")
