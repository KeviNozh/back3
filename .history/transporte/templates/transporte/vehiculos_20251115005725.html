{% extends 'base.html' %}
{% load static %}

{% block title %}Vehículos - Logística Global{% endblock %}

{% block content %}
<div class="page-title">
    <span>🚛</span>
    <span>Gestión de Vehículos</span>
</div>

<!-- BLOQUE DE PERMISOS PARA NO-ADMIN -->
{% if user.is_authenticated and user.perfilusuario.tipo_usuario != 'ADMIN' and not user.is_superuser %}
<div style="background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;">
    <div style="display: flex; align-items: center; gap: 0.5rem; color: #3b82f6;">
        <span>🔒</span>
        <div>
            <strong>Modo Solo Lectura</strong>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                Como {{ user.perfilusuario.tipo_usuario|title }}, solo puedes visualizar información de vehículos.
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Mensajes del sistema -->
{% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }}">
        {{ message }}
    </div>
    {% endfor %}
{% endif %}

<div class="filters">
    <div class="filter-group">
        <select class="filter-select" id="filter-status">
            <option value="">Todos los estados</option>
            <option value="active">Activo</option>
            <option value="inactive">Inactivo</option>
        </select>
        <select class="filter-select" id="filter-type">
            <option value="">Todos los tipos</option>
            <option value="camion">Camión</option>
            <option value="furgon">Furgón</option>
            <option value="trailer">Tráiler</option>
        </select>
    </div>
    <input type="text" class="search-input" id="search-input" placeholder="Buscar vehículo...">
    
    <!-- Solo mostrar botón para admin -->
    {% if user.is_superuser or user.perfilusuario.tipo_usuario == 'ADMIN' %}
    <button class="btn" onclick="window.location.href='{% url 'vehiculo_crear' %}'">➕ Nuevo Vehículo</button>
    {% endif %}
</div>

<div class="table-container">
    <div class="table-header">
        <div class="table-title">Lista de Vehículos</div>
        <div id="vehicle-count" style="color: var(--text-secondary); font-size: 0.9rem;">
            Total: {{ vehiculos|length }} vehículos
        </div>
    </div>
    
    {% if vehiculos %}
    <table class="table">
        <thead>
            <tr>
                <th>Patente</th>
                <th>Modelo</th>
                <th>Tipo</th>
                <th>Capacidad</th>
                <th>Conductor</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for vehiculo in vehiculos %}
            <tr>
                <td>{{ vehiculo.patente }}</td>
                <td>{{ vehiculo.modelo }}</td>
                <td>{{ vehiculo.tipo_vehiculo }}</td>
                <td>{{ vehiculo.capacidad_kg }} kg</td>
                <td>
                    {% if vehiculo.conductor_asignado %}
                        {{ vehiculo.conductor_asignado.nombre }}
                    {% else %}
                        <span style="color: var(--text-secondary);">Sin asignar</span>
                    {% endif %}
                </td>
                <td>
                    <span class="badge {% if vehiculo.activo %}active{% else %}inactive{% endif %}">
                        {% if vehiculo.activo %}Activo{% else %}Inactivo{% endif %}
                    </span>
                </td>
                <td>
                    <button class="action-btn" onclick="viewVehicle('{{ vehiculo.patente }}')">Ver</button>
                    
                    <!-- Solo admin puede editar/eliminar -->
                    {% if user.is_superuser or user.perfilusuario.tipo_usuario == 'ADMIN' %}
                    <button class="action-btn" onclick="editVehicle({{ vehiculo.id }})">Editar</button>
                    <button class="action-btn delete" onclick="deleteVehicle({{ vehiculo.id }})">Eliminar</button>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🚛</div>
        <h3>No hay vehículos registrados</h3>
        <p style="margin-top: 0.5rem;">Comienza registrando el primer vehículo en el sistema.</p>
        
        {% if user.is_superuser or user.perfilusuario.tipo_usuario == 'ADMIN' %}
        <button class="btn" onclick="window.location.href='{% url 'vehiculo_crear' %}'" style="margin-top: 1rem;">
            ➕ Registrar Primer Vehículo
        </button>
        {% endif %}
    </div>
    {% endif %}
</div>

<script>
// Funciones de acción para los vehículos
function viewVehicle(patente) {
    showNotification(`Viendo detalles del vehículo ${patente}`);
    // En una implementación real, redirigiría a la página de detalles
}

function editVehicle(vehicleId) {
    window.location.href = `/vehiculos/${vehicleId}/editar/`;
}

function deleteVehicle(vehicleId) {
    if (confirm('¿Está seguro de que desea eliminar este vehículo? Esta acción no se puede deshacer.')) {
        window.location.href = `/vehiculos/${vehicleId}/eliminar/`;
    }
}

// Filtros y búsqueda
document.addEventListener('DOMContentLoaded', function() {
    const filterStatus = document.getElementById('filter-status');
    const filterType = document.getElementById('filter-type');
    const searchInput = document.getElementById('search-input');
    
    function filterVehicles() {
        const statusValue = filterStatus.value;
        const typeValue = filterType.value;
        const searchValue = searchInput.value.toLowerCase();
        const rows = document.querySelectorAll('.table tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const status = row.cells[5].textContent.trim().toLowerCase();
            const type = row.cells[2].textContent.toLowerCase();
            const patente = row.cells[0].textContent.toLowerCase();
            const modelo = row.cells[1].textContent.toLowerCase();
            
            const matchesStatus = !statusValue || 
                                (statusValue === 'active' && status === 'activo') ||
                                (statusValue === 'inactive' && status === 'inactivo');
            
            const matchesType = !typeValue || type.includes(typeValue);
            const matchesSearch = !searchValue || 
                                patente.includes(searchValue) || 
                                modelo.includes(searchValue);
            
            if (matchesStatus && matchesType && matchesSearch) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        document.getElementById('vehicle-count').textContent = `Total: ${visibleCount} vehículos`;
    }
    
    filterStatus.addEventListener('change', filterVehicles);
    filterType.addEventListener('change', filterVehicles);
    searchInput.addEventListener('input', filterVehicles);
    
    // Ocultar botones de acción para no-admin
    {% if user.is_authenticated and user.perfilusuario.tipo_usuario != 'ADMIN' and not user.is_superuser %}
    const actionButtons = document.querySelectorAll('.action-btn.delete, .action-btn:nth-child(2)');
    actionButtons.forEach(btn => {
        if (btn.textContent === 'Editar' || btn.textContent === 'Eliminar') {
            btn.style.display = 'none';
        }
    });
    {% endif %}
});

function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = `ℹ️ ${message}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
        z-index: 1000;
        animation: slideInRight 0.4s ease-out;
        font-weight: 600;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s ease-out';
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}
</script>
{% endblock %}