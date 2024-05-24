from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


from nxtbn.payment.payment_manager import PaymentManager
from nxtbn.payment.utils import check_plugin_directory


class NonSensitivePaymentKey(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        if check_plugin_directory(payment_plugin_id):
            data =  PaymentManager(payment_plugin_id).public_keys()
            return Response(data)
        else:
            raise Http404(f"Payment gateway '{payment_plugin_id}' is not installed plugin.")
        

class WebhookAPIView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, payment_plugin_id):
        return self.dispatch_hook(request, payment_plugin_id)

    @method_decorator(csrf_exempt)
    def post(self, request, payment_plugin_id):
        return self.dispatch_hook(request, payment_plugin_id)

    def dispatch_hook(self, request, payment_plugin_id):
        return PaymentManager(payment_plugin_id).handle_webhook_event(request)