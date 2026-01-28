#aforos 
#utilidades/programación 

<span style="background:#b1ffff">Codigo en Python:</span>

``` python
import matplotlib.pyplot as plt

import matplotlib.patches as mpatches

  

# Datos de porcentajes horarios (h1 a h24)

horas = list(range(1, 25))

porcentajes = [2.5, 1.69, 0.83, 0.39, 0.38, 0.51, 1.45, 1.71, 2.16, 4.61, 4.17, 5.48, 5.83, 7.28, 6.41, 6.89, 6.62, 6.74, 6.63, 7.03, 7.13, 6.35, 4.43, 2.78]

  

# Definir colores: rojo para picos (>=7.0), verde para valles (<=1), azul para el resto

colores = []

for p in porcentajes:

    if p >= 7.0:

        colores.append('red')

    elif p <= 1:

        colores.append('green')

    else:

        colores.append('blue')

  

# Crear gráfica de barras

plt.figure(figsize=(12, 6))

bars = plt.bar(horas, porcentajes, color=colores)

  

# Añadir valores encima de las barras

for bar, p in zip(bars, porcentajes):

    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{p:.2f}', ha='center', va='bottom')

  

plt.xlabel('Hora del día (h1: 00-01, h24: 23-00)')

plt.ylabel('Porcentaje del tráfico diario (%)')

plt.title('Distribución Horaria del Tráfico')

plt.xticks(horas)

plt.grid(axis='y', linestyle='--', alpha=0.7)

  
  

# 4. Crear los "parches" manuales para la leyenda

# Estos objetos no se dibujan en el gráfico, solo sirven para la leyenda

patch_verde = mpatches.Patch(color='green', label='Valle')

patch_azul  = mpatches.Patch(color='blue',  label='Tráfico Normal')

patch_rojo  = mpatches.Patch(color='red',   label='Pico')

  

# 5. Añadir la leyenda especificando los 'handles'

plt.legend(handles=[patch_verde, patch_azul, patch_rojo])

  
  

plt.show()
```

<span style="background:#b1ffff">Grafica:</span>
![-](./ANEXOS/Pastedimage20251215145037.png)  

<span style="background:#b1ffff">Código fuente:</span>
![-](./ANEXOS/DistribucionHorariaTrafico%201.py)  


**Nota.**
Leyenda personalizada: hay que usar  patches de la libreria matplotlib
[[python online pagina web)  
