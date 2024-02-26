from django.shortcuts import render, redirect
from .forms import SubscriptionForm
from .models import Subscription, Newsletter
from django.conf import settings
from django.core.mail import send_mail

def send_newsletter(request, newsletter_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    subscribers = Subscription.objects.all()  # You might want to filter subscribers based on preferences

    for subscriber in subscribers:
        subject = f'Newsletter: {newsletter.title}'
        message = f'Hi {subscriber.email},\n\n{newsletter.content}'
        recipient_list = [subscriber.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    return redirect('newsletter_list')  # Redirect to a page after sending newsletters

def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            city = form.cleaned_data['city']
            categories = form.cleaned_data['categories']

            # Handle the subscription logic
            # For simplicity, let's assume you have a Subscription model
            subscription = Subscription.objects.create(email=email, city=city)
            subscription.categories.set(categories)

            return redirect('subscribe_success')  # Redirect to a success page
    else:
        form = SubscriptionForm()

    return render(request, 'newsletter/subscribe.html', {'form': form})

def subscribe_success(request):
    return render(request, 'newsletter/subscribe_success.html')

def newsletter_list(request):
    newsletters = Newsletter.objects.all()
    return render(request, 'newsletter/newsletter_list.html', {'newsletters': newsletters})
