<span style="background:#b1ffff">Prompt:</span>
Eres un experto en programación web, sqlite y python. 
Haz una aplicación para llevar el control de una biblioteca de los libros que tiene la biblioteca. 
Tiene que tener una pagina web en html para añadir/editar/borrar libros de la base de datos sqlite. 
Tiene que tener un servidor realizado en python dedicado a gestionar la base de datos sqlite. 
Quiero que sea accesible la aplicación a otros dispositivos de mi red local.
Quiero añadir un campo de texto para observaciones y otro para poder añadir la imagen de la portada del libro
Necesito que la imagen se guarde en la base de datos, usa Base64
Añade un elemento de paginación cada 5 elementos.
Añade una pestaña para buscar libros por autor, por año, por nombre parcial del libro.

**Nota 1:**
Me daba un error al no estar instalado flask
Pongo en comando en la terminal:

> python3 -m pip install flask

y se instala y se ejecuta la app.py

**Nota 2:**
En la ultima linea, hay que poner la ip local del ordenador que aloja la app.py.


**Nota 3:**
La base de datos sqlite (biblioteca.db) la crea si no existe el fichero.

**Nota 4:**
¿que quiere decir "WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead." que sale en la terminal de la ejecución de la aplicacion app.py?

> Ese mensaje es completamente normal y **no es un error**.
> Te explico qué significa:
> 1. **Servidor de Desarrollo vs. Producción:** Flask (la herramienta que usas) viene con un servidor "ligero" incorporado para que puedas probar tu aplicación mientras la programas. Ese es el que estás usando ahora.
>     
> 2. **La Advertencia:** Te avisa de que ese servidor ligero no está diseñado para soportar miles de usuarios a la vez ni tiene todas las medidas de seguridad necesarias para estar abierto en internet a todo el mundo (como una web profesional tipo Facebook o Google).
>     
> 3. **¿Debes preocuparte?** **No.** Para tu uso (una biblioteca personal en tu casa o red local), el servidor de desarrollo es perfecto, seguro y suficiente.
>     
> En resumen: Flask te está diciendo "Oye, si vas a montar una empresa con esto, usa un servidor más potente (WSGI)", pero para lo que estamos haciendo, **puedes ignorar el mensaje tranquilamente**. Todo está funcionando bien.
> 

<span style="background:#b1ffff">Captura de la aplicación:</span>

| ordenador                                                                  | movil                                              |
| -------------------------------------------------------------------------- | -------------------------------------------------- |
| Ventana de Inventario y Gestión: ![ANEXOS/Pasted%20image%2020251224124345.png\|800]   | ![ANEXOS/Pasted%20image%2020251224124952.png]                 |
| Pestaña de Busqueda: ![ANEXOS/Pasted%20image%2020251224131142.png\|800]               | Servidor:![ANEXOS/Pasted%20image%2020251224125037.png\|400]   |


<span style="background:#affad1">Código:</span>
![ANEXOS/app.py]  