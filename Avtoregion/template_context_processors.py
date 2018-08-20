from django.conf import settings


def settings_context_processor(request):
    return {
        'JS_MAIN': settings.JS_MAIN,
        'JS_CHOSEN': settings.JS_CHOSEN,
        'JS_DATERANGE': settings.JS_DATERANGE,
        'JS_BOOTSTRAP': settings.JS_BOOTSTRAP,
        'JS_MODAL': settings.JS_MODAL,
    }
