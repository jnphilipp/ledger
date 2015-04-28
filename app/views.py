from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def llogin(request):
	gnext = request.GET.get('next')
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				messages.add_message(request, messages.SUCCESS, 'you have successfully logged in.')
				return redirect(gnext)
			else:
				messages.add_message(request, messages.ERROR, 'your account is disabled.')
			return redirect(request.META.get('HTTP_REFERER'))
		else:
			messages.add_message(request, messages.ERROR, 'please enter the correct username and password for an account. Note that both fields may be case-sensitive.')
			return redirect(request.META.get('HTTP_REFERER'))
	else:
		form = AuthenticationForm(request)
		return render(request, 'registration/login.html', locals())