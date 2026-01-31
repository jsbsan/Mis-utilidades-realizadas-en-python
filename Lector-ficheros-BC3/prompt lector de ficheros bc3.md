-------
prompt inicial
-------

Analiza la documentación que te adjunto sobre el formato BC3
ROL: INGENIERO PROGRAMADOR
Crear una aplicación lectora de fichero bc3.
- Centrate en los registros tipo:
	- ~V.  REGISTRO TIPO PROPIEDAD Y VERSIÓN.
	- ~C.  REGISTRO TIPO CONCEPTO.
	- ~D.  REGISTRO TIPO DESCOMPOSICIÓN. 
	- ~T.  REGISTRO TIPO TEXTO.
	- ~M.  REGISTRO TIPO MEDICIONES. 


Ultiliza la plantilla division.html para:
- En el panel "arbol", que muestre el arbol de conceptos y permita seleccionarlo y bajar o subir por el arbol de conceptos.
- En el panel "descompuesto", muestre los registros de descompuestos del concepto seleccionado en el panel "arbol"
- En el panel "textodescriptivo" muestre el regitro tipo texto del concepto seleccionado del panel "arbol"
- En el panel "mediciones", muestre los registros de mediciones del concepto seleccionado en el panel "arbol"

El programa debe de permitir que el usuario selecciones un fichero bc3

-------
prompt
-------
Necesito que cuando le hagas click a una partida del arbol de conceptos muestre los precios que lo descomponen , y actualice el resto de paneles.

-------
prompt
-------

Ten encuenta que: El concepto raiz es el que tenga de parte del codigo es ##, el que esta debajo justo de el en el arbol es el que contenga en el código #


-------
prompt
-------
El concepto que tiene en el código  los caractes "##", tiene información del titulo del presupuesto. Ponlo en un panel arriba de los otros. Los conceptos de lectura iniciales son los que tienen el caracter "#" en el código. Actualiza el código teniendo encuenta lo anterior.


-------
prompt
-------
Cuando seleciono el archivo bc3, el arbol de capitulo no se rellena


-------
prompt
-------
Rol: eres analista en programación y especializado en sistemas para realizar  presupuestos. Analiza la información que te adjunto, para hacer mejoras en el fichero index.html
El concepto que tiene en el código  los caractes "##", tiene información del titulo del presupuesto. Los conceptos de capitulos son los que tienen el caracter "#" en el código. Actualiza el código teniendo encuenta lo anterior. Los otros conceptos serán hijos de los anteriores (conceptos capitulos)



-------
prompt
-------
No consigo ver el arbol. El concepto que tiene en el código los caractes "##", tiene información del titulo del presupuesto. Los conceptos de capitulos son los que tienen el caracter "#" en el código. Actualiza el código teniendo encuenta lo anterior. Los otros conceptos serán hijos de los anteriores (conceptos capitulos). Modifica el código para ver el arbol completo de la esctructura de la obra

-------
prompt
-------
He actualizado el fichero "descripcion formato bc3.txt", para que lo vuelvas a analizar. Analiza la el ~K. REGISTRO TIPO COEFICIENTES para interpretarlo. 

-------
prompt
-------
El desglose de mediciones, no se muestra, revisalo y comprueba el código

-------
prompt (le adjunto el bc3 de centano.bc3)
------- 
Te paso un bc3 más completo para que veas como es. 

-------
prompt
-------

En el precio unitario y en el total de lineas, además del valor,  añades los datos de coeficientes y moneda, no pongas los coeficientes

Le paso una imagen subrayando los valores que no quiero que aparezcan y le digo:
Me refiero a que no deben de aparecen lo subrayado en rojo

-------
prompt
-------
No sale el total de la obra ni el total de los capitulos. (te lo marco subrayado en la imagen adjunta)

-------
prompt (cargo archivos y activo modo "pro")
-------
Rol: eres ingeniero programador especializado en programs para presupuestos de obra. Analiza el código de lector_bc3, el fichero de descripción del formato bc3 y el fichero centano.bc3 que es un ejemplo completo del formato  bc3. Cuando estes listo me lo dices para añadir corregir algunos bugs que he visto.

(detecta varios bug, y le digo que los corrija)

-------
prompt (cargo archivos y activo modo "pro")
-------
En lo que muestras del listado de mediciones, debe aparecer los valores de Subtotal como en la imagen que te adjunto. 

Vamos a revisar los textos largo, parece que solo se muestra una linea, cuando el texto largo son varias. Por ejemplo de la imagen que te adjunto, solo sale el texto que te he subrayado, el resto no se muestra. ¿puedes analizar que pasa?

Otro detalle, el texto que muestras siempre le pones al final el caracter "|", este no deberia de salir.

Otro detalle. En las mediciones. Parece que faltan columnas, deberían de ser las que te adjunto en el imagen. Revisalo 

Para interpretar la fórmula ten tambien en cuenta lo siguiente: Correspondencia de Columnas
a = Columna N 
b = Columna Longitud
c = Columna Anchura
d = Columna Altura

vaya, parece que el comentario de la mediciones algunas veces no lo muestras. Fijate en la imagen adjunta, los subrayados son los que faltan, el resto esta correcto. -> me doy cuenta que el bc3 no lo ha exportado esa información.


-------
prompt
-------
Otro detalle de diseño web, quiero que salga de mayor tamaño el texto del código. Te adjunto pantallazo indicando con una flecha a lo que me refiero.


