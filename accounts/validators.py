"""
Validateurs personnalisés pour les fichiers uploadés
"""
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import os


def validate_image_file(image):
    """
    Valide qu'un fichier uploadé est bien une image valide.
    
    Vérifie:
    - Type MIME
    - Extension
    - Taille max (5 MB)
    - Dimensions max (4000x4000)
    """
    # Vérifier la taille du fichier
    max_size_mb = 5
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'La taille du fichier ne doit pas dépasser {max_size_mb} MB.')
    
    # Vérifier l'extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Format de fichier non autorisé. Utilisez: {", ".join(valid_extensions)}'
        )
    
    # Vérifier que c'est vraiment une image (pas juste l'extension)
    try:
        # get_image_dimensions retourne (width, height) ou None si pas une image
        width, height = get_image_dimensions(image)
        
        if width is None or height is None:
            raise ValidationError('Le fichier n\'est pas une image valide.')
        
        # Vérifier les dimensions maximales
        max_dimension = 4000
        if width > max_dimension or height > max_dimension:
            raise ValidationError(
                f'Les dimensions de l\'image ne doivent pas dépasser {max_dimension}x{max_dimension} pixels.'
            )
            
    except Exception as e:
        raise ValidationError(f'Erreur lors de la validation de l\'image: {str(e)}')
    
    return image


def validate_file_size(file, max_mb=10):
    """
    Validateur générique pour la taille de fichier.
    
    Args:
        file: Le fichier à valider
        max_mb: Taille maximale en MB (défaut: 10)
    """
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f'La taille du fichier ne doit pas dépasser {max_mb} MB.')
    return file
