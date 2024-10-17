from apps.users.models import Token
from django.utils.translation import activate

class LanguageMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language_code = request.META.get("HTTP_LANGUAGE_CODE")
        try:
            key = request.META.get("HTTP_AUTHORIZATION").split(" ")
            key = key[-1]
            user = Token.objects.get(key=key).user
            language_code = user.language.item_code
        except:
            pass
        if language_code:
            activate(language_code)

        return self.get_response(request)
