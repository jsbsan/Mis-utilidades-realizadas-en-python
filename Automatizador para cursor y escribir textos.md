#utilidades/programación 
#python 


### <span style="background:#b1ffff">Prompt:</span>
Necesito un script en python, con interfaz grafica en pyqt6 que haga:
-Permita seleccionar un archivo
-Este archivo es de texto plano, y en cada linea tiene una serie de comandos
-El programa Leerá el archivo y ejecutará los comandos.
La estructura de los comandos es:
orden,parametro1,parametro2,parametro3
Te describo las distintas ordenes:
orden: cursor,x,y
ejecuta: pone el cursor del ratón en la coordenada x e y de la pantalla
orden: texto,"texto"
ejecuta: manda por el teclado las pulsaciones del "texto"
orden: return
ejecuta: manda por el teclado la pulsación de la tecla retorno
orden: click
ejecuta: hace una pulsación del boton izquierdo del raton

### <span style="background:#b1ffff">Librerias a instalar:</span>
pip install PyQt6
pip install PyAutoGUI

<span style="background:#b1ffff">Captura de pantalla:</span>

![[ANEXOS/Pasted%20image%2020250710101726.png]]


### Código:
![[automatizar.py]]


### EXTRA:  CODIGO USANDO EL PATRON COMANDO
<span style="background:#b1ffff">PROMPT:</span>
¿puedes aplicar al codigo fuente el patron comando de OOP?
#### **Ventajas de esta nueva estructura**

- **Más limpio**: La lógica de ejecución en `execute_commands` es ahora mucho más simple. Ya no necesita saber qué es un "cursor" o un "texto", solo que tiene un objeto con un método `execute()`.
    
- **Extensible**: Para añadir un nuevo comando (por ejemplo, `dobleclick`), solo necesitas:
    
    1. Crear una nueva clase `DobleClickCommand(Comando)`.
        
    2. Actualizar la función `parse_line_to_command` para que reconozca "dobleclick" y cree un objeto de esa clase. ¡No necesitarás tocar la clase `CommandExecutor` en absoluto!
        
- **Separación de responsabilidades**: Cada clase tiene ahora una única y clara responsabilidad, siguiendo el Principio de Responsabilidad Única (SRP) de SOLID.

Este patrón encapsula una solicitud (un comando) como un objeto, permitiendo parametrizar clientes con diferentes solicitudes, encolar o registrar solicitudes y soportar operaciones que se pueden deshacer. En nuestro caso, nos servirá para eliminar el bloque `if/elif/else` y hacer que añadir nuevos comandos sea mucho más sencillo.

### **Estructura del Patrón Comando Aplicado**

1. **Command (Interfaz)**: Será una clase base abstracta (`Comando`) que define un método `execute()`.
    
2. **ConcreteCommand (Comandos Concretos)**: Crearemos una clase para cada acción (`CursorCommand`, `TextoCommand`, `ClickCommand`, etc.). Cada una heredará de `Comando` y sabrá cómo ejecutar su acción específica.
    
3. **Receiver (Receptor)**: Las bibliotecas `pyautogui` y `time` actúan como receptores. Son las que finalmente realizan el trabajo.
    
4. **Invoker (Invocador)**: La clase `CommandExecutor` (nuestra GUI) actuará como invocador. Su método `execute_commands` no sabrá nada sobre las operaciones; simplemente tomará un objeto comando y llamará a su método `execute()`.
    
5. **Client (Cliente)**: La parte del código que lee y analiza el archivo de texto actuará como cliente, creando la instancia del comando concreto que corresponde a cada línea.


CODIGO PATRON COMANDO
![[ANEXOS/automatizarOOP.py]]