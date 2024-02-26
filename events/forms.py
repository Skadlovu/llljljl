from django import forms
from.models import Event,Comment,ReviewRating,ReviewComment
from bootstrap_datepicker_plus.widgets import DatePickerInput,TimePickerInput,DateTimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.utils import timezone


class ReviewRatingForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['rating']
        RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
        widgets={
            'rating':forms.ChoiceField(choices=RATING_CHOICES)
        }



class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Add a comment...'}),
        }




class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Add a comment...'}),
        }



class LikeForm(forms.Form):
    event_id = forms.IntegerField(widget=forms.HiddenInput())





class EVentUploadForm(forms.ModelForm):
    class Meta:
        model=Event
        fields=['title', 'category','city','description','event_venue','entry_fee', 'event_date', 'event_time', 'thumb','tags','end_time' ]
        widgets={'event_date': DatePickerInput(),
                 'event_time':TimePickerInput(),
                 'end_time':DateTimePickerInput(),
                 'description': forms.Textarea(attrs={'rows': 5, 'cols': 40}),}


        def __init__(self, *args, **kwargs):
            super(EVentUploadForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                'title',
                'city',
                'category',
                'description',
                'event_date',
                'event_time',
                'thumb',
                'event_venue',
            Submit('submit', 'Create Event')
            )


class EventSearchForm(forms.Form):
    title=forms.CharField(max_length=100, required=False, label='Search for events')

class CitySearchForm(forms.Form):
    city=forms.CharField(max_length=100, required=False, label='Search for the city')




