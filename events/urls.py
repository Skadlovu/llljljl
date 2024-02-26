from .views import review_list, monthly_view,events_today,events_this_week, event_date_view, user_events, submit_comment, calendar_view, EventDateView, UserEventListView, all_tag,tagged_events,toggle_attending, LikeEventView,get_event, recently_posted_events,home, search,categorylist,categoryview,citylist,cityview,create_event,upcoming_events,trending_events,most_viewed
from django.urls import path


app_name='events'

urlpatterns=[
    path('events/search/', search, name='search'),
    path('events/event/<event_id>', get_event,name='event'),
    #path('events/event_list',eventlist, name='home'),
    path('events/category_list <str:slug>/', categorylist, name='categorylist'),
    path('events/category_view/',categoryview, name='category'),
    path('events/city_view/',cityview, name='city'),
    path('events/city_list <str:slug>/',citylist, name='citylist'),
    path('events/new/', create_event,name='create_event'),
    path('events/upcoming_events/', upcoming_events, name='upcoming_events'),
    path('', home, name='home'),
    path('events/recently_posted/', recently_posted_events, name='recently_posted'),
    path('events/most_viewed/', most_viewed, name='most_viewed'),
    path('events/trending_events/', trending_events ,name='trending_events'),
    path('events/event/<int:event_id>/', LikeEventView.as_view(), name='like_event'),
    path('events/event/<int:event_id>/', toggle_attending, name='toggle_attending'),
    path('events/tags/', all_tag, name='all_tags'),
    path('events/tags/<slug:slug>/', tagged_events, name='tagged_events'),
    path('events/user/<str:username>',UserEventListView.as_view(template_name='events/user_events.html'),name='user_events'),
    path('events/calendar/', calendar_view, name='calendar'),
    path('events/event<int:event_id>/submit_comment/', submit_comment, name='submit_comment'),
    path('events/user_events/<username>',user_events,name='user_events'),
    path('events/event_date/<int:year>/<int:month>/<int:day>', event_date_view, name='event_date_view'),
    path('events/monthly_view/', monthly_view, name='monthly_view'),
    path('events/events_today/', events_today, name='events_today'),
    path('events/events_this_week/', events_this_week, name='events_this_week'),
    path('events/event_review_list/',review_list,name='review_list')
]


