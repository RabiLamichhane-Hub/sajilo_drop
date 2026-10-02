from django.shortcuts import render, redirect
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from .models import Message, JSONLDSchema, SharedFile
from . forms import JSONLDSchemaForm, SharedFileForm
import json
from .utils import get_client_ip
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404


from datetime import timedelta
from django.utils import timezone


def index(request):
    ip_addr = get_client_ip(request.META)

    obj, created = Message.objects.get_or_create(ip=ip_addr)

    if created:
        obj.content = "Nothing to see here!"
        obj.save()

    # Delete files older than 24 hours
    expiry_time = timezone.now() - timedelta(hours=24)

    expired_files = SharedFile.objects.filter(
        uploaded_at__lt=expiry_time
    )

    for shared_file in expired_files:
        shared_file.file.delete(save=False)
        shared_file.delete()

    file_form = SharedFileForm()

    schemas = JSONLDSchema.objects.all()

    shared_files = SharedFile.objects.filter(
        uploaded_at__gte=expiry_time
    ).order_by("-uploaded_at")

    faqs = []

    for schema in schemas:
        if schema.schema.get("@type") == "FAQPage":
            faqs = schema.schema.get("mainEntity", [])
            break

    return render(request, "index.html", {
        "obj": obj,
        "schemas": schemas,
        "file_form": file_form,
        "shared_files": shared_files,
        "faqs": faqs,
    })



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

@ratelimit(key='ip', rate='20/m', method='POST', block=False)
def upload_file(request):
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )
    if request.method == "POST":
        form = SharedFileForm(request.POST, request.FILES)
        if form.is_valid():
            shared_file = form.save(commit=False)
            shared_file.ip_address = get_client_ip(request.META)
            shared_file.save()
            return redirect("index")
    return redirect("index")

@ratelimit(key='ip', rate='20/m', method='POST', block=False)
def delete_file(request, file_id):
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )

    if request.method == "POST":
        shared_file = get_object_or_404(SharedFile, id=file_id)

        # Optional: only allow the IP that uploaded the file to delete it
        if shared_file.ip_address != get_client_ip(request.META):
            return JsonResponse(
                {"error": "You are not allowed to delete this file."},
                status=403
            )

        shared_file.delete()

    return redirect("index")

def create_jsonld(request):

    if request.method == "POST":
        form = JSONLDSchemaForm(request.POST)

        if form.is_valid():

            schema_data = request.POST.get("schema")

            try:
                schema_data = json.loads(schema_data)
            except (json.JSONDecodeError, TypeError):
                form.add_error(None, "Invalid JSON data.")
            else:
                jsonld = form.save(commit=False)
                jsonld.schema = schema_data
                jsonld.save()

                return redirect("jsonld_success")

    else:
        form = JSONLDSchemaForm()

    return render(request, "create.html", {
        "form": form
    })


def jsonld_success(request):
    return render(request, "success.html")

 