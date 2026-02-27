/**
 * FinTrack - Skeleton Loader Integration Script
 * Gestion intelligente de l'affichage du skeleton loader
 */

document.addEventListener('DOMContentLoaded', function() {
    const skeletonLoader = document.getElementById('skeleton-loader');
    const dashboardContent = document.getElementById('dashboard-content');
    
    // Afficher le skeleton pendant le chargement si la page prend du temps
    let showSkeleton = false;
    const skeletonTimeout = setTimeout(() => {
        if (skeletonLoader && dashboardContent) {
            showSkeleton = true;
            skeletonLoader.style.display = 'block';
            dashboardContent.style.opacity = '0';
        }
    }, 100); // Attendre 100ms avant d'afficher le skeleton
    
    // Une fois le contenu chargé, masquer le skeleton
    window.addEventListener('load', function() {
        clearTimeout(skeletonTimeout);
        
        if (showSkeleton && skeletonLoader && dashboardContent) {
            // Animation de transition
            dashboardContent.style.transition = 'opacity 0.3s ease-in';
            dashboardContent.style.opacity = '1';
            
            setTimeout(() => {
                skeletonLoader.style.display = 'none';
            }, 300);
        } else if (dashboardContent) {
            dashboardContent.style.opacity = '1';
        }
    });
});

/**
 * Fonction utilitaire pour afficher des toasts de succès après actions
 */
function showSuccessToast(message) {
    if (window.Toast) {
        window.Toast.success(message);
    }
}

function showErrorToast(message) {
    if (window.Toast) {
        window.Toast.error(message);
    }
}

function showInfoToast(message) {
    if (window.Toast) {
        window.Toast.info(message);
    }
}

// Exposer globalement pour utilisation dans d'autres scripts
window.showSuccessToast = showSuccessToast;
window.showErrorToast = showErrorToast;
window.showInfoToast = showInfoToast;
