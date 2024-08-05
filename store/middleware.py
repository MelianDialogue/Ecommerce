# middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import activate

class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.session.get('django_language', 'en')
        activate(language)