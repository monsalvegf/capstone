document.addEventListener('DOMContentLoaded', function() {
    // Función para cargar los detalles en el panel o en el modal
    function loadNonconformityDetail(nonconformityId) {
        fetch('/nonconformities/detail/partial/' + nonconformityId + '/')
        .then(response => response.text())
        .then(data => {
            if (window.innerWidth >= 768) {
                // Pantalla ancha: cargar detalle en el panel lateral
                var panel = document.getElementById('detail-panel');
                panel.innerHTML = data;
                panel.classList.add('open');
            } else {
                // Pantalla pequeña: mostrar detalle en un modal
                var modalContent = document.getElementById('modal-content');
                modalContent.innerHTML = data;
                var modal = document.getElementById('detail-modal');
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden'; // Evitar desplazamiento del fondo
            }
        });
    }

    // Añadir event listeners a las filas de la tabla
    document.querySelectorAll('.nonconformity-row').forEach(function(row) {
        row.addEventListener('click', function() {
            var nonconformityId = this.dataset.id;
            loadNonconformityDetail(nonconformityId);
        });
    });

    // Cerrar el panel lateral al hacer clic fuera de él
    document.addEventListener('click', function(event) {
        var panel = document.getElementById('detail-panel');
        if (panel && panel.classList.contains('open') && !panel.contains(event.target) && !event.target.closest('.nonconformity-row')) {
            panel.classList.remove('open');
            panel.innerHTML = ''; // Limpiar el contenido del panel
        }
    });

    // Cerrar el modal al hacer clic en el botón de cerrar o fuera del modal
    var closeModalButton = document.getElementById('close-modal');
    if (closeModalButton) {
        closeModalButton.addEventListener('click', function() {
            var modal = document.getElementById('detail-modal');
            modal.style.display = 'none';
            document.getElementById('modal-content').innerHTML = ''; // Limpiar el contenido del modal
            document.body.style.overflow = ''; // Restablecer el desplazamiento
        });
    }

    window.addEventListener('click', function(event) {
        var modal = document.getElementById('detail-modal');
        if (modal && event.target === modal) {
            modal.style.display = 'none';
            document.getElementById('modal-content').innerHTML = '';
            document.body.style.overflow = '';
        }
    });

    // Cerrar el modal al presionar la tecla ESC
    document.addEventListener('keydown', function(event) {
        var modal = document.getElementById('detail-modal');
        if (modal && modal.style.display === 'block' && event.key === 'Escape') {
            modal.style.display = 'none';
            document.getElementById('modal-content').innerHTML = '';
            document.body.style.overflow = '';
        }
    });

    // Script para manejar el envío del formulario de filtrado
    var filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('change', function() {
            this.submit();
        });
    }
});
