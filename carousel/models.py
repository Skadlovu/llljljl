from django.db import models

class CarouselImage(models.Model):
    image=models.ImageField(upload_to='carousl_images')
    caption=models.CharField(max_length=255,blank=True)
    status=models.BooleanField()

    def __str__(self):
        return self.caption

