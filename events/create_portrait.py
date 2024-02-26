# portrait_creator.py
import os
from PIL import Image
from django.core.files.base import ContentFile
from tempfile import NamedTemporaryFile
from django.utils.text import slugify

def create_portrait(event):
    if event.thumb and event.thumb.file and not event.portrait:
        thumb_path = event.thumb.path

        # Open the thumbnail image
        with Image.open(thumb_path) as img:
            # Resize the image to create the portrait
            portrait = img.resize((600, 900))  # Adjust dimensions as needed

            # Save the portrait to a temporary file
            temp_file = NamedTemporaryFile(delete=False)
            portrait.save(temp_file, 'JPEG')
            temp_file.close()

            # Read the temporary file and create a ContentFile
            with open(temp_file.name, 'rb') as temp_file_content:
                content_file = ContentFile(temp_file_content.read(), name=f'{slugify(event.title)}_portrait.jpg')

            # Update the model's portrait field
            event.portrait.save(content_file.name, content_file, save=True)

            # Remove the temporary file
            os.remove(temp_file.name)
