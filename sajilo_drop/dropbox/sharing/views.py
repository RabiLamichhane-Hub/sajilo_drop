from django.shortcuts import render
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from .models import Message

from .utils import get_client_ip

@ratelimit(key='ip', rate='60/m')
def index(req):
    ip_addr = get_client_ip(req.META)
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
    ip_addr = get_client_ip(req.META)
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

    ip_addr = get_client_ip(req.META)
    obj, created = Message.objects.get_or_create(ip=ip_addr)
    return JsonResponse(
        {
            "status": 226,
            "content": obj.content
        }
    )


from django.core.cache import cache
from django.http import JsonResponse

def redis_test(request):
    cache.set("django_test", "Hello Redis", timeout=60)

    value = cache.get("django_test")

    return JsonResponse({
        "value": value
    })