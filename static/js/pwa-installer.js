/**
 * FinTrack - PWA Intelligent Installer
 * Détecte l'OS et affiche les instructions appropriées
 */

(function() {
    'use strict';

    // Détection de l'OS
    function detectOS() {
        const userAgent = window.navigator.userAgent.toLowerCase();
        const platform = window.navigator.platform.toLowerCase();

        if (/iphone|ipad|ipod/.test(userAgent)) {
            return 'ios';
        } else if (/android/.test(userAgent)) {
            return 'android';
        } else if (/win/.test(platform)) {
            return 'windows';
        } else if (/mac/.test(platform)) {
            return 'macos';
        } else if (/linux/.test(platform)) {
            return 'linux';
        }
        return 'unknown';
    }

    // Mapping OS → ID accordéon
    const osToAccordion = {
        'android': 'collapseAndroid',
        'ios': 'collapseiOS',
        'windows': 'collapseWindows',
        'macos': 'collapseWindows', // Mac utilise Chrome/Edge comme Windows
        'linux': 'collapseWindows'
    };

    document.addEventListener('DOMContentLoaded', function() {
        const os = detectOS();
        const installModal = document.getElementById('installModal');
        
        if (!installModal) return;

        // Quand le modal s'ouvre
        installModal.addEventListener('shown.bs.modal', function() {
            const accordionId = osToAccordion[os];
            
            if (accordionId) {
                // Ouvrir automatiquement l'accordéon approprié
                const targetAccordion = document.getElementById(accordionId);
                if (targetAccordion) {
                    const bsCollapse = new bootstrap.Collapse(targetAccordion, {
                        toggle: true
                    });
                }

                // Masquer les instructions non pertinentes (optionnel)
                const allAccordions = document.querySelectorAll('#installInstructions .accordion-item');
                allAccordions.forEach(item => {
                    const collapseElement = item.querySelector('.accordion-collapse');
                    if (collapseElement && collapseElement.id !== accordionId) {
                        // Ajouter un badge "Autre plateforme"
                        const button = item.querySelector('.accordion-button');
                        if (button && !button.querySelector('.badge')) {
                            const badge = document.createElement('span');
                            badge.className = 'badge bg-secondary ms-2';
                            badge.textContent = 'Autre plateforme';
                            badge.style.fontSize = '0.7rem';
                            button.appendChild(badge);
                        }
                    }
                });

                // Ajouter un badge "Votre appareil" sur la section pertinente
                const relevantItem = document.querySelector(`#${accordionId}`).closest('.accordion-item');
                const relevantButton = relevantItem.querySelector('.accordion-button');
                if (relevantButton && !relevantButton.querySelector('.badge-success')) {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-success ms-2';
                    badge.textContent = '✓ Votre appareil';
                    badge.style.fontSize = '0.7rem';
                    relevantButton.appendChild(badge);
                }
            }
        });
    });

    // Détection du support PWA
    function isPWASupported() {
        return 'serviceWorker' in navigator && 'BeforeInstallPromptEvent' in window;
    }

    // Gestion du bouton d'installation (déjà dans base.html mais amélioration)
    let deferredPrompt;
    const installButton = document.getElementById('pwa-install-btn');

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        if (installButton) {
            installButton.style.display = 'block';
        }
    });

    if (installButton) {
        installButton.addEventListener('click', async () => {
            if (!deferredPrompt) {
                // Afficher le modal avec instructions
                const modal = document.getElementById('installModal');
                if (modal) {
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                }
                return;
            }

            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                if (window.Toast) {
                    window.Toast.success('Application installée avec succès ! 🎉');
                }
            }
            
            deferredPrompt = null;
            installButton.style.display = 'none';
        });
    }

    // Détecter si déjà installé
    window.addEventListener('appinstalled', () => {
        if (installButton) {
            installButton.style.display = 'none';
        }
        if (window.Toast) {
            window.Toast.success('MonNkap est maintenant installé sur votre appareil ! 🚀');
        }
    });

    // Masquer le bouton si déjà en mode standalone
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
        if (installButton) {
            installButton.style.display = 'none';
        }
    }
})();
