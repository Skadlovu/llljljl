from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . forms import UserRegistrationForm, UserUpdateForm, UserProfileUpdateForm, ChangePasswordForm
from django.contrib.auth.models import User
from .models import Profile
from events.models import Event
from django.contrib.auth.views import LoginView
from events import views
from django.urls import reverse_lazy,reverse
from django.http import HttpResponseRedirect,JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme



def register(request):
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('login')
	else: 
		form=UserRegistrationForm()
	return render(request, 'profiles/register.html', {'form': form})


@login_required
def profile(request):
	Profile.objects.get_or_create(user=request.user)
	if request.method == 'POST':
		userform=UserUpdateForm(request.POST, instance=request.user)
		profileform= UserProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if userform.is_valid() and profileform.is_valid():
			userform.save()
			profileform.save()
			return redirect('profile')
	else: 
		userform=UserUpdateForm(instance=request.user)
		profileform=UserProfileUpdateForm(instance=request.user.profile)
		


	user_events =Event.objects.filter(uploaded_by=request.user)
	


	context ={
		'userform':userform,
		'profileform': profileform,
		'user_events':user_events
	}
	

	return render(request, 'profiles/profile.html', context)






"""
class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        next_url = self.request.GET.get('next')
        home_url = reverse('home')  # Assuming 'home' is the name of your URL pattern

        # Check if the 'next' URL is safe; if not, redirect to the home page
        if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={self.request.get_host()}):
            return HttpResponseRedirect(next_url)
        else:
            return redirect(home_url)


class CustomLoginView(LoginView):
    success_url = reverse_lazy('home')
    template_name = 'profiles/login.html'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            next_url = self.request.GET.get('next')
            return self.get_success_url(next_url)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error in form_valid: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

    def get_success_url(self, next_url=None):
        try:
            if next_url and next_url != reverse_lazy('login'):
                return next_url
            return super().get_success_url()
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error in get_success_url: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
"""
