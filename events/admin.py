from django.contrib import admin
from .models import Category,Event,City, EventReview,Comment

class EventAdmin(admin.ModelAdmin):
	list_display = ('category', 'title', 'description','views')
	prepopulated_fields = {'slug':('title','category')}


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'description','number_of_events')
	prepopulated_fields={'slug':('name','description')}

	class Meta:
		ordering = ['name']

class CityAdmin(admin.ModelAdmin):
	list_display = ('name', 'description','number_of_events')
	prepopulated_fields={'slug':('name','description')}

	class Meta:
		ordering = ['name']

class EventReviewadmin(admin.ModelAdmin):
	list_display=('event', 'user', 'ratings')



admin.site.register(Event, EventAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(City,CityAdmin)
admin.site.register(EventReview,EventReviewadmin)
admin.site.register(Comment)

# Register your models here.
