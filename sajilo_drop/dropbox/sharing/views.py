from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from .models import Message, JSONLDSchema, SharedFile
from .forms import JSONLDSchemaForm, SharedFileForm
import json
from .utils import get_client_ip
from datetime import timedelta
from django.utils import timezone
from . models import ActivityLog


def cleanup_expired_files():
    """Deletes files older than 24 hours or orphan records with missing files."""
    expiry_time = timezone.now() - timedelta(hours=24)
    expired_files = SharedFile.objects.filter(uploaded_at__lt=expiry_time)
    for shared_file in expired_files:
        if shared_file.file:
            try:
                shared_file.file.delete(save=False)
            except Exception:
                pass
        shared_file.delete()

    # Clean up orphan database records whose files do not exist in storage
    for sf in SharedFile.objects.all():
        try:
            if not sf.file or not sf.file.storage.exists(sf.file.name):
                sf.delete()
        except Exception:
            sf.delete()

    return expiry_time


def serialize_files(queryset, client_ip=None):
    """Helper to convert SharedFile objects into JSON-friendly dicts."""
    file_list = []
    for sf in queryset:
        try:
            if not sf.file or not sf.file.storage.exists(sf.file.name):
                continue
            url = sf.file.url
            size = sf.file.size
        except Exception:
            url = ""
            size = 0
        file_list.append({
            "id": sf.id,
            "name": sf.filename,
            "url": url,
            "size": size,
            "formatted_size": sf.formatted_size,
            "uploaded_at": sf.uploaded_at.isoformat(),
            "can_delete": True if client_ip is None else (sf.ip_address == client_ip),
        })
    return file_list


def index(request):
    ip_addr = get_client_ip(request.META)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    obj, created = Message.objects.get_or_create(ip=ip_addr)

    ActivityLog.objects.create(
        ip=ip_addr,
        user_agent=user_agent,
        action="ACCESS",
    )
    
    if created:
        obj.content = "Nothing to see here!"
        obj.save()

    expiry_time = cleanup_expired_files()

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
        "user_agent": user_agent,
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


@ratelimit(key='ip', rate='60/m', method='GET', block=False)
def get_files(request):
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )
    expiry_time = cleanup_expired_files()
    client_ip = get_client_ip(request.META)
    files = SharedFile.objects.filter(uploaded_at__gte=expiry_time).order_by("-uploaded_at")
    return JsonResponse({
        "status": "success",
        "files": serialize_files(files, client_ip)
    })


@ratelimit(key='ip', rate='30/m', method='POST', block=False)
def upload_file(request):
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.POST.get('ajax') == '1'
    )

    if request.method == "POST":
        form = SharedFileForm(request.POST, request.FILES)
        if form.is_valid():
            shared_file = form.save(commit=False)
            client_ip = get_client_ip(request.META)
            shared_file.ip_address = client_ip
            shared_file.save()

            if is_ajax:
                expiry_time = cleanup_expired_files()
                all_files = SharedFile.objects.filter(uploaded_at__gte=expiry_time).order_by("-uploaded_at")
                return JsonResponse({
                    "status": "success",
                    "message": f"'{shared_file.filename}' uploaded successfully!",
                    "uploaded_file": {
                        "id": shared_file.id,
                        "name": shared_file.filename,
                        "url": shared_file.file.url,
                        "size": shared_file.file.size,
                        "formatted_size": shared_file.formatted_size,
                    },
                    "files": serialize_files(all_files, client_ip)
                })
            return redirect("index")
        else:
            if is_ajax:
                errors = []
                for field, field_errors in form.errors.items():
                    for err in field_errors:
                        errors.append(str(err))
                error_msg = " ".join(errors) if errors else "Invalid file upload."
                return JsonResponse({"error": error_msg}, status=400)

    return redirect("index")


@ratelimit(key='ip', rate='30/m', method='POST', block=False)
def delete_file(request, file_id):
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please slow down."},
            status=429
        )

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.POST.get('ajax') == '1'
    )

    if request.method == "POST":
        shared_file = get_object_or_404(SharedFile, id=file_id)
        client_ip = get_client_ip(request.META)

        if shared_file.ip_address != client_ip:
            if is_ajax:
                return JsonResponse(
                    {"error": "You are not allowed to delete this file."},
                    status=403
                )
            return redirect("index")

        if shared_file.file:
            try:
                shared_file.file.delete(save=False)
            except Exception:
                pass
        shared_file.delete()

        if is_ajax:
            expiry_time = cleanup_expired_files()
            all_files = SharedFile.objects.filter(uploaded_at__gte=expiry_time).order_by("-uploaded_at")
            return JsonResponse({
                "status": "success",
                "message": "File deleted successfully.",
                "files": serialize_files(all_files, client_ip)
            })

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

    return render(request, "create.html", {"form": form})


def jsonld_success(request):
    return render(request, "success.html")