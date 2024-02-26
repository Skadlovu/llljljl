from .views import calendar_view, EventDateView, UserEventListView, all_tag,tagged_events,toggle_attending, LikeEventView, get_event, recently_posted_events,home, search,eventlist,categorylist,categoryview,citylist,cityview,create_event,upcoming_events,event_review_detail,event_review_list,create_event_review,trending_events,most_viewed
from django.urls import path

app_name='events'

urlpatterns=[
    path('events/search/', search, name='search'),
    path('events/event/<event_id>', get_event,name='event'),
    path('events/event_list',eventlist, name='home'),
    path('events/category_list <str:slug>/', categorylist, name='categorylist'),
    path('events/category_view/',categoryview, name='category'),
    path('events/city_view/',cityview, name='city'),
    path('events/city_list <str:slug>/',citylist, name='citylist'),
    path('events/new/', create_event,name='create_event'),
    path('events/upcoming_events/', upcoming_events, name='upcoming_events'),
    path('reviews/', event_review_list, name='event_review_list'),
    path('<int:event_id>/reviews/create/', create_event_review, name='create_event_review'),
    path('<int:event_id>/reviews/<int:review_id>/', event_review_detail, name='event_review_detail'),
    path('', home, name='home'),
    path('events/recently_posted/', recently_posted_events, name='recently_posted'),
    path('events/most_viewed/', most_viewed, name='most_viewed'),
    path('events/trending_events/', trending_events ,name='trending_events'),
    path('events/event/<int:event_id>/', LikeEventView.as_view(), name='like_event'),
    path('events/toggle_attending/<int:event_id>/', toggle_attending, name='toggle_attending'),
    path('events/tags/', all_tag, name='all_tags'),
    path('events/tags/<slug:slug>/', tagged_events, name='tagged_events'),
    path('events/user/<str:username>',UserEventListView.as_view(template_name='events/user_events.html'),name='user_events'),
    path('events/date/<int:year>/<int:month>/<int:day>/', EventDateView.as_view(), name='event_date'),
    path('events/calendar/', calendar_view, name='calendar'),
    #path('events/user_events',user_events,name='user_events')
]