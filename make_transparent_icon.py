from PIL import Image

# Open the logo
img = Image.open('logo.png').convert('RGBA')
pixels = img.load()
width, height = img.size

# Make white pixels transparent
for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        # If pixel is white (or very close to white)
        if r >= 250 and g >= 250 and b >= 250:
            pixels[x, y] = (255, 255, 255, 0)  # Make it transparent

# Save as PNG with transparency
img.save('logo_transparent.png')
print('✓ Transparent PNG created')

# Save as ICO with multiple sizes
img.save('logo.ico', format='ICO', sizes=[
    (256, 256),
    (128, 128),
    (64, 64),
    (48, 48),
    (32, 32),
    (16, 16)
])
print('✓ ICO file created with transparency')
print('Done! The logo.ico file now has a transparent background.')
