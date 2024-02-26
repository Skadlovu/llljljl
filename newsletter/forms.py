from django import forms
from events.models import Category, City  # Import the Category and City models from your actual app

class SubscriptionForm(forms.Form):
    email = forms.EmailField(label='Email')
    city = forms.ModelMultipleChoiceField(queryset=City.objects.all(), required=False, label='City')
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False, label='Categories')
