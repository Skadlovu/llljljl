import os
from PIL import Image
from django.core.files.base import ContentFile
from tempfile import NamedTemporaryFile
from django.utils.text import slugify

def create_landscape(event):
    if event.thumb and event.thumb.file and not event.landscape:
        thumb_path = event.thumb.path

        # Open the thumbnail image
        with Image.open(thumb_path) as img:
            # Resize the image to create the landscape
            landscape = img.resize((900, 571))  # Adjust dimensions as needed

            # Save the landscape to a temporary file
            temp_file = NamedTemporaryFile(delete=False)
            landscape.save(temp_file, 'JPEG')
            temp_file.close()

            # Read the temporary file and create a ContentFile
            with open(temp_file.name, 'rb') as temp_file_content:
                content_file = ContentFile(temp_file_content.read(), name=f'{slugify(event.title)}_landscape.jpg')

            # Update the model's landscape field
            event.landscape.save(content_file.name, content_file, save=True)

            # Remove the temporary file
            os.remove(temp_file.name)
