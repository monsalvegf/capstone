// Esperar a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Agregar event listener a las filas de la tabla
    document.querySelectorAll('.nonconformity-row').forEach(function(row) {
        row.addEventListener('click', function() {
            var nonconformityId = this.getAttribute('data-id');
            // Llamar a la función para cargar los detalles
            loadNonconformityDetail(nonconformityId);
            // Actualizar la selección en la tabla
            updateSelectedRow(this);
        });
    });

    // Agregar event listener al formulario de filtrado
    var filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('change', function() {
            filterForm.submit();
        });
    }
});

function loadNonconformityDetail(nonconformityId) {
    fetch('/nonconformities/detail/partial/' + nonconformityId + '/')
    .then(response => response.text())
    .then(data => {
        var isSmallScreen = window.matchMedia("(max-width: 767px)").matches;
        if (isSmallScreen) {
            // Pantalla pequeña: mostrar modal
            var modal = document.getElementById('detail-modal');
            var modalContent = document.getElementById('modal-content');
            modalContent.innerHTML = data;
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Evitar scroll en el fondo
        } else {
            // Pantalla grande: cargar detalle en el panel lateral
            var panel = document.getElementById('detail-panel');
            panel.innerHTML = data;
        }
    });
}

function updateSelectedRow(selectedRow) {
    // Remover la clase 'selected' de cualquier fila previamente seleccionada
    var previouslySelected = document.querySelector('.nonconformity-row.selected');
    if (previouslySelected) {
        previouslySelected.classList.remove('selected');
    }
    // Añadir la clase 'selected' a la fila clicada
    selectedRow.classList.add('selected');
}

// Cerrar el modal al hacer clic en el botón de cierre
document.getElementById('close-modal').addEventListener('click', function() {
    var modal = document.getElementById('detail-modal');
    modal.style.display = 'none';
    document.getElementById('modal-content').innerHTML = '';
    document.body.style.overflow = '';
});

// Cerrar el modal al hacer clic fuera de él
window.addEventListener('click', function(event) {
    var modal = document.getElementById('detail-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
        document.getElementById('modal-content').innerHTML = '';
        document.body.style.overflow = '';
    }
});

// Cerrar el modal al presionar Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        var modal = document.getElementById('detail-modal');
        if (modal.style.display === 'block') {
            modal.style.display = 'none';
            document.getElementById('modal-content').innerHTML = '';
            document.body.style.overflow = '';
        }
    }
});
