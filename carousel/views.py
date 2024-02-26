from django.shortcuts import render
from.models import CarouselImage


def carousel_view(request):
    images=CarouselImage.objects.all()
    return render(request,'carousel/carousel.html',{'images':images})