import sqlite3
import base64
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash
import json
import os

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = 'super_secret_key_mantenimiento_factory'
DB_NAME = 'mantenimiento_factory.db'

# --- CAPA DE DATOS (DATABASE LAYER) ---

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Tabla Tipos de Equipo
    c.execute('''CREATE TABLE IF NOT EXISTS tipos_equipo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL
                )''')
    
    # Insertar tipos por defecto si no existen
    defaults = ['Obra Civil', 'Instalaciones Eléctricas', 'Instalaciones Hidráulicas']
    for d in defaults:
        try:
            c.execute("INSERT INTO tipos_equipo (nombre) VALUES (?)", (d,))
        except sqlite3.IntegrityError:
            pass

    # Tabla Inventario
    c.execute('''CREATE TABLE IF NOT EXISTS inventario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo_id INTEGER NOT NULL,
                    descripcion TEXT,
                    images TEXT, 
                    pdfs TEXT,
                    FOREIGN KEY (tipo_id) REFERENCES tipos_equipo (id)
                )''')

    # Tabla Actividades
    c.execute('''CREATE TABLE IF NOT EXISTS actividades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    equipo_id INTEGER NOT NULL,
                    periodicidad INTEGER NOT NULL, -- en días
                    operaciones TEXT,
                    fecha_inicio_gen DATE NOT NULL,
                    FOREIGN KEY (equipo_id) REFERENCES inventario (id)
                )''')

    # Tabla Ordenes de Trabajo
    c.execute('''CREATE TABLE IF NOT EXISTS ordenes_trabajo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actividad_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    fecha_generacion DATE NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'En curso', 
                    observaciones TEXT,
                    fecha_realizada DATE,
                    FOREIGN KEY (actividad_id) REFERENCES actividades (id)
                )''')
    
    # Tabla Correctivos / Incidencias
    c.execute('''CREATE TABLE IF NOT EXISTS correctivos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    equipo_id INTEGER NOT NULL,
                    comentario TEXT,
                    solucion TEXT,
                    estado TEXT NOT NULL DEFAULT 'Detectada',
                    fecha_detectada DATE NOT NULL,
                    fecha_resolucion DATE,
                    images TEXT, 
                    pdfs TEXT,
                    FOREIGN KEY (equipo_id) REFERENCES inventario (id)
                )''')
    
    # Tabla Configuración Fecha Sistema
    c.execute('''CREATE TABLE IF NOT EXISTS configuracion (
                    id INTEGER PRIMARY KEY,
                    fecha_sistema DATE
                )''')
    
    # Inicializar fecha del sistema con la fecha real si no existe
    try:
        c.execute("INSERT INTO configuracion (id, fecha_sistema) VALUES (1, ?)", (datetime.date.today(),))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

# --- UTILIDADES ---

def get_system_date():
    try:
        conn = get_db_connection()
        row = conn.execute('SELECT fecha_sistema FROM configuracion WHERE id=1').fetchone()
        conn.close()
        if row and row['fecha_sistema']:
            return datetime.datetime.strptime(row['fecha_sistema'], '%Y-%m-%d').date()
    except:
        pass
    return datetime.date.today()

def allowed_file_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file_pdf(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def file_to_base64(file):
    return base64.b64encode(file.read()).decode('utf-8')

def normalize_files(file_list):
    normalized = []
    if not file_list:
        return []
    for item in file_list:
        if isinstance(item, str):
            normalized.append({'name': 'Archivo existente (Legacy)', 'data': item})
        elif isinstance(item, dict):
            normalized.append(item)
    return normalized

def get_cronograma_data(conn, year):
    actividades = conn.execute('''
        SELECT a.id, a.nombre, i.nombre as equipo_nombre
        FROM actividades a
        JOIN inventario i ON a.equipo_id = i.id
    ''').fetchall()
    
    cronograma_data = []
    
    for act in actividades:
        row = {
            'actividad': act['nombre'],
            'equipo': act['equipo_nombre'],
            'ots': {}
        }
        
        ots = conn.execute('''
            SELECT ot.id, ot.nombre, ot.fecha_generacion, ot.estado, 
                   ot.observaciones, ot.fecha_realizada, a.operaciones
            FROM ordenes_trabajo ot
            JOIN actividades a ON ot.actividad_id = a.id
            WHERE ot.actividad_id = ? AND strftime('%Y', ot.fecha_generacion) = ?
        ''', (act['id'], str(year))).fetchall()
        
        for ot in ots:
            fecha = datetime.datetime.strptime(ot['fecha_generacion'], '%Y-%m-%d')
            mes_idx = fecha.month
            
            if mes_idx not in row['ots']:
                row['ots'][mes_idx] = []
            
            row['ots'][mes_idx].append({
                'id': ot['id'],
                'nombre': ot['nombre'],
                'estado': ot['estado'],
                'day_day': fecha.day,
                'fecha': ot['fecha_generacion'],
                'operaciones': ot['operaciones'],
                'observaciones': ot['observaciones'],
                'fecha_realizada': ot['fecha_realizada']
            })
            
        cronograma_data.append(row)
    return cronograma_data

# --- TEMPLATES HTML ---

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GMAO Factory - Gestión de Mantenimiento</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .sidebar { min-height: 100vh; background-color: #2c3e50; color: white; }
        .sidebar a { color: #bdc3c7; text-decoration: none; display: block; padding: 10px; }
        .sidebar a:hover, .sidebar a.active { background-color: #34495e; color: white; border-left: 4px solid #3498db; }
        .content { padding: 20px; }
        /* COLORES DE ESTADO GENERAL */
        .status-realizada { background-color: #198754; color: white; } /* Verde */
        .status-en-curso { background-color: #ffc107; color: #212529; } /* Amarillo */
        .status-rechazada { background-color: #000000; color: white; } /* Negro */
        .status-pendiente { background-color: #dc3545; color: white; } /* Rojo (Vencida) */
        .status-prevista { background-color: #6c757d; color: white; } /* Gris (Futura) */
        
        /* COLORES DE ESTADO CORRECTIVO */
        .corr-detectada { background-color: #dc3545; color: white; } /* Rojo */
        .corr-en-curso { background-color: #ffc107; color: #212529; } /* Amarillo */
        .corr-resuelta { background-color: #198754; color: white; } /* Verde */

        .badge-status { font-size: 0.8em; padding: 5px; border-radius: 4px; display: inline-block; margin-bottom: 2px; cursor: pointer; transition: transform 0.1s; }
        .badge-status:hover { transform: scale(1.1); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .img-thumb { width: 50px; height: 50px; object-fit: cover; cursor: pointer; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 d-none d-md-block sidebar p-0">
                <div class="p-3 text-center">
                    <h4>🏭 GMAO Factory</h4>
                    <small>Arquitectura v3.5</small>
                </div>
                <div class="mt-4">
                    <a href="{{ url_for('index') }}" class="{{ 'active' if active_page == 'inventario' else '' }}"><i class="fas fa-boxes me-2"></i> Inventario</a>
                    <a href="{{ url_for('activities') }}" class="{{ 'active' if active_page == 'actividades' else '' }}"><i class="fas fa-clipboard-list me-2"></i> Actividades</a>
                    <a href="{{ url_for('work_orders') }}" class="{{ 'active' if active_page == 'ots' else '' }}"><i class="fas fa-tools me-2"></i> Órdenes de Trabajo</a>
                    <a href="{{ url_for('cronograma') }}" class="{{ 'active' if active_page == 'cronograma' else '' }}"><i class="fas fa-calendar-alt me-2"></i> Cronogramas de Ordenes de Trabajo</a>
                    <a href="{{ url_for('correctivos') }}" class="{{ 'active' if active_page == 'correctivos' else '' }}"><i class="fas fa-exclamation-triangle me-2"></i> Correctivos</a>
                    <hr>
                    <a href="{{ url_for('configuration') }}" class="{{ 'active' if active_page == 'configuracion' else '' }}"><i class="fas fa-tags me-2"></i> Configuración de tipos</a>
                    <a href="{{ url_for('system_date_config') }}" class="{{ 'active' if active_page == 'fecha_sistema' else '' }}"><i class="fas fa-clock me-2"></i> Fecha del Sistema</a>
                </div>
            </nav>
            <main class="col-md-10 ms-sm-auto col-lg-10 content">
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
                
                <div class="alert alert-secondary py-1 px-3 mb-3 d-flex justify-content-between align-items-center">
                    <small><i class="fas fa-calendar-day"></i> Fecha Sistema: <strong>{{ system_date }}</strong></small>
                </div>

                <!-- CONTENT_PLACEHOLDER -->
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

INVENTARIO_TEMPLATE = """
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Inventario de Equipos</h1>
    <div>
        <a href="{{ url_for('print_all_inventory', f_nombre=f_nombre, f_tipo=f_tipo) }}" class="btn btn-secondary btn-sm me-2" target="_blank"><i class="fas fa-print"></i> Imprimir Tabla</a>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addEquipModal">+ Nuevo Equipo</button>
    </div>
</div>

<div class="card mb-3"><div class="card-body py-3"><form action="{{ url_for('index') }}" method="GET" class="row g-2 align-items-end"><div class="col-md-4"><label class="form-label small mb-1">Nombre Equipo</label><input type="text" class="form-control form-control-sm" name="f_nombre" value="{{ f_nombre }}" placeholder="Buscar..."></div><div class="col-md-4"><label class="form-label small mb-1">Tipo</label><select class="form-select form-select-sm" name="f_tipo"><option value="">Todos</option>{% for t in tipos %}<option value="{{ t.id }}" {{ 'selected' if f_tipo|string == t.id|string }}>{{ t.nombre }}</option>{% endfor %}</select></div><div class="col-md-4 d-flex gap-2"><button type="submit" class="btn btn-primary btn-sm w-100"><i class="fas fa-filter"></i> Filtrar</button><a href="{{ url_for('index') }}" class="btn btn-outline-secondary btn-sm"><i class="fas fa-times"></i> Limpiar</a></div></form></div></div>

<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead class="table-dark">
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>Descripción</th>
                <th>Archivos</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.id }}</td>
                <td>{{ item.nombre }}</td>
                <td>{{ item.tipo_nombre }}</td>
                <td>{{ item.descripcion }}</td>
                <td>
                    {% set imgs = item.images|json_load %}
                    {% if imgs %}
                        <button class="btn btn-info btn-sm btn-xs" onclick="verGaleria('inventory', 'img', '{{ item.id }}')"><i class="fas fa-images"></i> {{ imgs|length }}</button>
                    {% endif %}
                    {% set pdfs = item.pdfs|json_load %}
                    {% if pdfs %}
                        <button class="btn btn-danger btn-sm btn-xs" onclick="verGaleria('inventory', 'pdf', '{{ item.id }}')"><i class="fas fa-file-pdf"></i> {{ pdfs|length }}</button>
                    {% endif %}
                </td>
                <td>
                   <a href="{{ url_for('print_inventory', id=item.id) }}" class="btn btn-sm btn-secondary" target="_blank" title="Imprimir PDF"><i class="fas fa-print"></i></a>
                   <a href="{{ url_for('edit_inventory', id=item.id) }}" class="btn btn-sm btn-warning" title="Editar"><i class="fas fa-edit"></i></a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<nav>
  <ul class="pagination justify-content-center">
    {% if page > 1 %}
    <li class="page-item"><a class="page-link" href="{{ url_for('index', page=page-1, f_nombre=f_nombre, f_tipo=f_tipo) }}">Anterior</a></li>
    {% endif %}
    <li class="page-item disabled"><span class="page-link">Página {{ page }}</span></li>
    {% if has_next %}
    <li class="page-item"><a class="page-link" href="{{ url_for('index', page=page+1, f_nombre=f_nombre, f_tipo=f_tipo) }}">Siguiente</a></li>
    {% endif %}
  </ul>
</nav>

<div class="modal fade" id="addEquipModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <form action="{{ url_for('add_inventory') }}" method="POST" enctype="multipart/form-data">
                <div class="modal-header">
                    <h5 class="modal-title">Añadir Equipo</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Nombre</label>
                        <input type="text" class="form-control" name="nombre" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Tipo</label>
                        <select class="form-select" name="tipo_id" required>
                            {% for t in tipos %}
                            <option value="{{ t.id }}">{{ t.nombre }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Descripción</label>
                        <textarea class="form-control" name="descripcion" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Imágenes (Máx 5)</label>
                        <input type="file" class="form-control" name="images" multiple accept="image/*">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">PDFs (Máx 5)</label>
                        <input type="file" class="form-control" name="pdfs" multiple accept="application/pdf">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="submit" class="btn btn-primary">Guardar</button>
                </div>
            </form>
        </div>
    </div>
</div>
<script>
function verGaleria(source, tipo, id) {
    window.location.href = "/view_files/" + source + "/" + tipo + "/" + id;
}
</script>
"""

EDIT_INVENTORY_TEMPLATE = """
<h2>Editar Equipo: {{ item.nombre }}</h2>
<form action="{{ url_for('update_inventory', id=item.id) }}" method="POST" enctype="multipart/form-data" class="mt-4">
    <div class="row">
        <div class="col-md-7">
            <div class="mb-3">
                <label class="form-label">Nombre</label>
                <input type="text" class="form-control" name="nombre" value="{{ item.nombre }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Tipo</label>
                <select class="form-select" name="tipo_id" required>
                    {% for t in tipos %}
                    <option value="{{ t.id }}" {{ 'selected' if t.id == item.tipo_id }}>{{ t.nombre }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Descripción</label>
                <textarea class="form-control" name="descripcion" rows="3">{{ item.descripcion }}</textarea>
            </div>
        </div>
        <div class="col-md-5">
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Imágenes ({{ imgs|length }}/5)</span>
                    <small>Selecciona para borrar</small>
                </div>
                <div class="card-body">
                    {% if imgs %}
                    <div class="list-group mb-3">
                        {% for img in imgs %}
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div class="text-truncate" style="max-width: 200px;" title="{{ img.name }}">{{ img.name }}</div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="delete_images" value="{{ loop.index0 }}">
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    {% if imgs|length < 5 %}
                        <input type="file" class="form-control form-control-sm" name="images" multiple accept="image/*">
                    {% endif %}
                </div>
            </div>
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>PDFs ({{ pdfs|length }}/5)</span>
                    <small>Selecciona para borrar</small>
                </div>
                <div class="card-body">
                    {% if pdfs %}
                    <div class="list-group mb-3">
                        {% for pdf in pdfs %}
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div class="text-truncate" style="max-width: 200px;" title="{{ pdf.name }}">{{ pdf.name }}</div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="delete_pdfs" value="{{ loop.index0 }}">
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    {% if pdfs|length < 5 %}
                        <input type="file" class="form-control form-control-sm" name="pdfs" multiple accept="application/pdf">
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    <hr>
    <div class="d-flex justify-content-end gap-2">
        <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancelar</a>
        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
    </div>
</form>
"""

ACTIVIDADES_TEMPLATE = """
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Gestión de Actividades</h1>
    <div>
        <button class="btn btn-primary btn-sm me-2" type="button" data-bs-toggle="collapse" data-bs-target="#formNuevaActividad">
            <i class="fas fa-plus"></i> Nueva Actividad
        </button>
        <a href="{{ url_for('print_all_activities') }}" class="btn btn-secondary btn-sm" target="_blank"><i class="fas fa-print"></i> Imprimir Tabla</a>
    </div>
</div>

<div class="collapse mb-4" id="formNuevaActividad">
    <div class="card card-body bg-light">
        <h5 class="card-title mb-3">Registrar Nueva Actividad</h5>
        <form action="{{ url_for('add_activity') }}" method="POST" class="row g-3">
            <div class="col-md-4">
                <label class="form-label">Nombre Actividad</label>
                <input type="text" class="form-control" name="nombre" required>
            </div>
            <div class="col-md-4">
                <label class="form-label">Equipo Asociado</label>
                <select class="form-select" name="equipo_id" required>
                    {% for eq in equipos %}
                    <option value="{{ eq.id }}">{{ eq.nombre }} ({{ eq.tipo_nombre }})</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Periodicidad (días)</label>
                <input type="number" class="form-control" name="periodicidad" required min="1">
            </div>
            <div class="col-md-2">
                <label class="form-label">Inicio Generación</label>
                <input type="date" class="form-control" name="fecha_inicio" required>
            </div>
            <div class="col-12">
                <label class="form-label">Operaciones a realizar</label>
                <textarea class="form-control" name="operaciones" rows="2" required></textarea>
            </div>
            <div class="col-12 text-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-toggle="collapse" data-bs-target="#formNuevaActividad">Cancelar</button>
                <button type="submit" class="btn btn-success">Crear Actividad</button>
            </div>
        </form>
    </div>
</div>

<div class="card mb-3">
    <div class="card-body py-3">
        <form action="{{ url_for('activities') }}" method="GET" class="row g-2 align-items-end">
            <div class="col-md-3"><label class="form-label small mb-1">Nombre</label><input type="text" class="form-control form-control-sm" name="f_nombre" value="{{ f_nombre }}" placeholder="Buscar..."></div>
            <div class="col-md-3"><label class="form-label small mb-1">Equipo</label><select class="form-select form-select-sm" name="f_equipo"><option value="">Todos</option>{% for eq in equipos %}<option value="{{ eq.id }}" {{ 'selected' if f_equipo|string == eq.id|string }}>{{ eq.nombre }}</option>{% endfor %}</select></div>
            <div class="col-md-2"><label class="form-label small mb-1">Frecuencia</label><input type="number" class="form-control form-control-sm" name="f_periodicidad" value="{{ f_periodicidad }}"></div>
            <div class="col-md-4 d-flex gap-2"><button type="submit" class="btn btn-primary btn-sm w-100"><i class="fas fa-filter"></i> Filtrar</button><a href="{{ url_for('activities') }}" class="btn btn-outline-secondary btn-sm"><i class="fas fa-times"></i> Limpiar</a></div>
        </form>
    </div>
</div>

<div class="table-responsive">
    <table class="table table-bordered">
        <thead class="table-light">
            <tr>
                <th>Actividad</th>
                <th>Equipo</th>
                <th>Frecuencia</th>
                <th>Inicio</th>
                <th>Operaciones</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for act in actividades %}
            <tr>
                <td>{{ act.nombre }}</td>
                <td>{{ act.equipo_nombre }}</td>
                <td>Cada {{ act.periodicidad }} días</td>
                <td>{{ act.fecha_inicio_gen }}</td>
                <td><small>{{ act.operaciones }}</small></td>
                <td>
                    <a href="{{ url_for('print_activity_single', id=act.id) }}" class="btn btn-sm btn-secondary" target="_blank" title="Imprimir PDF"><i class="fas fa-print"></i></a>
                    <a href="{{ url_for('edit_activity', id=act.id) }}" class="btn btn-sm btn-warning"><i class="fas fa-edit"></i></a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
"""

EDIT_ACTIVITY_TEMPLATE = """
<h2>Editar Actividad: {{ activity.nombre }}</h2>
<form action="{{ url_for('update_activity', id=activity.id) }}" method="POST" class="row g-3 mt-4">
    <div class="col-md-4"><label class="form-label">Nombre</label><input type="text" class="form-control" name="nombre" value="{{ activity.nombre }}" required></div>
    <div class="col-md-4"><label class="form-label">Equipo</label><select class="form-select" name="equipo_id" required>{% for eq in equipos %}<option value="{{ eq.id }}" {{ 'selected' if eq.id == activity.equipo_id }}>{{ eq.nombre }}</option>{% endfor %}</select></div>
    <div class="col-md-2"><label class="form-label">Periodicidad</label><input type="number" class="form-control" name="periodicidad" value="{{ activity.periodicidad }}" required></div>
    <div class="col-md-2"><label class="form-label">Inicio</label><input type="date" class="form-control" name="fecha_inicio" value="{{ activity.fecha_inicio_gen }}" required></div>
    <div class="col-12"><label class="form-label">Operaciones</label><textarea class="form-control" name="operaciones" rows="2" required>{{ activity.operaciones }}</textarea></div>
    <div class="col-12 d-flex justify-content-end gap-2"><a href="{{ url_for('activities') }}" class="btn btn-secondary">Cancelar</a><button type="submit" class="btn btn-primary">Guardar</button></div>
</form>
"""

OTS_TEMPLATE = """
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Órdenes de Trabajo (OTs)</h1>
    <div class="d-flex gap-2">
        <a href="{{ url_for('print_all_ots', estado=estado_filter, fecha_inicio=fecha_inicio_filter, fecha_fin=fecha_fin_filter) }}" class="btn btn-secondary" target="_blank"><i class="fas fa-print"></i> Imprimir Tabla</a>
        <form action="{{ url_for('generate_work_orders') }}" method="POST">
            <button type="submit" class="btn btn-warning"><i class="fas fa-sync-alt"></i> Generar OTs Pendientes</button>
        </form>
    </div>
</div>

<div class="card mb-3">
    <div class="card-body">
        <form action="{{ url_for('work_orders') }}" method="GET" class="row g-3 align-items-end">
            <div class="col-md-3">
                <label class="form-label">Estado</label>
                <select class="form-select" name="estado">
                    <option value="">Todos</option>
                    <option value="En curso" {{ 'selected' if estado_filter == 'En curso' }}>En curso</option>
                    <option value="Pendiente" {{ 'selected' if estado_filter == 'Pendiente' }}>Pendiente</option>
                    <option value="Prevista" {{ 'selected' if estado_filter == 'Prevista' }}>Prevista</option>
                    <option value="Realizada" {{ 'selected' if estado_filter == 'Realizada' }}>Realizada</option>
                    <option value="Rechazada" {{ 'selected' if estado_filter == 'Rechazada' }}>Rechazada</option>
                </select>
            </div>
            <div class="col-md-3"><label class="form-label">Desde</label><input type="date" class="form-control" name="fecha_inicio" value="{{ fecha_inicio_filter }}"></div>
            <div class="col-md-3"><label class="form-label">Hasta</label><input type="date" class="form-control" name="fecha_fin" value="{{ fecha_fin_filter }}"></div>
            <div class="col-md-3"><button type="submit" class="btn btn-primary w-100"><i class="fas fa-filter"></i> Filtrar</button></div>
        </form>
    </div>
</div>

<div class="table-responsive">
    <table class="table table-hover align-middle">
        <thead class="table-dark">
            <tr>
                <th>ID</th>
                <th>Nombre OT</th>
                <th>Equipo</th>
                <th>Fecha Gen.</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for ot in ots %}
            <tr>
                <td>{{ ot.id }}</td>
                <td>{{ ot.nombre }}</td>
                <td>{{ ot.equipo_nombre }}</td>
                <td>{{ ot.fecha_generacion }}</td>
                <td>
                    {% if ot.estado == 'Realizada' %}<span class="badge bg-success">Realizada</span>
                    {% elif ot.estado == 'En curso' %}<span class="badge bg-warning text-dark">En curso</span>
                    {% elif ot.estado == 'Pendiente' %}<span class="badge bg-danger">Pendiente</span>
                    {% elif ot.estado == 'Prevista' %}<span class="badge bg-secondary">Prevista</span>
                    {% else %}<span class="badge bg-dark">Rechazada</span>{% endif %}
                </td>
                <td>
                    <a href="{{ url_for('print_ot', id=ot.id) }}" class="btn btn-sm btn-secondary" target="_blank"><i class="fas fa-print"></i></a>
                    <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#modalOT{{ ot.id }}">Gestionar</button>
                </td>
            </tr>
            <div class="modal fade" id="modalOT{{ ot.id }}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form action="{{ url_for('update_ot', id=ot.id) }}" method="POST">
                            <div class="modal-header"><h5 class="modal-title">{{ ot.nombre }}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                            <div class="modal-body">
                                <div class="alert alert-secondary"><strong>Operaciones:</strong><br>{{ ot.operaciones }}</div>
                                <div class="mb-3">
                                    <label class="form-label">Estado</label>
                                    <select class="form-select" name="estado">
                                        <option value="En curso" {{ 'selected' if ot.estado == 'En curso' }}>En curso</option>
                                        <option value="Pendiente" {{ 'selected' if ot.estado == 'Pendiente' }}>Pendiente</option>
                                        <option value="Prevista" {{ 'selected' if ot.estado == 'Prevista' }}>Prevista</option>
                                        <option value="Realizada" {{ 'selected' if ot.estado == 'Realizada' }}>Realizada</option>
                                        <option value="Rechazada" {{ 'selected' if ot.estado == 'Rechazada' }}>Rechazada</option>
                                    </select>
                                </div>
                                <div class="mb-3"><label class="form-label">Observaciones</label><textarea class="form-control" name="observaciones">{{ ot.observaciones }}</textarea></div>
                                <div class="mb-3"><label class="form-label">Fecha Realización</label><input type="date" class="form-control" name="fecha_realizada" value="{{ ot.fecha_realizada }}"></div>
                            </div>
                            <div class="modal-footer"><button type="submit" class="btn btn-primary">Actualizar OT</button></div>
                        </form>
                    </div>
                </div>
            </div>
            {% endfor %}
        </tbody>
    </table>
</div>

<nav>
  <ul class="pagination justify-content-center">
    {% if page > 1 %}
    <li class="page-item"><a class="page-link" href="{{ url_for('work_orders', page=page-1, estado=estado_filter, fecha_inicio=fecha_inicio_filter, fecha_fin=fecha_fin_filter) }}">Anterior</a></li>
    {% endif %}
    <li class="page-item disabled"><span class="page-link">Página {{ page }}</span></li>
    {% if has_next %}
    <li class="page-item"><a class="page-link" href="{{ url_for('work_orders', page=page+1, estado=estado_filter, fecha_inicio=fecha_inicio_filter, fecha_fin=fecha_fin_filter) }}">Siguiente</a></li>
    {% endif %}
  </ul>
</nav>
"""

CRONOGRAMA_TEMPLATE = """
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Cronogramas de Ordenes de Trabajo {{ year }}</h1>
    <div class="d-flex align-items-center gap-3">
        <form action="{{ url_for('cronograma') }}" method="GET" class="d-flex align-items-center">
            <label for="yearSelect" class="me-2 fw-bold">Año:</label>
            <input type="number" id="yearSelect" name="year" class="form-control" value="{{ year }}" style="width: 100px;" onchange="this.form.submit()">
            <button type="submit" class="btn btn-primary btn-sm ms-2">Ir</button>
        </form>
        <a href="{{ url_for('print_cronograma', year=year) }}" target="_blank" class="btn btn-secondary"><i class="fas fa-print"></i> Imprimir PDF</a>
    </div>
</div>

<div class="table-responsive">
    <table class="table table-bordered table-sm text-center">
        <thead class="table-dark">
            <tr>
                <th style="width: 200px;">Actividad / Equipo</th>
                {% for m in meses %}<th>{{ m }}</th>{% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td class="text-start bg-light fw-bold">{{ row.actividad }}<br><small class="text-muted">{{ row.equipo }}</small></td>
                {% for month_idx in range(1, 13) %}
                <td style="vertical-align: top;">
                    {% if month_idx in row.ots %}
                        {% for ot in row.ots[month_idx] %}
                        <div class="badge-status 
                            {% if ot.estado == 'Realizada' %}status-realizada
                            {% elif ot.estado == 'En curso' %}status-en-curso
                            {% elif ot.estado == 'Pendiente' %}status-pendiente
                            {% elif ot.estado == 'Prevista' %}status-prevista
                            {% else %}status-rechazada{% endif %}"
                            title="{{ ot.nombre }} ({{ ot.fecha }})"
                            data-bs-toggle="modal" data-bs-target="#cronModalOT{{ ot.id }}">
                            {{ ot.day_day }}
                        </div>
                        <div class="modal fade text-start" id="cronModalOT{{ ot.id }}" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <form action="{{ url_for('update_ot', id=ot.id) }}" method="POST">
                                        <div class="modal-header"><h5 class="modal-title">{{ ot.nombre }}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                        <div class="modal-body">
                                            <input type="hidden" name="redirect_to" value="cronograma">
                                            <div class="alert alert-secondary"><strong>Operaciones:</strong><br>{{ ot.operaciones }}</div>
                                            <div class="mb-3">
                                                <label class="form-label">Estado</label>
                                                <select class="form-select" name="estado">
                                                    <option value="En curso" {{ 'selected' if ot.estado == 'En curso' }}>En curso</option>
                                                    <option value="Pendiente" {{ 'selected' if ot.estado == 'Pendiente' }}>Pendiente</option>
                                                    <option value="Prevista" {{ 'selected' if ot.estado == 'Prevista' }}>Prevista</option>
                                                    <option value="Realizada" {{ 'selected' if ot.estado == 'Realizada' }}>Realizada</option>
                                                    <option value="Rechazada" {{ 'selected' if ot.estado == 'Rechazada' }}>Rechazada</option>
                                                </select>
                                            </div>
                                            <div class="mb-3"><label class="form-label">Observaciones</label><textarea class="form-control" name="observaciones">{{ ot.observaciones or '' }}</textarea></div>
                                            <div class="mb-3"><label class="form-label">Fecha Realización</label><input type="date" class="form-control" name="fecha_realizada" value="{{ ot.fecha_realizada or '' }}"></div>
                                        </div>
                                        <div class="modal-footer"><button type="submit" class="btn btn-primary">Actualizar OT</button></div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}
                </td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<div class="mt-3">
    <small>Leyenda: <span class="badge bg-success">Realizada</span> <span class="badge bg-warning text-dark">En Curso</span> <span class="badge bg-danger">Pendiente</span> <span class="badge bg-secondary">Prevista</span> <span class="badge bg-dark">Rechazada</span>. El número indica el día del mes. Haz click para editar.</small>
</div>
"""

CORRECTIVOS_TEMPLATE = """
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Correctivos e Incidencias</h1>
    <div>
        <button class="btn btn-primary btn-sm me-2" type="button" data-bs-toggle="collapse" data-bs-target="#formNuevoCorrectivo">
            <i class="fas fa-plus"></i> Nueva Incidencia
        </button>
        <a href="{{ url_for('print_all_correctivos', f_nombre=f_nombre, f_equipo=f_equipo, f_estado=f_estado, f_fecha_desde=f_fecha_desde, f_fecha_hasta=f_fecha_hasta) }}" class="btn btn-secondary btn-sm" target="_blank"><i class="fas fa-print"></i> Imprimir Tabla</a>
    </div>
</div>

<div class="collapse mb-4" id="formNuevoCorrectivo">
    <div class="card card-body bg-light">
        <h5 class="card-title mb-3">Registrar Nueva Incidencia</h5>
        <form action="{{ url_for('add_correctivo') }}" method="POST" enctype="multipart/form-data" class="row g-3">
            <div class="col-md-6"><label class="form-label">Nombre del Correctivo</label><input type="text" class="form-control" name="nombre" required></div>
            <div class="col-md-6"><label class="form-label">Equipo Afectado</label><select class="form-select" name="equipo_id" required>{% for eq in equipos %}<option value="{{ eq.id }}">{{ eq.nombre }} ({{ eq.tipo_nombre }})</option>{% endfor %}</select></div>
            <div class="col-12"><label class="form-label">Comentario</label><textarea class="form-control" name="comentario" rows="2"></textarea></div>
            <div class="col-md-3"><label class="form-label">Fecha Detectada</label><input type="date" class="form-control" name="fecha_detectada" value="{{ system_date }}" required></div>
            <div class="col-md-3"><label class="form-label">Estado Inicial</label><select class="form-select" name="estado"><option value="Detectada">Detectada</option><option value="En curso">En curso</option><option value="Resuelta">Resuelta</option></select></div>
             <div class="col-md-3"><label class="form-label">Imágenes</label><input type="file" class="form-control" name="images" multiple accept="image/*"></div>
            <div class="col-md-3"><label class="form-label">PDFs</label><input type="file" class="form-control" name="pdfs" multiple accept="application/pdf"></div>
            <div class="col-12 text-end"><button type="button" class="btn btn-secondary me-2" data-bs-toggle="collapse" data-bs-target="#formNuevoCorrectivo">Cancelar</button><button type="submit" class="btn btn-danger">Guardar Incidencia</button></div>
        </form>
    </div>
</div>

<div class="card mb-3">
    <div class="card-body py-3">
        <form action="{{ url_for('correctivos') }}" method="GET" class="row g-2 align-items-end">
            <div class="col-md-3"><label class="form-label small mb-1">Nombre</label><input type="text" class="form-control form-control-sm" name="f_nombre" value="{{ f_nombre }}" placeholder="Buscar..."></div>
            <div class="col-md-2"><label class="form-label small mb-1">Equipo</label><select class="form-select form-select-sm" name="f_equipo"><option value="">Todos</option>{% for eq in equipos %}<option value="{{ eq.id }}" {{ 'selected' if f_equipo|string == eq.id|string }}>{{ eq.nombre }}</option>{% endfor %}</select></div>
            <div class="col-md-2"><label class="form-label small mb-1">Estado</label><select class="form-select form-select-sm" name="f_estado"><option value="">Todos</option><option value="Detectada" {{ 'selected' if f_estado == 'Detectada' }}>Detectada</option><option value="En curso" {{ 'selected' if f_estado == 'En curso' }}>En curso</option><option value="Resuelta" {{ 'selected' if f_estado == 'Resuelta' }}>Resuelta</option></select></div>
            <div class="col-md-2"><label class="form-label small mb-1">Desde</label><input type="date" class="form-control form-control-sm" name="f_fecha_desde" value="{{ f_fecha_desde }}"></div>
            <div class="col-md-2 d-flex gap-2"><button type="submit" class="btn btn-primary btn-sm w-100"><i class="fas fa-filter"></i></button><a href="{{ url_for('correctivos') }}" class="btn btn-outline-secondary btn-sm"><i class="fas fa-times"></i></a></div>
        </form>
    </div>
</div>

<div class="table-responsive">
    <table class="table table-hover align-middle">
        <thead class="table-dark"><tr><th>ID</th><th>Incidencia</th><th>Equipo</th><th>Estado</th><th>Detectada</th><th>Resolución</th><th>Archivos</th><th>Acciones</th></tr></thead>
        <tbody>
            {% for c in correctivos %}
            <tr>
                <td>{{ c.id }}</td><td>{{ c.nombre }}</td><td>{{ c.equipo_nombre }}</td>
                <td>{% if c.estado == 'Detectada' %}<span class="badge corr-detectada">Detectada</span>{% elif c.estado == 'En curso' %}<span class="badge corr-en-curso">En curso</span>{% elif c.estado == 'Resuelta' %}<span class="badge corr-resuelta">Resuelta</span>{% endif %}</td>
                <td>{{ c.fecha_detectada }}</td><td>{{ c.fecha_resolucion or '-' }}</td>
                <td>
                    {% set imgs = c.images|json_load %}
                    {% if imgs %}
                        <button class="btn btn-info btn-sm btn-xs" onclick="verGaleria('corrective', 'img', '{{ c.id }}')"><i class="fas fa-images"></i> {{ imgs|length }}</button>
                    {% endif %}
                    {% set pdfs = c.pdfs|json_load %}
                    {% if pdfs %}
                        <button class="btn btn-danger btn-sm btn-xs" onclick="verGaleria('corrective', 'pdf', '{{ c.id }}')"><i class="fas fa-file-pdf"></i> {{ pdfs|length }}</button>
                    {% endif %}
                    {% if not imgs and not pdfs %}<small class="text-muted">-</small>{% endif %}
                </td>
                <td>
                    <a href="{{ url_for('print_correctivo', id=c.id) }}" class="btn btn-sm btn-secondary" target="_blank"><i class="fas fa-print"></i></a>
                    <a href="{{ url_for('edit_correctivo', id=c.id) }}" class="btn btn-sm btn-warning"><i class="fas fa-edit"></i></a>
                    <form action="{{ url_for('delete_correctivo', id=c.id) }}" method="POST" class="d-inline" onsubmit="return confirm('¿Borrar?');"><button type="submit" class="btn btn-sm btn-danger"><i class="fas fa-trash"></i></button></form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<script>
function verGaleria(source, tipo, id) {
    window.location.href = "/view_files/" + source + "/" + tipo + "/" + id;
}
</script>
"""

EDIT_CORRECTIVO_TEMPLATE = """
<h2>Editar Incidencia: {{ item.nombre }}</h2>
<form action="{{ url_for('update_correctivo', id=item.id) }}" method="POST" enctype="multipart/form-data" class="mt-4">
    <div class="row">
        <div class="col-md-6">
            <div class="mb-3"><label class="form-label">Nombre</label><input type="text" class="form-control" name="nombre" value="{{ item.nombre }}" required></div>
            <div class="mb-3"><label class="form-label">Equipo</label><select class="form-select" name="equipo_id" required>{% for eq in equipos %}<option value="{{ eq.id }}" {{ 'selected' if eq.id == item.equipo_id }}>{{ eq.nombre }}</option>{% endfor %}</select></div>
            <div class="mb-3"><label class="form-label">Comentario</label><textarea class="form-control" name="comentario" rows="3">{{ item.comentario }}</textarea></div>
            <div class="mb-3"><label class="form-label">Solución</label><textarea class="form-control" name="solucion" rows="3">{{ item.solucion }}</textarea></div>
        </div>
        <div class="col-md-6">
            <div class="row">
                 <div class="col-md-6 mb-3"><label class="form-label">Fecha Detectada</label><input type="date" class="form-control" name="fecha_detectada" value="{{ item.fecha_detectada }}" required></div>
                <div class="col-md-6 mb-3"><label class="form-label">Fecha Resolución</label><input type="date" class="form-control" name="fecha_resolucion" value="{{ item.fecha_resolucion or '' }}"></div>
                <div class="col-12 mb-3"><label class="form-label">Estado</label><select class="form-select" name="estado"><option value="Detectada" {{ 'selected' if item.estado == 'Detectada' }}>Detectada</option><option value="En curso" {{ 'selected' if item.estado == 'En curso' }}>En curso</option><option value="Resuelta" {{ 'selected' if item.estado == 'Resuelta' }}>Resuelta</option></select></div>
            </div>
             <div class="card mb-3"><div class="card-header d-flex justify-content-between align-items-center"><span>Imágenes ({{ imgs|length }}/5)</span><small class="text-muted">Selecciona para borrar</small></div><div class="card-body">{% if imgs %}<div class="list-group mb-2">{% for img in imgs %}<div class="list-group-item d-flex justify-content-between align-items-center p-1"><small class="text-truncate" style="max-width: 200px;">{{ img.name }}</small> <input class="form-check-input" type="checkbox" name="delete_images" value="{{ loop.index0 }}"></div>{% endfor %}</div>{% endif %}{% if imgs|length < 5 %}<input type="file" class="form-control form-control-sm" name="images" multiple accept="image/*">{% endif %}</div></div>
            <div class="card"><div class="card-header d-flex justify-content-between align-items-center"><span>PDFs ({{ pdfs|length }}/5)</span><small class="text-muted">Selecciona para borrar</small></div><div class="card-body">{% if pdfs %}<div class="list-group mb-2">{% for pdf in pdfs %}<div class="list-group-item d-flex justify-content-between align-items-center p-1"><small class="text-truncate" style="max-width: 200px;">{{ pdf.name }}</small> <input class="form-check-input" type="checkbox" name="delete_pdfs" value="{{ loop.index0 }}"></div>{% endfor %}</div>{% endif %}{% if pdfs|length < 5 %}<input type="file" class="form-control form-control-sm" name="pdfs" multiple accept="application/pdf">{% endif %}</div></div>
        </div>
    </div>
    <hr><div class="d-flex justify-content-end gap-2"><a href="{{ url_for('correctivos') }}" class="btn btn-secondary">Cancelar</a><button type="submit" class="btn btn-primary">Guardar Cambios</button></div>
</form>
"""

VIEWER_TEMPLATE = """
<div class="mb-3"><a href="{{ back_url }}" class="btn btn-secondary">&larr; Volver</a><h3>{{ title_prefix }}: {{ item.nombre }}</h3></div>
<div class="row">
    {% if tipo == 'img' %}{% for file in files %}<div class="col-md-6 mb-4"><div class="card"><img src="data:image/png;base64,{{ file.data }}" class="card-img-top"><div class="card-footer text-muted">{{ file.name }}</div></div></div>{% endfor %}
    {% elif tipo == 'pdf' %}{% for file in files %}<div class="col-12 mb-5"><div class="card h-100"><div class="card-header">{{ file.name }}</div><div class="card-body p-0" style="height: 600px;"><embed src="data:application/pdf;base64,{{ file.data }}" type="application/pdf" width="100%" height="100%"></div></div></div>{% endfor %}
    {% endif %}
</div>
{% if not files %}<div class="alert alert-warning">No hay archivos.</div>{% endif %}
"""

PRINT_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}} img {max-width:100%;}</style></head><body onload="window.print()"><div class="container"><h1>Ficha Técnica</h1><div class="card mb-3"><div class="card-body"><strong>Nombre:</strong> {{ item.nombre }}<br><strong>Tipo:</strong> {{ item.tipo_nombre }}<br><strong>Desc:</strong> {{ item.descripcion }}</div></div><h3>Imágenes</h3><div class="row">{% for img in imgs %}<div class="col-6 mb-3"><img src="data:image/png;base64,{{ img.data }}"><br><small>{{ img.name }}</small></div>{% endfor %}</div><h3>PDFs</h3><ul>{% for pdf in pdfs %}<li>{{ pdf.name }}</li>{% endfor %}</ul></div></body></html>"""
PRINT_ALL_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Listado</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}} table{width:100%;border-collapse:collapse;} th,td{border:1px solid #ddd;padding:8px;}</style></head><body onload="window.print()"><div class="container"><h2>Listado Inventario</h2><table class="table"><thead><tr><th>ID</th><th>Nombre</th><th>Tipo</th><th>Desc</th></tr></thead><tbody>{% for i in items %}<tr><td>{{ i.id }}</td><td>{{ i.nombre }}</td><td>{{ i.tipo_nombre }}</td><td>{{ i.descripcion }}</td></tr>{% endfor %}</tbody></table></div></body></html>"""
PRINT_ACTIVITY_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Actividad</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}}</style></head><body onload="window.print()"><div class="container"><h1>Actividad: {{ activity.nombre }}</h1><p>Equipo: {{ activity.equipo_nombre }}</p><p>Periodicidad: {{ activity.periodicidad }}</p><p>Operaciones: {{ activity.operaciones }}</p></div></body></html>"""
PRINT_ALL_ACTIVITIES_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Actividades</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}} table{width:100%;border:1px solid #ddd;} th,td{border:1px solid #ddd;padding:5px;}</style></head><body onload="window.print()"><div class="container"><h2>Listado Actividades</h2><table><thead><tr><th>Actividad</th><th>Equipo</th><th>Freq</th><th>Ops</th></tr></thead><tbody>{% for a in activities %}<tr><td>{{ a.nombre }}</td><td>{{ a.equipo_nombre }}</td><td>{{ a.periodicidad }}</td><td>{{ a.operaciones }}</td></tr>{% endfor %}</tbody></table></div></body></html>"""
PRINT_OT_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>OT</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}}</style></head><body onload="window.print()"><div class="container"><h1>Orden de Trabajo #{{ ot.id }}</h1><h3>{{ ot.nombre }}</h3><p><strong>Estado:</strong> {{ ot.estado }}</p><p><strong>Equipo:</strong> {{ ot.equipo_nombre }}</p><p><strong>Fecha Gen:</strong> {{ ot.fecha_generacion }}</p><hr><h5>Operaciones</h5><p>{{ ot.operaciones }}</p><h5>Observaciones</h5><p>{{ ot.observaciones }}</p></div></body></html>"""
PRINT_ALL_OTS_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Listado OTs</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}} table{width:100%;border:1px solid #ddd;} th,td{border:1px solid #ddd;padding:5px;}</style></head><body onload="window.print()"><div class="container"><h2>Listado Órdenes de Trabajo</h2><table><thead><tr><th>ID</th><th>Nombre</th><th>Equipo</th><th>Fecha</th><th>Estado</th></tr></thead><tbody>{% for ot in ots %}<tr><td>{{ ot.id }}</td><td>{{ ot.nombre }}</td><td>{{ ot.equipo_nombre }}</td><td>{{ ot.fecha_generacion }}</td><td>{{ ot.estado }}</td></tr>{% endfor %}</tbody></table></div></body></html>"""
PRINT_CRONOGRAMA_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Cronograma de Mantenimiento {{ year }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @media print {
            .no-print { display: none; }
            @page { size: landscape; margin: 1cm; }
            /* Forzar impresión de colores de fondo */
            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            .badge-status, .badge-legend {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important; 
            }
        }
        body { padding: 20px; font-family: sans-serif; font-size: 0.8rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 4px; text-align: center; vertical-align: middle; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .text-start { text-align: left; }
        .badge-status {
            font-size: 0.75em;
            padding: 2px 4px;
            border-radius: 3px;
            display: inline-block;
            margin: 1px;
            color: #fff; /* Texto blanco por defecto para legibilidad */
            border: 1px solid #ccc;
        }
        /* Definición explícita de colores para impresión */
        .status-realizada { background-color: #198754 !important; color: white !important; border-color: #198754; }
        .status-en-curso { background-color: #ffc107 !important; color: #212529 !important; border-color: #ffc107; }
        .status-rechazada { background-color: #000000 !important; color: white !important; border-color: #000000; }
        .status-pendiente { background-color: #dc3545 !important; color: white !important; border-color: #dc3545; }
        .status-prevista { background-color: #6c757d !important; color: white !important; border-color: #6c757d; }
        
        .badge-legend {
            display: inline-block;
            padding: 3px 6px;
            font-size: 0.8em;
            font-weight: bold;
            border-radius: 4px;
            margin-right: 5px;
            border: 1px solid #999;
        }
    </style>
</head>
<body onload="window.print()">
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h2>Cronograma de Mantenimiento - Año {{ year }}</h2>
            <button class="btn btn-secondary no-print" onclick="window.close()">Cerrar</button>
        </div>

        <table class="table table-bordered table-sm">
            <thead>
                <tr>
                    <th style="width: 20%;">Actividad / Equipo</th>
                    {% for m in meses %}
                    <th>{{ m }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                <tr>
                    <td class="text-start bg-light">
                        <strong>{{ row.actividad }}</strong><br>
                        <span class="text-muted">{{ row.equipo }}</span>
                    </td>
                    {% for month_idx in range(1, 13) %}
                    <td style="vertical-align: top;">
                        {% if month_idx in row.ots %}
                            {% for ot in row.ots[month_idx] %}
                            <div class="badge-status 
                                {% if ot.estado == 'Realizada' %}status-realizada{% elif ot.estado == 'En curso' %}status-en-curso{% elif ot.estado == 'Pendiente' %}status-pendiente{% elif ot.estado == 'Prevista' %}status-prevista{% else %}status-rechazada{% endif %}">
                                {{ ot.day_day }}
                            </div>
                            {% endfor %}
                        {% endif %}
                    </td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="mt-3">
            <strong>Leyenda:</strong> 
            <span class="badge-legend status-realizada">Realizada</span>
            <span class="badge-legend status-en-curso">En Curso</span>
            <span class="badge-legend status-pendiente">Pendiente (Vencida)</span>
            <span class="badge-legend status-prevista">Prevista</span>
            <span class="badge-legend status-rechazada">Rechazada</span>
            <small class="ms-2 text-muted">El número indica el día del mes.</small>
        </div>
        <div class="mt-2 text-end text-muted">
            <small>Generado: {{ hoy }}</small>
        </div>
    </div>
</body>
</html>
"""
PRINT_CORRECTIVO_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Incidencia</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}} img{max-width:100%;}</style></head><body onload="window.print()"><div class="container"><h1>Incidencia: {{ item.nombre }}</h1><p><strong>Estado:</strong> {{ item.estado }}</p><p><strong>Equipo:</strong> {{ item.equipo_nombre }}</p><p><strong>Detectada:</strong> {{ item.fecha_detectada }}</p><p><strong>Comentario:</strong> {{ item.comentario }}</p><p><strong>Solución:</strong> {{ item.solucion }}</p><h3>Fotos</h3><div class="row">{% for img in imgs %}<div class="col-6"><img src="data:image/png;base64,{{ img.data }}"><br>{{ img.name }}</div>{% endfor %}</div><h3>Documentos PDF Adjuntos</h3><ul class="list-group">{% for pdf in pdfs %}<li class="list-group-item d-flex align-items-center"><span style="font-size: 1.5em; color: #dc3545; margin-right: 10px;">📄</span><div><strong>{{ pdf.name }}</strong><br><small class="text-muted">El contenido del PDF se encuentra almacenado digitalmente.</small></div></li>{% else %}<li class="list-group-item">No hay documentos PDF adjuntos.</li>{% endfor %}</ul></div></body></html>"""
PRINT_ALL_CORRECTIVOS_TEMPLATE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Listado Incidencias</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>@media print {.no-print {display:none;}} table{width:100%;border:1px solid #ddd;} th,td{border:1px solid #ddd;padding:5px;}</style></head><body onload="window.print()"><div class="container"><h2>Listado Incidencias</h2><table><thead><tr><th>ID</th><th>Nombre</th><th>Equipo</th><th>Estado</th><th>Fecha</th></tr></thead><tbody>{% for c in items %}<tr><td>{{ c.id }}</td><td>{{ c.nombre }}</td><td>{{ c.equipo_nombre }}</td><td>{{ c.estado }}</td><td>{{ c.fecha_detectada }}</td></tr>{% endfor %}</tbody></table></div></body></html>"""

CONFIGURACION_TEMPLATE = """
<div class="d-flex justify-content-between align-items-center mb-4"><h1 class="h2">Configuración de tipos</h1></div>
<div class="row"><div class="col-md-8"><div class="card"><div class="card-header d-flex justify-content-between align-items-center"><span>Tipos de Equipo</span><button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addTypeConfigModal">+ Nuevo</button></div><div class="card-body p-0"><table class="table table-striped table-hover mb-0"><thead class="table-light"><tr><th>ID</th><th>Nombre</th><th>Acciones</th></tr></thead><tbody>{% for tipo in tipos %}<tr><td>{{ tipo.id }}</td><td>{{ tipo.nombre }}</td><td><a href="{{ url_for('edit_type', id=tipo.id) }}" class="btn btn-sm btn-outline-primary">Editar</a></td></tr>{% endfor %}</tbody></table></div></div></div></div>
<div class="modal fade" id="addTypeConfigModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><form action="{{ url_for('add_type_config') }}" method="POST"><div class="modal-header"><h5 class="modal-title">Nuevo Tipo</h5></div><div class="modal-body"><input type="text" class="form-control" name="nombre" required></div><div class="modal-footer"><button type="submit" class="btn btn-primary">Guardar</button></div></form></div></div></div>
"""
EDIT_TYPE_TEMPLATE = """<h2>Editar Tipo</h2><form action="{{ url_for('update_type', id=tipo.id) }}" method="POST"><div class="mb-3"><input type="text" class="form-control" name="nombre" value="{{ tipo.nombre }}" required></div><button type="submit" class="btn btn-primary">Actualizar</button></form>"""
SYSTEM_DATE_TEMPLATE = """<h1 class="h2">Fecha del Sistema</h1><form action="{{ url_for('update_system_date') }}" method="POST"><div class="mb-3"><input type="date" class="form-control" name="fecha_sistema" value="{{ fecha_sistema }}" required></div><button type="submit" class="btn btn-primary">Guardar</button></form>"""

# --- FILTROS ---
@app.template_filter('json_load')
def json_load_filter(s):
    try: return json.loads(s) if s else []
    except: return []

# --- RUTAS ---
@app.route('/')
def index():
    init_db()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    f_nombre = request.args.get('f_nombre', '')
    f_tipo = request.args.get('f_tipo', '')
    conn = get_db_connection()
    tipos = conn.execute('SELECT * FROM tipos_equipo').fetchall()
    where = "WHERE 1=1"
    p = []
    if f_nombre: where += " AND i.nombre LIKE ?"; p.append(f'%{f_nombre}%')
    if f_tipo: where += " AND i.tipo_id = ?"; p.append(f_tipo)
    count = conn.execute(f'SELECT COUNT(*) FROM inventario i {where}', p).fetchone()[0]
    items = conn.execute(f'SELECT i.*, t.nombre as tipo_nombre FROM inventario i LEFT JOIN tipos_equipo t ON i.tipo_id=t.id {where} LIMIT ? OFFSET ?', p + [per_page, offset]).fetchall()
    has_next = (page * per_page) < count
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', INVENTARIO_TEMPLATE), items=items, tipos=tipos, page=page, has_next=has_next, active_page='inventario', system_date=get_system_date(), f_nombre=f_nombre, f_tipo=f_tipo)

@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    try:
        images_list = []
        for f in request.files.getlist('images')[:5]:
             if f and allowed_file_image(f.filename): images_list.append({'name': f.filename, 'data': file_to_base64(f)})
        pdfs_list = []
        for f in request.files.getlist('pdfs')[:5]:
             if f and allowed_file_pdf(f.filename): pdfs_list.append({'name': f.filename, 'data': file_to_base64(f)})
        conn = get_db_connection()
        conn.execute('INSERT INTO inventario (nombre, tipo_id, descripcion, images, pdfs) VALUES (?, ?, ?, ?, ?)',
                     (request.form['nombre'], request.form['tipo_id'], request.form['descripcion'], json.dumps(images_list), json.dumps(pdfs_list)))
        conn.commit()
        conn.close()
        flash('Equipo añadido', 'success')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

@app.route('/inventory/edit/<int:id>')
def edit_inventory(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM inventario WHERE id=?', (id,)).fetchone()
    tipos = conn.execute('SELECT * FROM tipos_equipo').fetchall()
    conn.close()
    if not item: return redirect(url_for('index'))
    imgs = normalize_files(json.loads(item['images']) if item['images'] else [])
    pdfs = normalize_files(json.loads(item['pdfs']) if item['pdfs'] else [])
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', EDIT_INVENTORY_TEMPLATE), item=item, tipos=tipos, imgs=imgs, pdfs=pdfs, active_page='inventario', system_date=get_system_date())

@app.route('/inventory/update/<int:id>', methods=['POST'])
def update_inventory(id):
    conn = get_db_connection()
    curr = conn.execute('SELECT images, pdfs FROM inventario WHERE id=?', (id,)).fetchone()
    curr_imgs = normalize_files(json.loads(curr['images']) if curr['images'] else [])
    curr_pdfs = normalize_files(json.loads(curr['pdfs']) if curr['pdfs'] else [])
    del_imgs = [int(x) for x in request.form.getlist('delete_images')]
    kept_imgs = [x for i, x in enumerate(curr_imgs) if i not in del_imgs]
    for f in request.files.getlist('images'):
        if f and allowed_file_image(f.filename): kept_imgs.append({'name': f.filename, 'data': file_to_base64(f)})
    if len(kept_imgs)>5: kept_imgs=kept_imgs[:5]
    del_pdfs = [int(x) for x in request.form.getlist('delete_pdfs')]
    kept_pdfs = [x for i, x in enumerate(curr_pdfs) if i not in del_pdfs]
    for f in request.files.getlist('pdfs'):
        if f and allowed_file_pdf(f.filename): kept_pdfs.append({'name': f.filename, 'data': file_to_base64(f)})
    if len(kept_pdfs)>5: kept_pdfs=kept_pdfs[:5]
    conn.execute('UPDATE inventario SET nombre=?, tipo_id=?, descripcion=?, images=?, pdfs=? WHERE id=?',
                 (request.form['nombre'], request.form['tipo_id'], request.form['descripcion'], json.dumps(kept_imgs), json.dumps(kept_pdfs), id))
    conn.commit()
    conn.close()
    flash('Actualizado', 'success')
    return redirect(url_for('index'))

@app.route('/inventory/print/<int:id>')
def print_inventory(id):
    conn = get_db_connection()
    item = conn.execute('SELECT i.*, t.nombre as tipo_nombre FROM inventario i LEFT JOIN tipos_equipo t ON i.tipo_id=t.id WHERE i.id=?', (id,)).fetchone()
    conn.close()
    imgs = normalize_files(json.loads(item['images']) if item['images'] else [])
    pdfs = normalize_files(json.loads(item['pdfs']) if item['pdfs'] else [])
    return render_template_string(PRINT_TEMPLATE, item=item, imgs=imgs, pdfs=pdfs, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/inventory/print_all')
def print_all_inventory():
    f_nombre = request.args.get('f_nombre', '')
    f_tipo = request.args.get('f_tipo', '')
    conn = get_db_connection()
    where = "WHERE 1=1"
    p = []
    if f_nombre: where += " AND i.nombre LIKE ?"; p.append(f'%{f_nombre}%')
    if f_tipo: where += " AND i.tipo_id = ?"; p.append(f_tipo)
    items = conn.execute(f'SELECT i.*, t.nombre as tipo_nombre FROM inventario i LEFT JOIN tipos_equipo t ON i.tipo_id=t.id {where} ORDER BY i.nombre', p).fetchall()
    conn.close()
    return render_template_string(PRINT_ALL_TEMPLATE, items=items, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/view_files/<source>/<tipo>/<int:id>')
def view_files(source, tipo, id):
    conn = get_db_connection()
    if source == 'inventory':
        item = conn.execute('SELECT * FROM inventario WHERE id=?', (id,)).fetchone()
        back_url = url_for('index')
        title_prefix = "Archivos de Equipo"
    elif source == 'corrective':
        item = conn.execute('SELECT * FROM correctivos WHERE id=?', (id,)).fetchone()
        back_url = url_for('correctivos')
        title_prefix = "Archivos de Incidencia"
    else:
        # Fallback
        item = None
        back_url = url_for('index')
        title_prefix = "Archivos"

    conn.close()
    
    files = []
    if item:
        if tipo == 'img': 
            content = item['images']
            files = normalize_files(json.loads(content) if content else [])
        elif tipo == 'pdf': 
            content = item['pdfs']
            files = normalize_files(json.loads(content) if content else [])
            
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', VIEWER_TEMPLATE), item=item, files=files, tipo=tipo, back_url=back_url, title_prefix=title_prefix, active_page='inventario', system_date=get_system_date())

@app.route('/activities')
def activities():
    f_nombre = request.args.get('f_nombre', '')
    f_equipo = request.args.get('f_equipo', '')
    f_periodicidad = request.args.get('f_periodicidad', '')
    conn = get_db_connection()
    query = 'SELECT a.*, i.nombre as equipo_nombre FROM actividades a JOIN inventario i ON a.equipo_id = i.id WHERE 1=1'
    p = []
    if f_nombre: query += " AND a.nombre LIKE ?"; p.append(f'%{f_nombre}%')
    if f_equipo: query += " AND a.equipo_id = ?"; p.append(f_equipo)
    if f_periodicidad: query += " AND a.periodicidad = ?"; p.append(f_periodicidad)
    actividades = conn.execute(query, p).fetchall()
    equipos = conn.execute('SELECT i.id, i.nombre, t.nombre as tipo_nombre FROM inventario i JOIN tipos_equipo t ON i.tipo_id = t.id').fetchall()
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', ACTIVIDADES_TEMPLATE), actividades=actividades, equipos=equipos, active_page='actividades', f_nombre=f_nombre, f_equipo=f_equipo, f_periodicidad=f_periodicidad, system_date=get_system_date())

@app.route('/activities/add', methods=['POST'])
def add_activity():
    conn = get_db_connection()
    conn.execute('INSERT INTO actividades (nombre, equipo_id, periodicidad, operaciones, fecha_inicio_gen) VALUES (?,?,?,?,?)',
                 (request.form['nombre'], request.form['equipo_id'], request.form['periodicidad'], request.form['operaciones'], request.form['fecha_inicio']))
    conn.commit()
    conn.close()
    flash('Actividad creada', 'success')
    return redirect(url_for('activities'))

@app.route('/activities/edit/<int:id>')
def edit_activity(id):
    conn = get_db_connection()
    activity = conn.execute('SELECT * FROM actividades WHERE id=?', (id,)).fetchone()
    equipos = conn.execute('SELECT i.id, i.nombre, t.nombre as tipo_nombre FROM inventario i JOIN tipos_equipo t ON i.tipo_id = t.id').fetchall()
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', EDIT_ACTIVITY_TEMPLATE), activity=activity, equipos=equipos, active_page='actividades', system_date=get_system_date())

@app.route('/activities/update/<int:id>', methods=['POST'])
def update_activity(id):
    conn = get_db_connection()
    conn.execute('UPDATE actividades SET nombre=?, equipo_id=?, periodicidad=?, operaciones=?, fecha_inicio_gen=? WHERE id=?',
                 (request.form['nombre'], request.form['equipo_id'], request.form['periodicidad'], request.form['operaciones'], request.form['fecha_inicio'], id))
    conn.commit()
    conn.close()
    flash('Actividad actualizada', 'success')
    return redirect(url_for('activities'))

@app.route('/activities/print/<int:id>')
def print_activity_single(id):
    conn = get_db_connection()
    activity = conn.execute('SELECT a.*, i.nombre as equipo_nombre, t.nombre as tipo_nombre FROM actividades a JOIN inventario i ON a.equipo_id=i.id JOIN tipos_equipo t ON i.tipo_id=t.id WHERE a.id=?', (id,)).fetchone()
    conn.close()
    return render_template_string(PRINT_ACTIVITY_TEMPLATE, activity=activity, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/activities/print_all')
def print_all_activities():
    conn = get_db_connection()
    activities = conn.execute('SELECT a.*, i.nombre as equipo_nombre FROM actividades a JOIN inventario i ON a.equipo_id=i.id ORDER BY a.nombre').fetchall()
    conn.close()
    return render_template_string(PRINT_ALL_ACTIVITIES_TEMPLATE, activities=activities, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/work_orders')
def work_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    estado = request.args.get('estado', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    conn = get_db_connection()
    q = 'FROM ordenes_trabajo ot JOIN actividades a ON ot.actividad_id = a.id JOIN inventario i ON a.equipo_id = i.id WHERE 1=1'
    p = []
    if estado: q+=" AND ot.estado=?"; p.append(estado)
    if fecha_inicio: q+=" AND ot.fecha_generacion>=?"; p.append(fecha_inicio)
    if fecha_fin: q+=" AND ot.fecha_generacion<=?"; p.append(fecha_fin)
    count = conn.execute(f'SELECT COUNT(*) {q}', p).fetchone()[0]
    ots = conn.execute(f'SELECT ot.*, a.operaciones, i.nombre as equipo_nombre {q} ORDER BY ot.fecha_generacion DESC LIMIT ? OFFSET ?', p+[per_page, offset]).fetchall()
    has_next = (page*per_page)<count
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', OTS_TEMPLATE), ots=ots, page=page, has_next=has_next, active_page='ots', estado_filter=estado, fecha_inicio_filter=fecha_inicio, fecha_fin_filter=fecha_fin, system_date=get_system_date())

@app.route('/work_orders/generate', methods=['POST'])
def generate_work_orders():
    conn = get_db_connection()
    actividades = conn.execute('SELECT * FROM actividades').fetchall()
    hoy = get_system_date()
    count = 0
    for act in actividades:
        f = datetime.datetime.strptime(act['fecha_inicio_gen'], '%Y-%m-%d').date()
        p = act['periodicidad']
        while f <= hoy:
            if not conn.execute('SELECT id FROM ordenes_trabajo WHERE actividad_id=? AND fecha_generacion=?', (act['id'], f)).fetchone():
                limit = f + datetime.timedelta(days=p)
                st = 'Pendiente' if limit < hoy else 'En curso'
                conn.execute('INSERT INTO ordenes_trabajo (actividad_id, nombre, fecha_generacion, estado) VALUES (?,?,?,?)', 
                             (act['id'], f"{act['nombre']} - {f.strftime('%d/%m/%Y')}", f, st))
                count += 1
            f += datetime.timedelta(days=p)
            
    # Recalculate states
    active = conn.execute("SELECT ot.id, ot.fecha_generacion, a.periodicidad FROM ordenes_trabajo ot JOIN actividades a ON ot.actividad_id=a.id WHERE ot.estado NOT IN ('Realizada', 'Rechazada')").fetchall()
    for ot in active:
        gen = datetime.datetime.strptime(ot['fecha_generacion'], '%Y-%m-%d').date()
        if (gen.year > hoy.year) or (gen.year == hoy.year and gen.month > hoy.month):
             conn.execute("UPDATE ordenes_trabajo SET estado = 'Prevista' WHERE id = ?", (ot['id'],))
        else:
            deadline = gen + datetime.timedelta(days=ot['periodicidad'])
            if deadline < hoy: conn.execute("UPDATE ordenes_trabajo SET estado = 'Pendiente' WHERE id = ?", (ot['id'],))
            else: conn.execute("UPDATE ordenes_trabajo SET estado = 'En curso' WHERE id = ?", (ot['id'],))
    
    conn.commit()
    conn.close()
    flash(f'Generadas {count} nuevas OTs y estados actualizados.', 'info')
    return redirect(url_for('work_orders'))

@app.route('/work_orders/update/<int:id>', methods=['POST'])
def update_ot(id):
    conn = get_db_connection()
    conn.execute('UPDATE ordenes_trabajo SET estado=?, observaciones=?, fecha_realizada=? WHERE id=?', (request.form['estado'], request.form['observaciones'], request.form['fecha_realizada'], id))
    conn.commit()
    conn.close()
    flash('OT actualizada', 'success')
    if request.form.get('redirect_to')=='cronograma': return redirect(url_for('cronograma'))
    return redirect(url_for('work_orders'))

@app.route('/work_orders/print/<int:id>')
def print_ot(id):
    conn = get_db_connection()
    ot = conn.execute('SELECT ot.*, a.operaciones, i.nombre as equipo_nombre, t.nombre as tipo_nombre FROM ordenes_trabajo ot JOIN actividades a ON ot.actividad_id=a.id JOIN inventario i ON a.equipo_id=i.id JOIN tipos_equipo t ON i.tipo_id=t.id WHERE ot.id=?', (id,)).fetchone()
    conn.close()
    return render_template_string(PRINT_OT_TEMPLATE, ot=ot, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/work_orders/print_all')
def print_all_ots():
    estado = request.args.get('estado', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    conn = get_db_connection()
    q = 'SELECT ot.*, i.nombre as equipo_nombre FROM ordenes_trabajo ot JOIN actividades a ON ot.actividad_id=a.id JOIN inventario i ON a.equipo_id=i.id WHERE 1=1'
    p = []
    if estado: q+=" AND ot.estado=?"; p.append(estado)
    if fecha_inicio: q+=" AND ot.fecha_generacion>=?"; p.append(fecha_inicio)
    if fecha_fin: q+=" AND ot.fecha_generacion<=?"; p.append(fecha_fin)
    q += " ORDER BY ot.fecha_generacion DESC"
    ots = conn.execute(q, p).fetchall()
    conn.close()
    return render_template_string(PRINT_ALL_OTS_TEMPLATE, ots=ots, filters=[], hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/cronograma')
def cronograma():
    year = request.args.get('year', get_system_date().year, type=int)
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    conn = get_db_connection()
    data = get_cronograma_data(conn, year)
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', CRONOGRAMA_TEMPLATE), data=data, meses=meses, year=year, active_page='cronograma', system_date=get_system_date())

@app.route('/cronograma/print')
def print_cronograma():
    year = request.args.get('year', get_system_date().year, type=int)
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    conn = get_db_connection()
    data = get_cronograma_data(conn, year)
    conn.close()
    return render_template_string(PRINT_CRONOGRAMA_TEMPLATE, data=data, meses=meses, year=year, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/correctivos')
def correctivos():
    f_nombre = request.args.get('f_nombre', '')
    f_equipo = request.args.get('f_equipo', '')
    f_estado = request.args.get('f_estado', '')
    f_fecha_desde = request.args.get('f_fecha_desde', '')
    conn = get_db_connection()
    q = 'SELECT c.*, i.nombre as equipo_nombre FROM correctivos c JOIN inventario i ON c.equipo_id=i.id WHERE 1=1'
    p = []
    if f_nombre: q+=" AND c.nombre LIKE ?"; p.append(f'%{f_nombre}%')
    if f_equipo: q+=" AND c.equipo_id=?"; p.append(f_equipo)
    if f_estado: q+=" AND c.estado=?"; p.append(f_estado)
    if f_fecha_desde: q+=" AND c.fecha_detectada>=?"; p.append(f_fecha_desde)
    q += " ORDER BY c.fecha_detectada DESC"
    items = conn.execute(q, p).fetchall()
    equipos = conn.execute('SELECT i.id, i.nombre, t.nombre as tipo_nombre FROM inventario i JOIN tipos_equipo t ON i.tipo_id=t.id').fetchall()
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', CORRECTIVOS_TEMPLATE), correctivos=items, equipos=equipos, active_page='correctivos', f_nombre=f_nombre, f_equipo=f_equipo, f_estado=f_estado, f_fecha_desde=f_fecha_desde, system_date=get_system_date())

@app.route('/correctivos/add', methods=['POST'])
def add_correctivo():
    images_list = []
    for f in request.files.getlist('images')[:5]:
        if f and allowed_file_image(f.filename): images_list.append({'name': f.filename, 'data': file_to_base64(f)})
    pdfs_list = []
    for f in request.files.getlist('pdfs')[:5]:
        if f and allowed_file_pdf(f.filename): pdfs_list.append({'name': f.filename, 'data': file_to_base64(f)})
    conn = get_db_connection()
    conn.execute('INSERT INTO correctivos (nombre, equipo_id, comentario, fecha_detectada, estado, images, pdfs) VALUES (?,?,?,?,?,?,?)',
                 (request.form['nombre'], request.form['equipo_id'], request.form['comentario'], request.form['fecha_detectada'], request.form['estado'], json.dumps(images_list), json.dumps(pdfs_list)))
    conn.commit()
    conn.close()
    flash('Incidencia registrada', 'success')
    return redirect(url_for('correctivos'))

@app.route('/correctivos/edit/<int:id>')
def edit_correctivo(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM correctivos WHERE id=?', (id,)).fetchone()
    equipos = conn.execute('SELECT i.id, i.nombre, t.nombre as tipo_nombre FROM inventario i JOIN tipos_equipo t ON i.tipo_id=t.id').fetchall()
    conn.close()
    imgs = normalize_files(json.loads(item['images']) if item['images'] else [])
    pdfs = normalize_files(json.loads(item['pdfs']) if item['pdfs'] else [])
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', EDIT_CORRECTIVO_TEMPLATE), item=item, equipos=equipos, imgs=imgs, pdfs=pdfs, active_page='correctivos', system_date=get_system_date())

@app.route('/correctivos/update/<int:id>', methods=['POST'])
def update_correctivo(id):
    conn = get_db_connection()
    curr = conn.execute('SELECT images, pdfs FROM correctivos WHERE id=?', (id,)).fetchone()
    curr_imgs = normalize_files(json.loads(curr['images']) if curr['images'] else [])
    curr_pdfs = normalize_files(json.loads(curr['pdfs']) if curr['pdfs'] else [])
    
    del_imgs = [int(x) for x in request.form.getlist('delete_images')]
    kept_imgs = [x for i, x in enumerate(curr_imgs) if i not in del_imgs]
    for f in request.files.getlist('images'):
        if f and allowed_file_image(f.filename): kept_imgs.append({'name': f.filename, 'data': file_to_base64(f)})
    if len(kept_imgs)>5: kept_imgs=kept_imgs[:5]

    del_pdfs = [int(x) for x in request.form.getlist('delete_pdfs')]
    kept_pdfs = [x for i, x in enumerate(curr_pdfs) if i not in del_pdfs]
    for f in request.files.getlist('pdfs'):
        if f and allowed_file_pdf(f.filename): kept_pdfs.append({'name': f.filename, 'data': file_to_base64(f)})
    if len(kept_pdfs)>5: kept_pdfs=kept_pdfs[:5]
    
    conn.execute('UPDATE correctivos SET nombre=?, equipo_id=?, comentario=?, solucion=?, fecha_detectada=?, fecha_resolucion=?, estado=?, images=?, pdfs=? WHERE id=?',
                 (request.form['nombre'], request.form['equipo_id'], request.form['comentario'], request.form['solucion'], request.form['fecha_detectada'], request.form['fecha_resolucion'], request.form['estado'], json.dumps(kept_imgs), json.dumps(kept_pdfs), id))
    conn.commit()
    conn.close()
    flash('Incidencia actualizada', 'success')
    return redirect(url_for('correctivos'))

@app.route('/correctivos/delete/<int:id>', methods=['POST'])
def delete_correctivo(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM correctivos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Eliminado', 'success')
    return redirect(url_for('correctivos'))

@app.route('/correctivos/print/<int:id>')
def print_correctivo(id):
    conn = get_db_connection()
    item = conn.execute('SELECT c.*, i.nombre as equipo_nombre FROM correctivos c JOIN inventario i ON c.equipo_id=i.id WHERE c.id=?', (id,)).fetchone()
    conn.close()
    imgs = normalize_files(json.loads(item['images']) if item['images'] else [])
    pdfs = normalize_files(json.loads(item['pdfs']) if item['pdfs'] else []) # Extract PDFs
    return render_template_string(PRINT_CORRECTIVO_TEMPLATE, item=item, imgs=imgs, pdfs=pdfs, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/correctivos/print_all')
def print_all_correctivos():
    f_nombre = request.args.get('f_nombre', '')
    f_equipo = request.args.get('f_equipo', '')
    f_estado = request.args.get('f_estado', '')
    f_fecha_desde = request.args.get('f_fecha_desde', '')
    conn = get_db_connection()
    q = 'SELECT c.*, i.nombre as equipo_nombre FROM correctivos c JOIN inventario i ON c.equipo_id=i.id WHERE 1=1'
    p = []
    if f_nombre: q+=" AND c.nombre LIKE ?"; p.append(f'%{f_nombre}%')
    if f_equipo: q+=" AND c.equipo_id=?"; p.append(f_equipo)
    if f_estado: q+=" AND c.estado=?"; p.append(f_estado)
    if f_fecha_desde: q+=" AND c.fecha_detectada>=?"; p.append(f_fecha_desde)
    q += " ORDER BY c.fecha_detectada DESC"
    items = conn.execute(q, p).fetchall()
    conn.close()
    return render_template_string(PRINT_ALL_CORRECTIVOS_TEMPLATE, items=items, hoy=get_system_date().strftime('%d/%m/%Y'))

@app.route('/configuration')
def configuration():
    conn = get_db_connection()
    tipos = conn.execute('SELECT * FROM tipos_equipo').fetchall()
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', CONFIGURACION_TEMPLATE), tipos=tipos, active_page='configuracion', system_date=get_system_date())

@app.route('/configuration/type/add', methods=['POST'])
def add_type_config():
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO tipos_equipo (nombre) VALUES (?)', (request.form['nombre'],))
        conn.commit()
        conn.close()
    except: pass
    return redirect(url_for('configuration'))

@app.route('/configuration/type/edit/<int:id>')
def edit_type(id):
    conn = get_db_connection()
    tipo = conn.execute('SELECT * FROM tipos_equipo WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', EDIT_TYPE_TEMPLATE), tipo=tipo, active_page='configuracion', system_date=get_system_date())

@app.route('/configuration/type/update/<int:id>', methods=['POST'])
def update_type(id):
    try:
        conn = get_db_connection()
        conn.execute('UPDATE tipos_equipo SET nombre=? WHERE id=?', (request.form['nombre'], id))
        conn.commit()
        conn.close()
    except: pass
    return redirect(url_for('configuration'))

@app.route('/system_date_config')
def system_date_config():
    return render_template_string(BASE_TEMPLATE.replace('<!-- CONTENT_PLACEHOLDER -->', SYSTEM_DATE_TEMPLATE), fecha_sistema=get_system_date(), active_page='fecha_sistema', system_date=get_system_date())

@app.route('/system_date_config/update', methods=['POST'])
def update_system_date():
    conn = get_db_connection()
    conn.execute('UPDATE configuracion SET fecha_sistema=? WHERE id=1', (request.form['fecha_sistema'],))
    conn.commit()
    conn.close()
    return redirect(url_for('system_date_config'))

@app.route('/types/add', methods=['POST'])
def add_type():
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO tipos_equipo (nombre) VALUES (?)', (request.form['nombre'],))
        conn.commit()
        conn.close()
    except: pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('mantenimiento_factory.db'):
        init_db()
    print("Iniciando Sistema GMAO...")
    app.run(debug=True, port=5000, host='0.0.0.0')