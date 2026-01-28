#utilidades/programación 
#python 



**- prompt:**
1º Intento
Haz un script en python con interfaz visual realizado en pyqt6, donde: 
- Se pueda seleccionar un directorio
- Que muestre todos los ficheros del directorio seleccionado por orden alfabetico.
- Que muestre las siguiente opciones :
a) Añadir letras delante del nombre del fichero: una caja de texto se donde ponga un texto y esta opción renombrará todos los fichero del directorio añadiendo al texto definido por el usuario al inicio de cada nombre de los archivos del directorio seleccionado.

b) Añadir letras detras del nombre del fichero: una caja de texto donde se ponga un texto y esta opción renombrará todos los fichero del directorio añadiendo el texto definido por el usuario al final de cada nombre de los archivos del directorio seleccionado.

c) Reemplazar letras del nombre:  el usuario usa dos caja de texto. Una de ellas contiene el texto a reemplazar y la otra el texto nuevo. Esta opción renombrará todos los fichero del directorio sustituyendo el primer texto por el segundo texto.

La interfaz tendrá un boton de "Previsualización", donde se  previsualizan los cambios antes de realizarlo realmente. 
La interfaz tendrá un botón de "Aplicar", donde se aplicarán los cambios realmente.

2º Intengo
Hay un error, el botón de previsualizar no muestra nada
(corrige el código)

3º Pido que cuando se apliquen los cambios muestre un mensaje de "Cambios Realizados"
4º Le piedo que cree otra opción d) para numerar los ficheros:
Quiero que le añadas una nueva opcion llamemolas d) donde ponga delante del nombre del archvio un numero, este número iria creciendo de 1 en 1 , con un formato de 3 cifras, empezando por el 001
5º Da un error:  Me da este error "Exception has occurred: AttributeError 'QHBoxLayout' object has no attribute 'setVisible'"

Modifica el código y lo corrige.

**- captura de pantalla**
![[ANEXOS/Pasted%20image%2020250702124923.png]]

- **código**
![[ANEXOS/RenombrarFichero.py]]
**- Explicación del programa:**
[[Quiero que me expliques el siguiente código de py....pdf]]

**- Diagrama de flujo:**
``` mermaid
graph TD
    A[Inicio: Ejecutar el programa] --> B{Se abre la ventana principal};
    
    B --> C[Usuario pulsa 'Seleccionar Directorio'];
    C --> D{Abre diálogo para elegir carpeta};
    D -- Carpeta seleccionada --> E[Guarda la ruta y carga los archivos];
    E --> F[Muestra la lista de archivos en la interfaz];
    D -- Usuario cancela --> B;

    subgraph "Ciclo de Renombrado"
        F --> G["Usuario selecciona una opción de renombrado<br/>ej: Prefijo, Sufijo..."];
        G --> H["Usuario introduce el texto necesario<br/>ej: el prefijo 'IMG_'"];
        
        H --> I[Usuario pulsa 'Previsualizar'];
        I --> J["El programa calcula los nuevos nombres<br/>-sin modificar los archivos-"];
        J --> K[Muestra la previsualización:<br/>'nombre_antiguo -> nombre_nuevo'];
        
        K --> L[Usuario pulsa 'Aplicar Cambios'];
        L --> M[El programa vuelve a calcular los nombres];
        M --> N{¿Hay cambios para aplicar?};
        
        N -- Sí --> O["<b>Renombra los archivos en el disco<br/>usando la función os.rename</b>"];
        O --> P[Refresca la lista de archivos con los nuevos nombres];
        P --> Q{Muestra mensaje de 'Éxito'};
        
        N -- No --> R{Muestra mensaje de 'No hay cambios'};
        R --> F;
        Q --> F;
    end

    B --> S[Usuario cierra la ventana];
    S --> T[Fin del programa];
    ```
