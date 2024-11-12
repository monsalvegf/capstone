from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Nonconformity

@login_required
def nonconformity_list(request):
    nonconformities = Nonconformity.objects.all()
    return render(request, 'nonconformities/nonconformity_list.html', {'nonconformities': nonconformities})
