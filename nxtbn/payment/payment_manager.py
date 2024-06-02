import os
from decimal import Decimal
from typing import Optional
from django.conf import settings
from django.core.exceptions import ValidationError
from importlib import import_module


import logging

from nxtbn.order.models import Order
from nxtbn.payment.utils import check_plugin_directory, get_plugin_path, security_validation

logger = logging.getLogger(__name__)



class PaymentManager:
    """Centralized handler for payment operations with multiple gateways"""

    def __init__(self, payment_plugin_id: str, context: dict = {}, order: Optional[Order] = None):
        self.payment_plugin_id = payment_plugin_id
        self.context = context
        self.order = order
        self.gateway = self.select_gateway(payment_plugin_id, context, order)
    

    def select_gateway(self, payment_plugin_id: str, context: dict = {}, order: Optional[Order] = None):
        """Select the appropriate gateway based on the payment method."""

        security_validation(payment_plugin_id)
        
        if not  check_plugin_directory(payment_plugin_id):
            raise ValidationError("No getway class found")
        
        gateway_path = get_plugin_path(payment_plugin_id=payment_plugin_id, context=context, order=order)                        

        module_name, class_name = gateway_path.rsplit(".", 1)
        module = import_module(module_name)
        gateway_class = getattr(module, class_name)

        return gateway_class(context=self.context)

    def authorize_payment(self, amount: Decimal, order_id: str, **kwargs):
        """Authorize payment."""
        return self.gateway.authorize(amount, order_id, **kwargs)

    def capture_payment(self, amount: Decimal, order_id: str, **kwargs):
        """Capture payment."""
        return self.gateway.capture(amount, order_id, **kwargs)

    def cancel_payment(self, order_id: str, **kwargs):
        """Cancel authorization."""
        return self.gateway.cancel(order_id, **kwargs)

    def refund_payment(self, payment_id: str, amount: str, **kwargs):
        """Refund payment."""
        return self.gateway.refund(payment_id, amount, **kwargs)
    
    def special_serializer(self):
        """Return a serializer for handling client-side payloads in API views.

        This method returns a serializer specifically designed to handle payloads received from the client side. 
        It is intended to be used in API views to serialize and validate data related to gateway payments, 
        ensuring seamless communication between the client and the server. 
        """
        return self.gateway.special_serializer()

    def public_keys(self):
        """
            Retrieve public keys and non-sensitive information required for secure communication and client-side operations.

            Returns:
                dict: A dictionary containing public keys and non-sensitive data necessary for client-side operations.
                
                Example:
                    {
                        'store_id': 'your_store_id',
                        'public_key': 'your_public_key',
                        'location': 'payment_gateway_location',
                        'currency_code': 'USD',
                        # Add more relevant key-value pairs as needed...
                    }

            This method is intended to provide essential information such as store identifiers, public keys, gateway locations, 
            currency codes, and any other non-sensitive data required for secure communication between the client and the payment gateway. 
            Sensitive information such as secret keys and access key should never be included in the returned dictionary to ensure security.
        """
        return self.gateway.public_keys()
    
    def payment_url_with_meta(self, order_alias, **kwargs):
        """
        Get payment URL and additional metadata based on the order alias.

        Args:
            order_alias (str): The unique identifier for the order.

        Keyword Args:
            **kwargs: Additional keyword arguments specific to the payment gateway.

        Returns:
            dict: A dictionary containing the payment URL and other necessary metadata.

        Example:
            {
                'url': 'https://example.com/payment',  # URL for initiating the payment process
                'key1': 'value1',  # Additional metadata keys and values as required by the payment gateway
                'key2': 'value2',
                ...
            }
        """
        return self.gateway.payment_url_with_meta(order_alias, **kwargs)
    

    def handle_webhook_event(self, request_data, **kwargs):
        """
        Handle a webhook event received from the payment gateway.

        Args:
            request_data (dict): Data received from the webhook event.
            **kwargs: Additional keyword arguments specific to the payment gateway.

        Returns:
            dict: Response indicating the result of handling the event.

        Example:
            {
                'status': 'success',
                'transaction_id': '123456',
                'message': 'Webhook handled successfully',
                ...
            }
        """
        return self.gateway.handle_webhook_event(request_data, self.payment_plugin_id, **kwargs)
    
    def create_payment_instance(self, payload, **kwargs):
        return self.gateway.create_payment_instance(payload, **kwargs)
    

    def currency_code(self, context, **kwargs) -> str:
        """
        Get the currency code from the request.

        Args:
            request: The request object.
            **kwargs: Additional keyword arguments specific to the implementation.

        Returns:
            str: The currency code extracted from the request.
        """

        return self.gateway.get_currency_code()
    
    def total_amount_in_subunit(self, context, **kwargs) -> int:
        """
            Adjust the decimal amount by multiplying it by 100 and return as an integer.

            Returns:
                int: The adjusted amount as an integer.
        """
        return self.gateway.total_amount_in_subunit()
        