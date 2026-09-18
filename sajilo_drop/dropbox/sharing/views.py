from django.shortcuts import render
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from .models import Message

def get_client_ip(req):
    x_forwarded_for = req.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return req.META.get('REMOTE_ADDR', '127.0.0.1')

@ratelimit(key='ip', rate='60/m', block=False)
def index(req):
    ip_addr = get_client_ip(req)
    obj, created = Message.objects.get_or_create(ip=ip_addr)
    if created:
        obj.content = "Nothing to see here!"
    return render(req, 'index.html', {'obj': obj})

@ratelimit(key='ip', rate='30/m', method='POST', block=False)
def upload(req):
    if getattr(req, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )

    message = req.POST.get('content', '')
    ip_addr = get_client_ip(req)
    obj, created = Message.objects.get_or_create(ip=ip_addr)
    if created:
        obj.content = "Nothing to see here!"

    obj.content = message
    obj.save()
    return JsonResponse(
        {
            "status": 226,
            "content": obj.content
        }
    )

@ratelimit(key='ip', rate='120/m', method='GET', block=False)
def content(req):
    if getattr(req, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )

    ip_addr = get_client_ip(req)
    obj, created = Message.objects.get_or_create(ip=ip_addr)
    return JsonResponse(
        {
            "status": 226,
            "content": obj.content
        }
    )