#!/usr/bin/env python3
"""
Script pour générer les icônes PWA à partir du favicon SVG
Crée les icônes nécessaires pour le manifest.json
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Créer le dossier static/icons s'il n'existe pas
ICONS_DIR = os.path.join('static', 'icons')
os.makedirs(ICONS_DIR, exist_ok=True)

def create_icon(size, filename, maskable=False):
    """
    Créer une icône PWA avec le logo MonNkap
    
    Args:
        size: Taille de l'icône (192, 512, etc.)
        filename: Nom du fichier de sortie
        maskable: Si True, ajoute une marge de sécurité (safe zone)
    """
    # Créer l'image avec fond bleu MonNkap
    img = Image.new('RGB', (size, size), color='#0066FF')
    draw = ImageDraw.Draw(img)
    
    # Calculer les marges
    if maskable:
        # Zone de sécurité pour maskable : 80% au centre
        margin = int(size * 0.1)  # 10% de chaque côté
    else:
        margin = int(size * 0.05)  # 5% de marge
    
    # Dessiner un cercle blanc au centre
    circle_size = size - (2 * margin)
    circle_bbox = [margin, margin, margin + circle_size, margin + circle_size]
    draw.ellipse(circle_bbox, fill='white', outline='white')
    
    # Ajouter le texte "Nk" au centre (stylisé)
    try:
        # Essayer différentes polices système
        font_size = int(circle_size * 0.4)
        try:
            # Windows
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                # Fallback : police par défaut
                font = ImageFont.load_default()
        
        text = "Nk"
        
        # Centrer le texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - int(font_size * 0.1)  # Ajustement vertical
        
        draw.text((text_x, text_y), text, fill='#0066FF', font=font)
    except Exception as e:
        print(f"⚠️  Impossible d'ajouter le texte: {e}")
    
    # Sauvegarder
    filepath = os.path.join(ICONS_DIR, filename)
    img.save(filepath, 'PNG', optimize=True)
    print(f"✅ Créé: {filepath} ({size}x{size})")

def main():
    print("🎨 Génération des icônes PWA pour MonNkap...\n")
    
    # Icônes standard
    create_icon(192, 'icon-192.png', maskable=False)
    create_icon(512, 'icon-512.png', maskable=False)
    
    # Icônes maskables (avec safe zone pour Android)
    create_icon(192, 'icon-maskable-192.png', maskable=True)
    create_icon(512, 'icon-maskable-512.png', maskable=True)
    
    # Apple touch icon
    create_icon(180, 'apple-touch-icon.png', maskable=False)
    
    print("\n✅ Toutes les icônes PWA ont été générées dans", ICONS_DIR)
    print("\n📱 Prochaines étapes:")
    print("1. Vérifier les icônes dans static/icons/")
    print("2. Déployer sur Render")
    print("3. Tester l'installation PWA sur mobile (Chrome)")
    print("4. Vérifier que l'icône s'affiche correctement")

if __name__ == '__main__':
    main()
