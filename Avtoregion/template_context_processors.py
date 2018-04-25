from django.conf import settings


def settings_context_processor(request):
    return {
        'JS_MD5': settings.JS_MD5,
    }
