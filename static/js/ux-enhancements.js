/**
 * FinTrack - Améliorations UX globales
 * Validation temps réel, feedback visuel, animations
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ============ VALIDATION FORMULAIRES ============
    
    /**
     * Ajoute la validation Bootstrap sur tous les formulaires
     */
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Validation en temps réel
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value) {
                    if (this.checkValidity()) {
                        this.classList.add('is-valid');
                        this.classList.remove('is-invalid');
                    } else {
                        this.classList.add('is-invalid');
                        this.classList.remove('is-valid');
                    }
                }
            });
        });
    });
    
    
    // ============ VALIDATION MONTANTS ============
    
    /**
     * Valide les champs de montant (nombre positif)
     */
    const amountInputs = document.querySelectorAll('input[type="number"][name*="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            const feedback = this.parentElement.querySelector('.invalid-feedback') || createFeedback();
            
            if (isNaN(value) || value <= 0) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                feedback.textContent = 'Le montant doit être supérieur à 0';
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
            
            function createFeedback() {
                const div = document.createElement('div');
                div.className = 'invalid-feedback';
                input.parentElement.appendChild(div);
                return div;
            }
        });
    });
    
    
    // ============ AUTO-SAVE INDICATION ============
    
    /**
     * Montre un indicateur visuel pendant la sauvegarde
     */
    const saveForms = document.querySelectorAll('form[data-auto-save]');
    saveForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enregistrement...';
                submitBtn.disabled = true;
                
                // En cas d'erreur, restaurer le bouton après 5 secondes
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 5000);
            }
        });
    });
    
    
    // ============ CONFIRMATION SUPPRESSION ============
    
    /**
     * Double confirmation pour les actions destructives
     */
    const deleteLinks = document.querySelectorAll('a[href*="delete"], button[data-action="delete"]');
    deleteLinks.forEach(link => {
        if (!link.hasAttribute('data-no-confirm')) {
            link.addEventListener('click', function(e) {
                if (!confirm('⚠️ Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.')) {
                    e.preventDefault();
                }
            });
        }
    });
    
    
    // ============ TOOLTIPS BOOTSTRAP ============
    
    /**
     * Active tous les tooltips Bootstrap
     */
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    
    // ============ AUTO-DISMISS ALERTS ============
    
    /**
     * Ferme automatiquement les alertes après 5 secondes
     */
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) { // Garder les erreurs visibles
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    
    // ============ FORMATAGE MONTANTS ============
    
    /**
     * Formate les montants avec séparateurs de milliers
     */
    const moneyDisplays = document.querySelectorAll('[data-money]');
    moneyDisplays.forEach(element => {
        const amount = parseFloat(element.getAttribute('data-money'));
        if (!isNaN(amount)) {
            element.textContent = amount.toLocaleString('fr-FR', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }) + ' FCFA';
        }
    });
    
    
    // ============ LAZY LOADING IMAGES ============
    
    /**
     * Charge les images au scroll (améliore performance)
     */
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img.lazy');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    
    // ============ KEYBOARD SHORTCUTS ============
    
    /**
     * Raccourcis clavier globaux
     */
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K : Focus sur la recherche
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) searchInput.focus();
        }
        
        // Escape : Fermer les modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
        }
    });
    
    
    // ============ COPY TO CLIPBOARD ============
    
    /**
     * Copie dans le presse-papiers avec feedback
     */
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-copy');
            navigator.clipboard.writeText(text).then(() => {
                const originalHtml = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i> Copié !';
                setTimeout(() => {
                    this.innerHTML = originalHtml;
                }, 2000);
            });
        });
    });
    
    
    // ============ SMOOTH SCROLL ============
    
    /**
     * Scroll fluide pour les ancres
     */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    
    // ============ ANIMATION AU SCROLL ============
    
    /**
     * Anime les éléments quand ils entrent dans le viewport
     */
    const animateOnScroll = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        animateOnScroll.observe(el);
    });
    
});


// ============ UTILITAIRES GLOBAUX ============

/**
 * Affiche un toast de notification
 */
window.showToast = function(message, type = 'info') {
    const toastHtml = `
        <div class="position-fixed top-0 end-0 p-3" style="z-index: 11000;">
            <div class="toast show" role="alert">
                <div class="toast-header bg-${type} text-white">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                    <strong class="me-auto">${type === 'success' ? 'Succès' : type === 'danger' ? 'Erreur' : 'Information'}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">${message}</div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toastHtml);
    const toast = document.querySelector('.toast:last-child');
    setTimeout(() => toast.remove(), 5000);
};

/**
 * Affiche un overlay de chargement
 */
window.showLoadingOverlay = function(message = 'Chargement...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'globalLoadingOverlay';
    overlay.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner mb-3"></div>
            <div>${message}</div>
        </div>
    `;
    document.body.appendChild(overlay);
};

window.hideLoadingOverlay = function() {
    const overlay = document.getElementById('globalLoadingOverlay');
    if (overlay) overlay.remove();
};
