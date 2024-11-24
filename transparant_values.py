from PIL import Image

def extract_opaque_pixel_locations(image_path):
    image = Image.open(image_path)
    opaque_pixel_locations = []

    # Convert the image to RGBA mode (if not already)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    width, height = image.size
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            # Get the pixel value and alpha channel
            pixel = pixels[x, y]
            alpha = pixel[3]

            # If the pixel is opaque (alpha = 255), add its location to the list
            if alpha != 255:
                opaque_pixel_locations.append([x, y])

    return opaque_pixel_locations

# Example usage
image_path = './media/piece_black.png'
opaque_pixel_locations = extract_opaque_pixel_locations(image_path)
amount_of_pixels = 38 ** 2
circle_area = 3.142 * 19 ** 2

print(F"From {amount_of_pixels}, {len(opaque_pixel_locations)} are transparant")
print(F"Expected {circle_area}, pixels to be non transparant")

# Display the opaque pixel locations
for location in opaque_pixel_locations:
    location[0] += 1
    location[1] += 1

for x in list(range(0, 40)):
    opaque_pixel_locations.append([x, 0])
    opaque_pixel_locations.append([x, 39])

for y in list(range(0, 40)):
    opaque_pixel_locations.append([0, y])
    opaque_pixel_locations.append([39, y])

unique_opaque_pixel_locations = set(tuple(coord) for coord in opaque_pixel_locations)

print(F"{unique_opaque_pixel_locations = }")

