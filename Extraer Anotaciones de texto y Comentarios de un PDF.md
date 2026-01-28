#utilidades/programación 
#python 


<span style="background:#affad1">Prompt</span>
Quiero un script en Python con interfaz gráfica pyqt6 que dado un PDF extraiga los comentarios y anotaciones insertados en el pdf


<span style="background:#affad1">Captura de pantalla:</span>
![[ANEXOS/Pasted%20image%2020251031093052.png]]

<span style="background:#affad1">Codigo:</span>
![[Extrae comentarios y anotaciones de texto de un pdf dado.py]]

La linea
Estaba dando problemas la linea
``` python
tipo_anot_str = fitz.PDF_ANNOT_TYPE_NAMES[anot.type]
```

y se cambio por:
``` python
tipo_anot_str = f"Tipo numérico: {anot.type}"
```
