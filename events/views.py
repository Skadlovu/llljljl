from django.shortcuts import render, get_object_or_404, redirect 
from .models import Event, Category,City,Comment,Review
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from .forms import EventSearchForm
from viewanalytics.models import Analytics
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .forms import EVentUploadForm,CommentForm,ReviewComment,ReviewRatingForm
import random
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import datetime as time
from django.http import HttpResponseBadRequest,JsonResponse
from django.urls import reverse
from django.views.generic import ListView, CreateView,DetailView
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.functions import Extract
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from taggit.models import Tag
from django.utils.decorators import method_decorator
from schedule.models import Calendar, Event as SchedulerEvent
from django.contrib import messages





class EventDateView(ListView):
    model = Event
    template_name = 'events/event_date.html'  # Create this template
    context_object_name = 'events'

    def get_queryset(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        day = self.kwargs['day']
        date = f'{year}-{month:02d}-{day:02d}'  # Format the date
        return Event.objects.filter(event_date=date)
    


def event_date_view(request, year, month, day):
    # Convert year, month, and day to integers
    year = int(year)
    month = int(month)
    day = int(day)

    # Retrieve events for the specified date
    events = Event.objects.filter(event_date__year=year, event_date__month=month, event_date__day=day)

    # Pass events and date to the template
    context = {
        'events': events,
        'date': f'{year}-{month:02d}-{day:02d}',
    }
    return render(request, 'events/event_date.html', context)





class UserEventListView(ListView):
    model= Event
    template_name='events/user_events.html'
    context_object_name='events'

    def get_quaryset(self):
        user= get_object_or_404(User,username=self.kwargs.get('username'))
        return Event.objects.filter(uploaded_by=user).order_by('-upload_date')




def all_tag(request):
    tags=Tag.objects.all()
    return render(request, 'events/tags.html', {'tags':tags})




def tagged_events(request,slug):
    tag=get_object_or_404(Tag,slug=slug)
    events=Event.objects.filter(tags__in=[tag])
    context={
        'tag': tag,
        'events':events
    }
    return render(request,'events/tagged_events.html',context)




def paginate_events(request, events, page_size):
    paginator = Paginator(events, page_size)
    page = request.GET.get('page')

    try:
        paginated_events = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        paginated_events = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results.
        paginated_events = paginator.page(paginator.num_pages)

    return paginated_events



def paginate_categories(request, category, page_size):
    paginator = Paginator(category, page_size)
    page = request.GET.get('page')

    try:
        paginated_category = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        paginated_category= paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results.
        paginated_category = paginator.page(paginator.num_pages)

    return paginated_category



def paginate_all_tags(request, all_tags, page_size):
    paginator = Paginator(all_tags, page_size)
    page = request.GET.get('page')

    try:
        paginated_all_tags = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        paginated_all_tags= paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results.
        paginated_all_tags = paginator.page(paginator.num_pages)

    return paginated_all_tags



def categorylist(request, slug):
    template='events/category_list.html'
    if (Category.objects.filter(slug=slug, status=0)):
        events=Event.objects.filter(category__slug=slug)
        category=Category.objects.filter(slug=slug).first()
        context={'events':events, 'category':category}

        events_per_page=20
        paginator=Paginator(events, events_per_page)
        page=request.GET.get('page')
        try:
            events=paginator.page('page')
        except PageNotAnInteger:
            events=paginator.page(1)
        except EmptyPage:
            events=paginator.page(paginator.num_pages)
        return render(request, template,context)


def home(request):
    #decay=0.05
    template='events/home.html'
    trending_events = Event.objects.annotate(
        age_in_days=ExpressionWrapper(
            Extract('upload_date', 'day', output_field=fields.IntegerField()) +
            Extract('upload_date', 'month', output_field=fields.IntegerField()) * 30 +
            Extract('upload_date', 'year', output_field=fields.IntegerField()) * 365,
            output_field=fields.IntegerField()
        )
    )

    # Calculate the trending score based on views, likes, attending count, and age_in_days
    trending_events = trending_events.annotate(
        trending_score=(F('views') + F('likes') + F('attending') * 2) / (F('age_in_days') + 1)  # Added 1 to handle potential division by zero
    ).order_by('-trending_score')
    most_viewed=Event.objects.all().order_by('-views')
    recently_posted_events = Event.objects.all().order_by('-upload_date')
    upcoming_events=Event.objects.all().order_by('event_date')
    category=Category.objects.all().order_by('name')
    city=City.objects.all().order_by('name')
    tags=Tag.objects.all().order_by('name')
    
    paginated_trending_events=paginate_events(request,trending_events,page_size=12)
    paginated_most_viewed=paginate_events(request,most_viewed,page_size=12)
    paginated_recently_posted_events=paginate_events(request,recently_posted_events,page_size=12)
    paginated_upcoming_events=paginate_events(request,upcoming_events,page_size=9)
    paginated_categories=paginate_categories(request,category,page_size=6)
    paginated_tags=paginate_all_tags(request,tags,page_size=6)

    context={
        'most_viewed':paginated_most_viewed,
        'trending_events':paginated_trending_events,
        'recently_posted_events':paginated_recently_posted_events,
        'upcoming_events':paginated_upcoming_events,
        'categories':paginated_categories,
        'city':city,
        'tags':paginated_tags

    }

  

    return render(request,template,context)




def recently_posted_events(request):
    recently_posted_events = Event.objects.all().order_by('-upload_date')
    paginated_recently_posted_events=paginate_events(request,recently_posted_events,page_size=18)
    context={
        'recently_posted_events':paginated_recently_posted_events
    }
   
    return render(request, 'events/recently_posted_events.html', context)





      
def most_viewed(request):
     most_viewed=Event.objects.all().order_by('-views')
     paginated_most_viewed=paginate_events(request,most_viewed,page_size=9)
     context={
          'most_viewed':paginated_most_viewed
     }
     return render(request,'events/most_viewed.html',context)





def search(request):
    events=[]
    query=''
    if 'title' in request.GET:
        form=EventSearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['title']
            events=Event.objects.filter(title__icontains=query)
    else:
        form=EventSearchForm()
    return render(request, 'events/search.html', {'form':form, 'events':events})






def categoryview(request):
    template='events/category.html'
    category=Category.objects.filter(status=0).order_by('name')
    context={'category':category}
    category_with_count=category.annotate(event_count=Count('event'))
    context={'category':category_with_count}
    return render(request, template, context)


    



def cityview(request):
    template='events/city.html'
    city=City.objects.filter(status=0).order_by('name')
    context={'city':city}
    city_with_count=city.annotate(event_count=Count('event'))
    context={'city':city_with_count}
    return render(request, template, context)




def citylist(request, slug):
    template='events/city_list.html'
    if (City.objects.filter(slug=slug, status=0)):
        events=Event.objects.filter(city__slug=slug)
        city=City.objects.filter(slug=slug).first()
        context={'events':events, 'city':city}

        events_per_page=20
        paginator=Paginator(events, events_per_page)
        page=request.GET.get('page')
        try:
            events=paginator.page('page')
        except PageNotAnInteger:
            events=paginator.page(1)
        except EmptyPage:
            events=paginator.page(paginator.num_pages)
        return render(request, template,context)




@login_required
def create_event(request):
    if request.method == 'POST':
        form = EVentUploadForm(request.POST,  request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.uploaded_by = request.user  # Set the user creating the event
            event.save()
            form.save_m2m()
            return redirect('/')
    else:
        form = EVentUploadForm()

    return render(request, 'events/create_event.html', {'form': form})




def upcoming_events(request):
    current_datetime = timezone.now()

    # Get the upcoming events within the next seven days
    seven_days_from_now = current_datetime + timedelta(days=365)
    upcoming_events = Event.objects.filter(event_date__range=[current_datetime, seven_days_from_now]).order_by('event_date')

    # Calculate the time difference for each event
    for event in upcoming_events:
        event_datetime = timezone.make_aware(datetime.combine(event.event_date, event.event_time), time.timezone.utc)
        event.time_until_start = event_datetime - current_datetime

    return render(request, 'events/upcoming_events.html', {'upcoming_events': upcoming_events})





@method_decorator(login_required, name='dispatch')
class LikeEventView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, event_id):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # This is an AJAX request
            event = get_object_or_404(Event, id=event_id)

            if request.user in event.likes.all():
                # User has already liked the event, unlike it
                event.likes.remove(request.user)
                liked = False
            else:
                # User hasn't liked the event, like it
                event.likes.add(request.user)
                liked = True

            response_data = {'liked': liked, 'like_count': event.likes.count()}
            return JsonResponse(response_data)

        # Return a regular HTTP response if it's not an AJAX request
        return redirect('events:event', event_id=event_id)
    

    

def toggle_attending(request, event_id):
    if request.user.is_authenticated:
        event = get_object_or_404(Event, id=event_id)

        if request.user in event.attending.all():
            # User is attending, remove them
            event.attending.remove(request.user)
            attending_status = False
        else:
            # User is not attending, add them
            event.attending.add(request.user)
            attending_status = True

        return JsonResponse({'attending': attending_status, 'attending_count': event.attending.count()})

    return JsonResponse({'error': 'User not authenticated'})




def calendar_view(request):
    # Fetch all events from both models
    django_events = Event.objects.all()
    scheduler_events = SchedulerEvent.objects.all()

    # Create a list of all events
    all_events = list(django_events) + list(scheduler_events)

    # Debugging: Print the number of events and their titles
    print("Total number of events:", len(all_events))
    for event in all_events:
        print("Event title:", event.title)

    # Pass the list to the template
    context = {'events': all_events}
    return render(request, 'events/calendar.html', context)




def get_event(request, event_id):
    template = 'events/event.html'
    event = Event.objects.get(id=event_id)
    categories = random.sample(list(Category.objects.all()), 10)
    cities = random.sample(list(City.objects.all()), 4)
    comments = Comment.objects.filter(event=event_id)
    current_datetime = timezone.now()
    event_datetime = timezone.make_aware(datetime.combine(event.event_date, event.event_time), time.timezone.utc)
    event_count_down = event_datetime - current_datetime
    days, seconds = divmod(event_count_down.total_seconds(), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    timer = {
        'days': int(days),
        'hours': int(hours),
        'minutes': int(minutes),
        'seconds': int(seconds)
    }

    form = CommentForm()

    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    is_views = Analytics.objects.filter(eventId=event_id, sesID=session_key)

    if is_views.count() == 0 and str(session_key) != "None":
        views = Analytics()
        views.sesID = session_key
        views.eventId = event
        views.save()
        event.views += 1
        event.save()
    
    try:
        related_events = random.sample(list(event.get_related_events()), 1)
    except Exception as e:
        print(f"Error retrieving related events: {str(e)}")
        related_events = []


    context = {'event': event, 'related_events': related_events, 'categories': categories, 'cities': cities,
               'comments': comments, 'timer': timer, 'form': form}

    return render(request, template, context)



@login_required
def submit_comment(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.event = event
            comment.save()
            # Add debug message
            messages.success(request, 'Comment saved successfully.')
            return redirect('events:event', event_id=event_id)
        else:
            # Add debug message for invalid form
            messages.error(request, 'Form is not valid.')
    else:
        # Add debug message for non-POST request
        messages.error(request, 'Form submission failed: method is not POST.')
    return redirect('events:event', event_id=event_id)




def review_list(request):
    template='events/events_review_list.html'
    reviews=Review.objects.all().order_by('created_at')
    context={
       'reviews':reviews
    }
    return render(request,template,context)





def review(request):
    template='events/event_review.html'
    event_review=Review.objects.get(id=id)
    comments=ReviewComment.objects.filter(id=id)

    try:
        categories = random.sample(list(Category.objects.all()), 10)
    except Exception as e:
        print('Not enough categories')
        categories=[]


    try:
        cities = random.sample(list(City.objects.all()), 4)
    except Exception as e:
        print('Not enough cities')
        cities=[]


    try:
        other_reviews=random.sample(list(Review.objects.all()), 5)
    except Exception as e:
        print('Not enough reviews')
        other_reviews=[]


    rating_form=ReviewRatingForm()
    comment_form=ReviewComment()
    if request.method == 'POST':
        review=get_object_or_404(Review,id=id)
        rating_form=ReviewRatingForm(request.POST,request.user)
        comment_form=ReviewComment(request.POST,request.user)
        if comment_form and rating_form.is_valid:
            rating_form=rating_form.save(commit=False)
            comment_form=comment_form.save(commit=False)
            rating_form=review.user_ratings.save()
            comment_form=review.user_comments.save()
            review.save()
            return redirect('events:review', id=id)
        
    context={
        'event_review':event_review,
        'comment_form':comment_form,
        'rating_form':rating_form,
        'other_reviews':other_reviews,
        'cities':cities,
        'categories':categories,
        'comments':comments
    }

    return render(request, template,context)




def user_events(request, username):
    template = 'events/user_events.html'
    user = get_object_or_404(User, username=username)
    events = Event.objects.filter(uploaded_by=user).order_by('-upload_date')

    context = {
        'user': user,
        'events': events
    }
    return render(request, template, context)



def monthly_view(request):
    # Get the current month and year
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year

    # Fetch events for the current month and year
    events = Event.objects.filter(event_date__month=current_month, event_date__year=current_year).order_by('event_date')

    # Pass the events and current month/year to the template
    context = {
        'events': events,
        'current_month': current_month,
        'current_year': current_year,
    }
    return render(request, 'events/monthly_view.html', context)




def events_today(request):
    # Get today's date
    today = timezone.now().date()

    # Query events happening today
    events = Event.objects.filter(event_date=today)

    context = {'events': events,'today':today}
    return render(request, 'events/events_today.html', context)




def events_this_week(request):
    # Get today's date
    today = timezone.now().date()

    # Calculate the start of the week as the current day
    start_of_week = today

    # Calculate the end of the week as 6 days after the start of the week
    end_of_week = start_of_week + timedelta(days=6)

    # Query events happening this week
    events = Event.objects.filter(event_date__range=[start_of_week, end_of_week])

    context = {
        'events': events,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week
    }
    return render(request, 'events/events_this_week.html', context)



def trending_events(request):
    # Define weights for each metric (adjust as needed)
    VIEW_WEIGHT = 0.4
    LIKE_WEIGHT = 0.2
    COMMENT_WEIGHT = 0.2
    ATTENDING_WEIGHT = 0.2  # Adjust based on importance

    MAX_ATTENDING = 1000  # Replace 1000 with the actual maximum attendance value
    MAX_VIEWS=1000
    MAX_LIKES=1000
    MAX_COMMENTS=1000



    # Query events and calculate normalized metrics
    events = Event.objects.annotate(
        normalized_views=ExpressionWrapper(F('views') / MAX_VIEWS, output_field=fields.FloatField()),
        normalized_likes=ExpressionWrapper(F('likes') / MAX_LIKES, output_field=fields.FloatField()),
        normalized_comments=ExpressionWrapper(F('comments') / MAX_COMMENTS, output_field=fields.FloatField()),
        normalized_attending=ExpressionWrapper(F('attending') / MAX_ATTENDING, output_field=fields.FloatField()),
    )

    # Calculate popularity score for each event
    events = events.annotate(
        popularity_score=(
            VIEW_WEIGHT * F('normalized_views') +
            LIKE_WEIGHT * F('normalized_likes') +
            COMMENT_WEIGHT * F('normalized_comments') +
            ATTENDING_WEIGHT * F('normalized_attending')
        )
    )

    # Sort events by popularity score (descending)
    trending_events = events.order_by('-popularity_score')

    # Pass trending events to the template
    context = {'trending_events': trending_events}
    return render(request, 'events/trending_events.html', context)




"""""
class EventReviewDetailView(DetailView):
    model = EventReview
    template_name = 'eventsevent_review_detail.html'


class EventReviewListView(ListView):
    model = EventReview
    template_name = 'event_review_list.html'
    context_object_name = 'event_reviews'


class CreateReviewView(CreateView):
    model = EventReview
    form_class = EventReviewForm
    template_name = 'create_review.html'

    def form_valid(self, form):
        event_slug = self.kwargs['event_slug']
        event = get_object_or_404(Event, slug=event_slug)
        form.instance.event = event
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('event_review_list')





"""
