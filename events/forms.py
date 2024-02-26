from django import forms
from.models import Event,EventReview,Comment
from bootstrap_datepicker_plus.widgets import DatePickerInput,TimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.utils import timezone



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Assuming your Comment model has a 'text' field for the actual comment text
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Add a comment...'}),
        }

class LikeForm(forms.Form):
    event_id = forms.IntegerField(widget=forms.HiddenInput())




class EventReviewForm(forms.ModelForm):
    class Meta:
        model=EventReview
        fields=['ratings', 'comment']
       



class EVentUploadForm(forms.ModelForm):
    class Meta:
        model=Event
        fields=['title', 'category','city','description','event_venue','entry_fee', 'event_date', 'event_time', 'thumb','tags' ]
        widgets={'event_date': DatePickerInput(),
                 'event_time':TimePickerInput(),
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



