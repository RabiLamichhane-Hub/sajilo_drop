from django.shortcuts import render
from .models import Message

# Create your views here.
def index(req):
    # form = PublicMessageForm()
    # message = req.POST['content']
    ip_addr = req.META['REMOTE_ADDR']
    obj,created = Message.objects.get_or_create(ip = ip_addr)
    if created:
        obj.content = "Nothing to see here!"

    # obj.content = message
    # obj.save()
    return render(req, 'index.html',{'obj': obj})

from django.http import JsonResponse
def upload(req):
    message = req.POST['content']
    ip_addr = req.META['REMOTE_ADDR']
    obj,created = Message.objects.get_or_create(ip = ip_addr)
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

def content(req):
    ip_addr = req.META['REMOTE_ADDR']
    obj,created = Message.objects.get_or_create(ip = ip_addr)


    return JsonResponse(
        {
            "status": 226,
            "content" : obj.content
        }
    )