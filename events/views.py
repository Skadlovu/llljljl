from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Category,City,EventReview
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from .forms import EventSearchForm
from viewanalytics.models import Analytics
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .forms import EVentUploadForm,EventReviewForm,CommentForm
import random
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import datetime as time
from django.http import HttpResponseBadRequest,JsonResponse
from django.urls import reverse
from django.views.generic import ListView
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.functions import Extract
from comment.models import Comment
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from taggit.models import Tag
from django.utils.decorators import method_decorator
from schedule.models import Calendar, Event as SchedulerEvent



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
            (Extract(F('upload_date'), 'day') - 1) +
            (Extract(F('upload_date'), 'month') - 1) * 30 +
            Extract(F('upload_date'), 'year') * 365,
            output_field=fields.IntegerField()
        )
    ).annotate(
        weighted_score=ExpressionWrapper(
            F('views') + F('likes') + F('attending') * 2,  # Adjust weights as needed
            output_field=fields.IntegerField()
        ) / (1 + 0.05 * F('age_in_days'))  # Adjust the decay factor as needed
    ).order_by('-weighted_score')

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



def trending_events(request):
    trending_events = Event.objects.annotate(
        age_in_days=ExpressionWrapper(
            (Extract(F('upload_date'), 'day') - 1) +
            (Extract(F('upload_date'), 'month') - 1) * 30 +
            Extract(F('upload_date'), 'year') * 365,
            output_field=fields.IntegerField()
        )
    ).annotate(
        weighted_score=ExpressionWrapper(
            F('views') + F('likes') + F('attending') * 2,  # Adjust weights as needed
            output_field=fields.IntegerField()
        ) / (1 + 0.05 * F('age_in_days'))  # Adjust the decay factor as needed
    ).order_by('-weighted_score')
    paginated_trending_events=paginate_events(request,trending_events,page_size=18)
    context={
        'trending_events':paginated_trending_events
    }
    return render(request,'events/trending_events.html',context)







def most_viewed(request):
     most_viewed=Event.objects.all().order_by('-views')
     paginated_most_viewed=paginate_events(request,most_viewed,page_size=9)
     context={
          'most_viewed':paginated_most_viewed
     }
     return render(request,'events/most_viewed.html',context)




def event_review_detail(request, event_id, review_id):
    review=get_object_or_404(EventReview, id=review_id, event__id=event_id)
    return render(request, 'events/event_review_detail.html', {'review':review})




def event_review_list(request):
    reviews=EventReview.objects.all()
    context={'reviews': reviews}
    return render(request, 'events/event_review_list.html',context )





def create_event_review(request, event_id):
    event= get_object_or_404(Event, id=event_id)
    if request.method=="POST":
        form=EventReviewForm(request.POST)
        if form.is_valid():
            review=form.save(commit=False)
            review.user=request.user
            review.event=event
            review.event()
            return redirect('event_review_list', event_id=event.id)
    else:
        form=EventReviewForm()
    return render(request, 'events/create_event_review.html',{'event':event, 'form':form})




def eventlist(request):
    events=Event.objects.all()
    events_per_page=20
    paginator= Paginator(events,events_per_page)

    page=request.GET.get('page')

    try:
        events=paginator.page(page)
    except PageNotAnInteger:
        events=paginator.page(1)
    except EmptyPage:
        events=paginator.page(paginator.num_pages)
    return render(request,'events/event_list.html', {'events': events})



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




def get_event(request, event_id):
    template = 'events/event.html'
    event = Event.objects.get(id=event_id)
    related_events = random.sample(list(event.get_related_events()), 1)
    categories = random.sample(list(Category.objects.all()), 10)
    cities = random.sample(list(City.objects.all()), 4)
    comments = event.comments.all()
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

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # Fix typo here
            comment.event = event
            comment.save()
            return redirect('events:get_event', event_id=event_id)  # Redirect to the same page after comment submission

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

    context = {'event': event, 'related_events': related_events, 'categories': categories, 'cities': cities,
               'comments': comments, 'timer': timer, 'form': form}

    return render(request, template, context)



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

    # Pass the list to the template
    context = {'events': all_events}
    return render(request, 'events/calendar.html', context)


"""""
@login_required


def user_events(request):
    template='events/user_events.html'
    user=get_object_or_404(User,username='username')
    events=get_object_or_404(Event,uploaded_by=user).order_by('-upload_date')

    if user ==events:
        return events.uploaded_by

    context={
        'user':user,
        'events':events
             }
    return render(request,template,context)





class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event.html'
    context_object_name = 'events'

    def get_views(self, request, event_id):
        event = Event.objects.get(id=event_id)
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        is_views = Analytics.objects.filter(eventId=event_id, sesID=session_key)
        if is_views.count() == 0 and str(session_key != "None"):
            views = Analytics()
            views.sesID = session_key
            views.eventId = event
            views.save()
            event.views += 1
            event.save()


def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        likes_connected = get_object_or_404(Event, id=self.kwargs['pk'])
        liked = False
        if likes_connected.likes.filter(id=self.request.user.id).exists():
            liked = True
        data['number_of_likes'] = likes_connected.number_of_likes()
        data['post_is_liked'] = liked
        return data



def like_event(request, pk):
    post= get_object_or_404(Event,id=request.POST.get('event_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('events', args=[str(pk)]))




def get_template_context():
    template='events/central.html'
    trending_events = Event.objects.filter(event_date__gt=timezone.now()).order_by('event_date')[:1]
    most_viewed=Event.objects.filter(status=True).order_by('-views')
    recently_posted_events = Event.objects.all().order_by('-event_date')[:1]
    upcoming_events=Event.objects.filter(status=True).order_by('-event_date')
    context={
        'trending_videos':trending_events,
        'most_viewed':most_viewed,
        'recently_posted':recently_posted_events,
        'upcoming_events':upcoming_events
    }
    return template,context


"""
