#!/usr/bin/env python3
"""Generate app icon and project placeholder images"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon(size=512):
    """Create a beautiful gradient app icon"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gradient background (purple to blue)
    for y in range(size):
        r = int(99 - (y/size) * 30)
        g = int(102 - (y/size) * 40)
        b = int(241 - (y/size) * 50)
        for x in range(size):
            # Circular mask
            cx, cy = size//2, size//2
            dist = ((x-cx)**2 + (y-cy)**2)**0.5
            if dist < size//2 - 10:
                alpha = 255
            elif dist < size//2:
                alpha = int(255 * (size//2 - dist) / 10)
            else:
                alpha = 0
            if alpha > 0:
                img.putpixel((x, y), (r, g, b, alpha))
    
    # Add sparkle/star
    center = size // 2
    star_size = size // 4
    draw.text((center-star_size//2, center-star_size), "✨", fill=(255, 255, 255, 255))
    
    return img

def create_placeholder(name, size=(400, 300)):
    """Create project placeholder image"""
    img = Image.new('RGB', size, (26, 26, 46))
    draw = ImageDraw.Draw(img)
    
    # Gradient overlay
    for y in range(size[1]):
        alpha = int(50 + (y/size[1]) * 100)
        for x in range(size[0]):
            r, g, b = img.getpixel((x, y))
            img.putpixel((x, y), (r + alpha//10, g + alpha//10, b + alpha//5))
    
    # Border
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(99, 102, 241), width=2)
    
    # Text
    text = name[:20]
    bbox = draw.textbbox((0, 0), text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size[0]-tw)//2, (size[1]-th)//2), text, fill=(255, 255, 255))
    
    return img

# Generate assets
os.makedirs('.', exist_ok=True)

# App icon
icon = create_app_icon(512)
icon.save('icon.png')
print("✅ Created icon.png (512x512)")

# Also create smaller version
icon_small = icon.resize((192, 192), Image.LANCZOS)
icon_small.save('icon-192.png')
print("✅ Created icon-192.png")

# Placeholder images for projects
placeholders = ['project-1', 'project-2', 'project-3', 'github', 'portfolio']
for name in placeholders:
    img = create_placeholder(name)
    img.save(f'{name}.png')
    print(f"✅ Created {name}.png")

print("\n🎨 All assets generated!")
