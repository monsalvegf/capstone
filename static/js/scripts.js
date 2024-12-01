document.addEventListener('DOMContentLoaded', function() {
    // Función para cargar los detalles en el panel o en el modal
    function loadNonconformityDetail(nonconformityId) {
        fetch('/nonconformities/detail/partial/' + nonconformityId + '/')
        .then(response => response.text())
        .then(data => {
            // Pantalla ancha: cargar detalle en el panel lateral
            var panel = document.getElementById('detail-panel');
            panel.innerHTML = data;
            // Asegurarse de que el panel está abierto (la clase 'open' ya está por defecto)
        });
    }
    

    // Añadir event listeners a las filas de la tabla
    document.querySelectorAll('.nonconformity-row').forEach(function(row) {
        row.addEventListener('click', function() {
            var nonconformityId = this.dataset.id;
            loadNonconformityDetail(nonconformityId);
        });
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
