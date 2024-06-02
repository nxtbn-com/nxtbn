from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


from nxtbn.order.models import Order
from nxtbn.payment.api.storefront.serializers import PaymentUrlSerializer
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
    


class StartPaymentProcess(generics.CreateAPIView):
    serializer_class = PaymentUrlSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_alias = serializer.validated_data['order_alias']
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        
        order = get_object_or_404(Order, alias=order_alias)
        payment_manager = PaymentManager(
            payment_plugin_id=payment_plugin_id,
            context={'request': request},
            order=order
        )
        payment_url_meta = payment_manager.payment_url_with_meta(order_alias)
        
        return Response(payment_url_meta)
    
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request.

        This method validates whether the provided payment gateway ID matches any defined payment gateway
        in the settings. If not, it raises a 404 error.
        """
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        if payment_plugin_id:
            if not  check_plugin_directory(payment_plugin_id):
                raise Http404(f"Payment gateway '{payment_plugin_id}' is not installed plugin.")
        return super().dispatch(request, *args, **kwargs)