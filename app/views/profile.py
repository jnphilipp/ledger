from app.forms import UserChangeForm
from app.models import Ledger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect

@login_required(login_url='/signin/')
@csrf_protect
def profile(request):
    print('profile')
    if request.method == 'POST':
        form = UserChangeForm(instance=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'your profile has been successfully updated.')
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'ledger/app/profile/form.html', locals())