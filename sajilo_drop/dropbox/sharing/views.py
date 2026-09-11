from django.shortcuts import render
from .forms import PublicMessageForm
from .models import PublicMessage

# Create your views here.
def index(req):
    # form = PublicMessageForm()
    # message = req.POST['content']
    ip_addr = req.META['REMOTE_ADDR']
    obj,created = PublicMessage.objects.get_or_create(ip = ip_addr)
    if created:
        obj.content = "Nothing to see here!"

    # obj.content = message
    # obj.save()
    return render(req, 'index.html',{'obj': obj})

from django.http import JsonResponse
def upload(req):
    message = req.POST['content']
    ip_addr = req.META['REMOTE_ADDR']
    obj,created = PublicMessage.objects.get_or_create(ip = ip_addr)
    if created:
        obj.content = "Nothing to see here!"

    obj.content = message
    obj.save()
    return JsonResponse(
        {
            "status": 226,
            "content" : obj.content
        }
    )

from django.http import HttpResponse
def content(req):
    ip_addr = req.META['REMOTE_ADDR']
    obj,created = PublicMessage.objects.get_or_create(ip = ip_addr)


    return JsonResponse(
        {
            "status": 226,
            "content" : obj.content
        }
    )