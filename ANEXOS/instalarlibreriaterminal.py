import sys
import subprocess

def gestionar_entorno():
    # 1. Detectar la versión de Python
    version = sys.version.split()[0]
    print(f"--- Sistema Detectado ---")
    print(f"Versión de Python: {version}")
    
    # 2. Solicitar la librería al usuario
    libreria = input("\n¿Qué librería deseas instalar? (ej. requests, pandas): ").strip()
    
    if not libreria:
        print("No ingresaste ningún nombre. Saliendo...")
        return

    print(f"Intentando instalar '{libreria}'...")

    # 3. Ejecutar la instalación
    try:
        # Usamos sys.executable para asegurarnos de que se instale 
        # en el mismo Python que está corriendo este script
        subprocess.check_call([sys.executable, "-m", "pip", "install", libreria])
        print(f"\n✅ ¡Éxito! La librería '{libreria}' se instaló correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al instalar la librería. Código de salida: {e.returncode}")
    except Exception as e:
        print(f"\n⚠️ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    gestionar_entorno()