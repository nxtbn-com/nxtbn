from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class CurrencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the currency from the X-Currency header
        currency = request.headers.get('Accept-Currency', settings.BASE_CURRENCY)
        
        # Store the currency in the request object
        request.currency = currency
