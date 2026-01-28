import sqlite3
import base64
import math
from flask import Flask, render_template_string, request, redirect, url_for, flash

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = 'super_secreto_clave_para_sesiones' 
DB_NAME = 'biblioteca.db'
LIBROS_POR_PAGINA = 5

# --- Lógica de Base de Datos (SQLite) ---

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                anio INTEGER,
                isbn TEXT
            )
        ''')
        
        # Migraciones
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(libros)")
        columnas = [info[1] for info in cursor.fetchall()]
        
        if 'observaciones' not in columnas:
            conn.execute('ALTER TABLE libros ADD COLUMN observaciones TEXT')
        if 'portada_data' not in columnas:
            conn.execute('ALTER TABLE libros ADD COLUMN portada_data TEXT')
            
        conn.commit()
    finally:
        conn.close()

def get_libros_paginados(page, busqueda=None, criterio=None):
    """
    Obtiene libros paginados, con soporte opcional para filtros de búsqueda.
    busqueda: texto a buscar
    criterio: columna donde buscar ('titulo', 'autor', 'anio')
    """
    conn = get_db_connection()
    offset = (page - 1) * LIBROS_POR_PAGINA

    # Construcción de la consulta SQL dinámica
    sql_base = "SELECT * FROM libros"
    sql_count = "SELECT COUNT(*) FROM libros"
    params = ()

    if busqueda and criterio in ['titulo', 'autor', 'anio']:
        # Filtro de búsqueda (usamos LIKE para búsquedas parciales)
        filtro = f" WHERE {criterio} LIKE ?"
        sql_base += filtro
        sql_count += filtro
        params = (f'%{busqueda}%',) # Los % permiten buscar texto parcial

    # 1. Contar total de resultados para la paginación
    total_libros = conn.execute(sql_count, params).fetchone()[0]
    total_pages = math.ceil(total_libros / LIBROS_POR_PAGINA)
    if total_pages == 0: total_pages = 1

    # Asegurar página válida
    if page < 1: page = 1
    if page > total_pages: page = total_pages
    
    # Recalcular offset si la página cambió
    offset = (page - 1) * LIBROS_POR_PAGINA

    # 2. Obtener los libros
    sql_final = sql_base + " ORDER BY id DESC LIMIT ? OFFSET ?"
    params_final = params + (LIBROS_POR_PAGINA, offset)
    
    libros = conn.execute(sql_final, params_final).fetchall()
    conn.close()
    
    return libros, total_pages, page, total_libros

# --- Plantilla HTML (Frontend) ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestión de Biblioteca</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f8f9fa; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header-bg { background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 2rem 0; margin-bottom: 2rem; }
        .book-cover-thumb { width: 60px; height: 90px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .book-cover-placeholder { width: 60px; height: 90px; background-color: #e9ecef; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #adb5bd; font-size: 1.5rem; }
        .preview-img { max-width: 100px; max-height: 150px; display: block; margin-top: 10px; border: 1px solid #ddd; }
        
        /* Estilo para las pestañas de navegación */
        .nav-tabs .nav-link { color: #495057; font-weight: 500; }
        .nav-tabs .nav-link.active { color: #0d6efd; border-top: 3px solid #0d6efd; font-weight: bold; }
        .highlight { background-color: #fff3cd; }
    </style>
</head>
<body>

    <div class="header-bg text-center">
        <h1><i class="fas fa-book-reader"></i> Biblioteca Digital</h1>
        <p class="lead">Gestión de Libros con Imágenes y Búsqueda</p>
    </div>

    <div class="container-fluid px-4">
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- Pestañas de Navegación -->
        <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
                <a class="nav-link {% if modo == 'inventario' %}active{% endif %}" href="{{ url_for('index') }}">
                    <i class="fas fa-list"></i> Inventario & Gestión
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if modo == 'buscar' %}active{% endif %}" href="{{ url_for('pagina_buscar') }}">
                    <i class="fas fa-search"></i> Buscar Libros
                </a>
            </li>
        </ul>

        <div class="row">
            <!-- COLUMNA IZQUIERDA: Formulario (Cambia según el modo) -->
            <div class="col-lg-4 mb-4">
                
                {% if modo == 'inventario' %}
                    <!-- MODO INVENTARIO: Formulario de Añadir/Editar -->
                    <div class="card sticky-top" style="top: 20px; z-index: 100;">
                        <div class="card-header bg-dark text-white">
                            <h5 class="mb-0">
                                {% if libro_editar %} <i class="fas fa-edit"></i> Editar Libro
                                {% else %} <i class="fas fa-plus-circle"></i> Nuevo Libro {% endif %}
                            </h5>
                        </div>
                        <div class="card-body">
                            <form action="{{ url_for('guardar_libro') }}" method="POST" enctype="multipart/form-data">
                                {% if libro_editar %}
                                    <input type="hidden" name="id" value="{{ libro_editar['id'] }}">
                                {% endif %}
                                
                                <div class="mb-3">
                                    <label class="form-label">Título</label>
                                    <input type="text" class="form-control" name="titulo" required 
                                           value="{{ libro_editar['titulo'] if libro_editar else '' }}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Autor</label>
                                    <input type="text" class="form-control" name="autor" required 
                                           value="{{ libro_editar['autor'] if libro_editar else '' }}">
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Año</label>
                                        <input type="number" class="form-control" name="anio" 
                                               value="{{ libro_editar['anio'] if libro_editar else '' }}">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">ISBN</label>
                                        <input type="text" class="form-control" name="isbn" 
                                               value="{{ libro_editar['isbn'] if libro_editar else '' }}">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Portada (Imagen)</label>
                                    <input type="file" class="form-control" name="portada_archivo" accept="image/*">
                                    {% if libro_editar and libro_editar['portada_data'] %}
                                        <div class="mt-2">
                                            <img src="{{ libro_editar['portada_data'] }}" class="preview-img">
                                            <div class="form-check mt-1">
                                                <input class="form-check-input" type="checkbox" name="borrar_imagen" id="borrar_img">
                                                <label class="form-check-label text-danger" for="borrar_img">Borrar imagen</label>
                                            </div>
                                        </div>
                                    {% endif %}
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Observaciones</label>
                                    <textarea class="form-control" name="observaciones" rows="3">{{ libro_editar['observaciones'] if libro_editar and libro_editar['observaciones'] else '' }}</textarea>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-primary">
                                        {% if libro_editar %} Actualizar {% else %} Guardar {% endif %}
                                    </button>
                                    {% if libro_editar %}
                                        <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancelar</a>
                                    {% endif %}
                                </div>
                            </form>
                        </div>
                    </div>

                {% else %}
                    <!-- MODO BÚSQUEDA: Formulario de Filtros -->
                    <div class="card bg-light border-primary sticky-top" style="top: 20px;">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0"><i class="fas fa-search"></i> Filtros de Búsqueda</h5>
                        </div>
                        <div class="card-body">
                            <form action="{{ url_for('pagina_buscar') }}" method="GET">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Buscar por:</label>
                                    <select name="criterio" class="form-select">
                                        <option value="titulo" {% if params_busqueda.criterio == 'titulo' %}selected{% endif %}>Título del Libro</option>
                                        <option value="autor" {% if params_busqueda.criterio == 'autor' %}selected{% endif %}>Nombre del Autor</option>
                                        <option value="anio" {% if params_busqueda.criterio == 'anio' %}selected{% endif %}>Año de Publicación</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Texto a buscar:</label>
                                    <input type="text" class="form-control" name="q" placeholder="Escribe aquí..." 
                                           value="{{ params_busqueda.q }}" autofocus>
                                    <div class="form-text">Puedes buscar por texto parcial.</div>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-primary"><i class="fas fa-search"></i> Buscar</button>
                                    <a href="{{ url_for('pagina_buscar') }}" class="btn btn-outline-secondary">Limpiar Filtros</a>
                                </div>
                            </form>
                        </div>
                    </div>
                {% endif %}
            </div>

            <!-- COLUMNA DERECHA: Tabla de Resultados -->
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0 text-secondary">
                            {% if modo == 'buscar' and params_busqueda.q %}
                                <i class="fas fa-filter"></i> Resultados: {{ total_items }} libros encontrados
                            {% else %}
                                <i class="fas fa-list"></i> Inventario Completo
                            {% endif %}
                        </h5>
                        <span class="badge bg-secondary">Página {{ page }} de {{ total_pages }}</span>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover table-striped mb-0 align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th style="width: 80px;">Portada</th>
                                        <th>Información</th>
                                        <th>Observaciones</th>
                                        <th class="text-end" style="width: 120px;">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for libro in libros %}
                                    <tr class="{% if modo == 'buscar' %}highlight{% endif %}">
                                        <td class="text-center p-2">
                                            {% if libro['portada_data'] %}
                                                <img src="{{ libro['portada_data'] }}" class="book-cover-thumb" alt="Portada">
                                            {% else %}
                                                <div class="book-cover-placeholder mx-auto"><i class="fas fa-book"></i></div>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <h6 class="mb-0 fw-bold">{{ libro['titulo'] }}</h6>
                                            <small class="text-muted d-block">{{ libro['autor'] }}</small>
                                            <small class="text-muted">
                                                {% if libro['anio'] %}{{ libro['anio'] }}{% endif %} 
                                                {% if libro['isbn'] %}| {{ libro['isbn'] }}{% endif %}
                                            </small>
                                        </td>
                                        <td>
                                            <small class="text-muted">{{ libro['observaciones'] if libro['observaciones'] else '-' }}</small>
                                        </td>
                                        <td class="text-end">
                                            <a href="{{ url_for('editar_libro', id=libro['id']) }}" class="btn btn-sm btn-outline-warning table-action-btn">
                                                <i class="fas fa-pencil-alt"></i>
                                            </a>
                                            <a href="{{ url_for('borrar_libro', id=libro['id']) }}" class="btn btn-sm btn-outline-danger table-action-btn" 
                                               onclick="return confirm('¿Estás seguro?');">
                                                <i class="fas fa-trash"></i>
                                            </a>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="4" class="text-center py-5 text-muted">
                                            {% if modo == 'buscar' %}
                                                <i class="fas fa-search-minus fa-3x mb-3 d-block"></i>
                                                No se encontraron resultados para tu búsqueda.
                                            {% else %}
                                                <i class="fas fa-book-open fa-3x mb-3 d-block"></i>
                                                La biblioteca está vacía.
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Paginación -->
                    <div class="card-footer bg-white border-top-0 py-3">
                        <nav aria-label="Navegación de páginas">
                            <ul class="pagination justify-content-center mb-0">
                                <!-- Generamos la URL base dependiendo de si estamos buscando o no -->
                                {% set endpoint = 'pagina_buscar' if modo == 'buscar' else 'index' %}
                                
                                <li class="page-item {% if page <= 1 %}disabled{% endif %}">
                                    <a class="page-link" href="{{ url_for(endpoint, page=page-1, q=params_busqueda.q, criterio=params_busqueda.criterio) }}">
                                        <i class="fas fa-chevron-left"></i> Anterior
                                    </a>
                                </li>
                                <li class="page-item disabled">
                                    <span class="page-link text-muted">
                                        Página {{ page }} / {{ total_pages }}
                                    </span>
                                </li>
                                <li class="page-item {% if page >= total_pages %}disabled{% endif %}">
                                    <a class="page-link" href="{{ url_for(endpoint, page=page+1, q=params_busqueda.q, criterio=params_busqueda.criterio) }}">
                                        Siguiente <i class="fas fa-chevron-right"></i>
                                    </a>
                                </li>
                            </ul>
                        </nav>
                    </div>
                    
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# --- Rutas del Servidor ---

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    libros, total_pages, current_page, total_items = get_libros_paginados(page)
    
    return render_template_string(HTML_TEMPLATE, 
                                  modo='inventario',
                                  libros=libros, 
                                  libro_editar=None,
                                  page=current_page,
                                  total_pages=total_pages,
                                  total_items=total_items,
                                  params_busqueda={}) # Vacío en modo inventario

@app.route('/buscar')
def pagina_buscar():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    criterio = request.args.get('criterio', 'titulo')
    
    # Llamamos a la función con los filtros
    libros, total_pages, current_page, total_items = get_libros_paginados(page, busqueda=q, criterio=criterio)
    
    return render_template_string(HTML_TEMPLATE, 
                                  modo='buscar',
                                  libros=libros, 
                                  libro_editar=None,
                                  page=current_page,
                                  total_pages=total_pages,
                                  total_items=total_items,
                                  params_busqueda={'q': q, 'criterio': criterio})

@app.route('/guardar', methods=['POST'])
def guardar_libro():
    id_libro = request.form.get('id')
    titulo = request.form['titulo']
    autor = request.form['autor']
    anio = request.form['anio']
    isbn = request.form['isbn']
    observaciones = request.form.get('observaciones', '')
    
    portada_b64 = None
    archivo = request.files.get('portada_archivo')
    
    if archivo and archivo.filename != '':
        try:
            contenido = archivo.read()
            base64_str = base64.b64encode(contenido).decode('utf-8')
            mime_type = archivo.mimetype or 'image/jpeg'
            portada_b64 = f"data:{mime_type};base64,{base64_str}"
        except Exception as e:
            flash('Error al procesar la imagen.', 'danger')

    conn = get_db_connection()
    
    if id_libro:
        if portada_b64:
            conn.execute('''UPDATE libros SET titulo=?, autor=?, anio=?, isbn=?, observaciones=?, portada_data=? WHERE id=?''', 
                         (titulo, autor, anio, isbn, observaciones, portada_b64, id_libro))
        elif request.form.get('borrar_imagen'):
            conn.execute('''UPDATE libros SET titulo=?, autor=?, anio=?, isbn=?, observaciones=?, portada_data=NULL WHERE id=?''', 
                         (titulo, autor, anio, isbn, observaciones, id_libro))
        else:
            conn.execute('''UPDATE libros SET titulo=?, autor=?, anio=?, isbn=?, observaciones=? WHERE id=?''', 
                         (titulo, autor, anio, isbn, observaciones, id_libro))
        flash('¡Libro actualizado!', 'success')
    else:
        conn.execute('''INSERT INTO libros (titulo, autor, anio, isbn, observaciones, portada_data) VALUES (?, ?, ?, ?, ?, ?)''', 
                     (titulo, autor, anio, isbn, observaciones, portada_b64))
        flash('¡Libro añadido!', 'success')
        
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar_libro(id):
    # Al editar, volvemos al modo inventario
    page = request.args.get('page', 1, type=int)
    libros, total_pages, current_page, total_items = get_libros_paginados(page)
    
    conn = get_db_connection()
    libro_editar = conn.execute('SELECT * FROM libros WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if libro_editar is None:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('index'))
        
    return render_template_string(HTML_TEMPLATE, 
                                  modo='inventario',
                                  libros=libros, 
                                  libro_editar=libro_editar,
                                  page=current_page,
                                  total_pages=total_pages,
                                  total_items=total_items,
                                  params_busqueda={})

@app.route('/borrar/<int:id>')
def borrar_libro(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM libros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Libro eliminado.', 'warning')
    # Intenta volver a la página de donde vino (por si estabas buscando)
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='192.168.0.17', port=5000, debug=True)