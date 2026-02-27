/**
 * FinTrack - Système de Toast Notifications Moderne
 * Notifications élégantes et non-intrusives
 */

class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Créer le conteneur de toasts s'il n'existe pas
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            this.container.setAttribute('aria-live', 'polite');
            this.container.setAttribute('aria-atomic', 'true');
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    /**
     * Affiche un toast
     * @param {string} message - Message à afficher
     * @param {string} type - Type: success, error, warning, info
     * @param {number} duration - Durée en ms (défaut: 6000)
     */
    show(message, type = 'info', duration = 6000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const icon = this.getIcon(type);
        const closeBtn = `<button type="button" class="toast-close" aria-label="Fermer">&times;</button>`;
        const progressBar = duration > 0 ? `<div class="toast-progress"></div>` : '';
        
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            ${closeBtn}
            ${progressBar}
        `;

        // Ajouter au conteneur
        this.container.appendChild(toast);
{
            toast.classList.add('show');
            
            // Animer la barre de progression
            const progressBar = toast.querySelector('.toast-progress');
            if (progressBar && duration > 0) {
                progressBar.style.animationDuration = `${duration}ms`;
            }
        }
        // Animation d'entrée
        setTimeout(() => toast.classList.add('show'), 10);

        // Gestionnaire de fermeture
        const closeButton = toast.querySelector('.toast-close');
        const close = () => {
            toast.classList.remove('show');
            toast.classList.add('fade-out');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        };

        closeButton.addEventListener('click', close);

        // Auto-fermeture avec pause au survol
        let autoCloseTimer = null;
        let remainingTime = duration;
        let startTime = Date.now();
        
        function startAutoClose() {
            if (duration > 0) {
                startTime = Date.now();
                autoCloseTimer = setTimeout(close, remainingTime);
            }
        }
        
        // Pause au survol
        toast.addEventListener('mouseenter', () => {
            if (autoCloseTimer) {
                clearTimeout(autoCloseTimer);
                remainingTime -= (Date.now() - startTime);
            }
        });
        
        // Reprendre au départ du survol
        toast.addEventListener('mouseleave', () => {
            startAutoClose();
        });
        
        // Démarrer l'auto-fermeture
        startAutoClose();

        return toast;
    }

    getIcon(type) {
        const icons = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-x-circle-fill"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>'
        };
        return icons[type] || icons.info;
    }

    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 8000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 7000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 6000) {
        return this.show(message, 'info', duration);
    }
}

// Instance globale
window.Toast = new ToastManager();

// Convertir les messages Django en toasts (1 seule fois)
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si déjà affiché pendant cette session
    if (sessionStorage.getItem('toasts-displayed')) {
        return;
    }
    
    const djangoMessages = document.querySelectorAll('.alert');
    
    if (djangoMessages.length > 0) {
        djangoMessages.forEach(alert => {
            const message = alert.textContent.trim();
            let type = 'info';
            
            if (alert.classList.contains('alert-success')) type = 'success';
            else if (alert.classList.contains('alert-danger') || alert.classList.contains('alert-error')) type = 'error';
            else if (alert.classList.contains('alert-warning')) type = 'warning';
            
            // Afficher en toast
            window.Toast.show(message, type);
            
            // Masquer l'alerte Django
            alert.style.display = 'none';
        });
        
        // Marquer comme affiché pour éviter les doublons
        sessionStorage.setItem('toasts-displayed', Date.now());
        
        // Nettoyer après 500ms
        setTimeout(() => {
            sessionStorage.removeItem('toasts-displayed');
        }, 500);
    }
});

