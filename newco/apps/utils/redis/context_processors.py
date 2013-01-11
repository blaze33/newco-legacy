from django.core.urlresolvers import reverse_lazy


def redis_url(request):
    return {
        "URL_REDIS": reverse_lazy("redis"),
        "URL_REDIS_TAG": reverse_lazy("redis", args=["tag"]),
        "URL_REDIS_PROFILE": reverse_lazy("redis", args=["profile"]),
    }
