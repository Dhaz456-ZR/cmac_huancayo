document.addEventListener('DOMContentLoaded', function() {

    // Toggle card number visibility
    const toggleBtn = document.getElementById('toggleCard');
    if (toggleBtn) {
        let isVisible = false;
        const cardNumberEl = document.querySelector('.card-number');
        const originalText = cardNumberEl ? cardNumberEl.textContent : '';

        toggleBtn.addEventListener('click', function() {
            isVisible = !isVisible;
            if (cardNumberEl) {
                if (isVisible) {
                    // Mostrar número completo (ejemplo)
                    cardNumberEl.textContent = '1234 5678 9012 1111';
                } else {
                    cardNumberEl.textContent = originalText;
                }
            }
        });
    }

    // Animar barras de progreso al cargar
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(function(fill) {
        var width = fill.style.width;
        fill.style.width = '0%';
        setTimeout(function() {
            fill.style.width = width;
        }, 300);
    });

    // Hover efecto en tarjetas
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.borderColor = 'rgba(196, 0, 24, 0.2)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.borderColor = 'rgba(255, 255, 255, 0.06)';
        });
    });

    console.log('Dashboard CMAC Huancayo cargado correctamente');
});