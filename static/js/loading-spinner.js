/**
 * Loading Spinner System
 * Affiche automatiquement un spinner lors des soumissions de formulaires et requêtes AJAX
 */

(function() {
    'use strict';
    
    // Créer l'overlay de chargement
    function createLoadingOverlay() {
        if (document.getElementById('loading-overlay')) return;
        
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(overlay);
    }
    
    // Afficher le spinner
    function showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('show');
        }
    }
    
    // Cacher le spinner
    function hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }
    
    // Initialisation
    document.addEventListener('DOMContentLoaded', function() {
        createLoadingOverlay();
        
        // Intercepter toutes les soumissions de formulaires
        document.addEventListener('submit', function(e) {
            const form = e.target;
            
            // Ignorer les formulaires de recherche/filtres
            if (form.method.toLowerCase() === 'get') return;
            
            // Afficher le spinner
            showLoading();
            
            // Désactiver le bouton submit
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
        
        // Intercepter les liens qui déclenchent des actions
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            
            if (!link) return;
            
            // Afficher le spinner pour les liens de suppression, export, etc.
            if (link.href.includes('/delete/') || link.href.includes('/export/')) {
                showLoading();
                
                // Cacher après 5 secondes max (sécurité)
                setTimeout(hideLoading, 5000);
            }
        });
        
        // Cacher le spinner si la page se recharge
        window.addEventListener('pageshow', function() {
            hideLoading();
        });
        
        // Exposer les fonctions globalement
        window.showLoading = showLoading;
        window.hideLoading = hideLoading;
    });
})();
