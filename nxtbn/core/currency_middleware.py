from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class CurrencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the currency from the X-Currency header
        currency = request.headers.get('Accept-Currency', settings.BASE_CURRENCY) # BASE_CURRENCY is fallback
        
        if currency not in settings.ALLOWED_CURRENCIES:
            currency = settings.BASE_CURRENCY # Fallback to base currency if not allowed
        # Store the currency in the request object
        request.currency = currency
