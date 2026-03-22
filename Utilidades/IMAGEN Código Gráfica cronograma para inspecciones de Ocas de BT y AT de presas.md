#OCAS 
#python 
#utilidades/programación 


**Utilidad:**
El programa genera una imagen (archivo gráfico) con los datos de presas/fechas de inspección.

**Promp pasado:**
HAZME UNA GRÁFICA TIPO CRONOGRAMA CON LA TABLA QUE TE ADJUNTO.
¿ME LA PUEDES REPRESENTAR?
¿me puedes presentar la gráfica con en eje Y nombre de la presa y en el eje x fechas?
no pongas leyenda
Quiero una gráfica para la BT que incluya desde el 2023 hasta el 2030

|        |                   |      |                  |             |
| ------ | ----------------- | ---- | ---------------- | ----------- |
| codigo | presa             | tipo | fecha prox. Insp | observación |
| 53     | peñaflor          | BT   | 05/11/2024       | presa       |
| 53     | peñaflor          | BT   | 05/11/2024       | poblado     |
| 55     | puebla de cazalla | BT   | 25/02/2027       |             |
| 56     | Huesna            | BT   | 07/11/2024       |             |
| 57     | Pintado           | BT   | 22/02/2027       | POBLADO     |
| 57     | Pintado           | BT   | 22/02/2027       | PRESA       |
| 58     | MELONARES         | BT   | 04/02/2025       |             |
| 61     | ARACENA           | BT   | 21/03/2027       | POBLADO     |
| 61     | ARACENA           | BT   | 21/03/2027       | PRESA       |
| 62     | ZUFRE             | BT   | 03/02/2025       |             |
| 67     | AGRIO             | BT   | 24/02/2025       |             |
| 68     | TORRE DEL AGUILA  | BT   | 26/05/2030       |             |
| 98     | INFIERNO          | BT   | 04/12/2025       |             |
| 99     | RENEGADO          | BT   | 04/12/2025       |             |


**Generación de imagen:**  
![-](./ANEXOS/Pastedimage20250910085836.png)  

**Código:**  

``` python
import pandas as pd

import matplotlib.pyplot as plt

from datetime import datetime

  

data = {

    'presa': ['peñaflor', 'peñaflor', 'puebla de caz', 'puebla de caz', 'puebla de caz', 'Huesna', 'Huesna',

              'Pintado', 'Pintado', 'Pintado', 'MELONARES', 'MELONARES', 'ARACENA', 'ARACENA', 'ZUFRE', 'ZUFRE',

              'AGRIO', 'AGRIO', 'TORRE DEL', 'TORRE DEL', 'INFIERNO', 'INFIERNO', 'RENEGADO', 'RENEGADO'],

    'tipo': ['BT', 'AT', 'BT', 'AT', 'AT', 'BT', 'AT', 'BT', 'BT', 'AT', 'BT', 'AT', 'BT', 'AT', 'BT', 'AT',

             'BT', 'AT', 'BT', 'AT', 'BT', 'AT', 'BT', 'AT'],

    'fecha_prox_Insp': ['05/11/2024', '21/06/2026', '25/02/2027', '24/02/2023', '07/06/2026', '07/11/2024', '23/10/2026',

                        '22/02/2027', '22/02/2027', '23/10/2026', '04/02/2025', '19/06/2026', '21/03/2027', '22/06/2026',

                        '03/02/2025', '23/06/2026', '24/02/2025', '24/02/2023', '26/05/2030', '20/06/2026',

                        '04/12/2025', '28/08/2027', '04/12/2025', '28/08/2027']

}

  

df = pd.DataFrame(data)

  

# Convert 'fecha_prox_Insp' to datetime and capitalize presa names

df['fecha'] = pd.to_datetime(df['fecha_prox_Insp'], format='%d/%m/%Y')

df['presa'] = df['presa'].str.title()

  

# Filter data to only include 'BT'

df_bt = df[df['tipo'] == 'BT'].copy()

  

# Sort data for better visualization

df_bt = df_bt.sort_values(by='presa', ascending=False)

  

# Create the plot

plt.style.use('seaborn-v0_8-whitegrid')

fig, ax = plt.subplots(figsize=(12, 8))

  

# Plot the filtered BT points (removed label as legend is not needed)

ax.plot(df_bt['fecha'], df_bt['presa'], marker='o', linestyle='', markersize=12, color='dodgerblue')

  

# Set the X-axis range from 2023 to 2030

start_date = datetime(2023, 1, 1)

end_date = datetime(2030, 12, 31)

ax.set_xlim(left=start_date, right=end_date)

  

# Add titles and labels

ax.set_title('Cronograma de Inspecciones BT (2023-2030)', fontsize=18, pad=20)

ax.set_xlabel('Fecha de Inspección', fontsize=12)

ax.set_ylabel('Presa', fontsize=12)

  

# --- REMOVE LEGEND ---

# ax.legend() # This line is commented out to remove the legend

# ---------------------

  

# Improve layout and formatting

ax.grid(True, which='major', axis='x', linestyle='--', linewidth=0.5)

plt.tight_layout()

fig.autofmt_xdate() # Format dates to avoid overlap

  

# Save the figure

plt.savefig('cronograma_bt_2023-2030_no_legend.png')

```


Nota:
Código para la AT:
``` python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Datos iniciales de la tabla
data = {
    'presa': ['peñaflor', 'peñaflor', 'puebla de caz', 'puebla de caz', 'puebla de caz', 'Huesna', 'Huesna',
              'Pintado', 'Pintado', 'Pintado', 'MELONARES', 'MELONARES', 'ARACENA', 'ARACENA', 'ZUFRE', 'ZUFRE',
              'AGRIO', 'AGRIO', 'TORRE DEL', 'TORRE DEL', 'INFIERNO', 'INFIERNO', 'RENEGADO', 'RENEGADO'],
    'tipo': ['BT', 'AT', 'BT', 'AT', 'AT', 'BT', 'AT', 'BT', 'BT', 'AT', 'BT', 'AT', 'BT', 'AT', 'BT', 'AT',
             'BT', 'AT', 'BT', 'AT', 'BT', 'AT', 'BT', 'AT'],
    'fecha_prox_Insp': ['05/11/2024', '21/06/2026', '25/02/2027', '24/02/2023', '07/06/2026', '07/11/2024', '23/10/2026',
                        '22/02/2027', '22/02/2027', '23/10/2026', '04/02/2025', '19/06/2026', '21/03/2027', '22/06/2026',
                        '03/02/2025', '23/06/2026', '24/02/2025', '24/02/2023', '26/05/2030', '20/06/2026',
                        '04/12/2025', '28/08/2027', '04/12/2025', '28/08/2027']
}

df = pd.DataFrame(data)

# 2. Preparación de los datos
# Convertir la columna de fecha a formato datetime
df['fecha'] = pd.to_datetime(df['fecha_prox_Insp'], format='%d/%m/%Y')
# Poner en mayúscula la primera letra del nombre de la presa
df['presa'] = df['presa'].str.title()

# 3. Filtrado de datos para la gráfica
# Seleccionar únicamente las filas de tipo 'AT'
df_at = df[df['tipo'] == 'AT'].copy()

# Ordenar los datos por el nombre de la presa para una mejor visualización
df_at = df_at.sort_values(by='presa', ascending=False)

# 4. Creación de la gráfica
# Configurar el estilo y tamaño del gráfico
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 8))

# Dibujar los puntos en la gráfica
ax.plot(df_at['fecha'], df_at['presa'], marker='o', linestyle='', markersize=12, color='coral')

# 5. Ajuste de los ejes
# Establecer el rango del eje X (fechas) desde 2023 a 2030
start_date = datetime(2023, 1, 1)
end_date = datetime(2030, 12, 31)
ax.set_xlim(left=start_date, right=end_date)

# 6. Añadir títulos y etiquetas
ax.set_title('Cronograma de Inspecciones AT (2023-2030)', fontsize=18, pad=20)
ax.set_xlabel('Fecha de Inspección', fontsize=12)
ax.set_ylabel('Presa', fontsize=12)

# 7. Formato final y guardado
# Añadir una rejilla para facilitar la lectura
ax.grid(True, which='major', axis='x', linestyle='--', linewidth=0.5)
# Ajustar el diseño para que todo encaje correctamente
plt.tight_layout()
# Formatear las fechas en el eje X para que no se solapen
fig.autofmt_xdate()

# Guardar la gráfica en un archivo de imagen
plt.savefig('cronograma_at_2023-2030.png')

# Mostrar la gráfica (si se ejecuta en un entorno interactivo)
plt.show()
```

![-](./ANEXOS/Pastedimage20250910091207.png)  