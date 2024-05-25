from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Any, Dict
from dataclasses import dataclass

from django.conf import settings
from rest_framework import serializers
from nxtbn.core.models import SiteSettings
from nxtbn.payment.models import Payment
from babel.numbers import get_currency_precision


class BasePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


@dataclass
class PaymentResponse:
    """
    Unified structure for payment gateway responses.

    Attributes:
        success (bool): Whether the payment was successful or not.
        transaction_id (str, optional): A unique transaction identifier from the payment gateway.
        message (str, optional): Additional message related to the payment response.
        raw_data (Any, optional): The raw response exactly as received from the payment gateway.
        meta_data (Any, optional): Additional metadata associated with the payment response.
    """
    success: bool
    transaction_id: Optional[str] = None
    message: Optional[str] = None
    raw_data: Optional[Any] = None
    meta_data: Optional[Any] = None


class PaymentPlugin(ABC):
    """
    Abstract base class for payment gateways.

    Defines the basic interface for interacting with payment gateways.
    """

    def __init__(self, context: dict = None):
        self.base_currency = settings.BASE_CURRENCY
        self.context = context or {}

    @abstractmethod
    def authorize(self, amount: Decimal, order_id: str, **kwargs):
        """
        Authorize a payment of the specified amount.

        Args:
            amount (Decimal): The amount to be authorized.
            order_id (str): The unique identifier for the order.
            **kwargs: Additional keyword arguments specific to the payment gateway.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def capture(self, amount: Decimal, order_id: str, **kwargs):
        """
        Capture an authorized payment.

        Args:
            amount (Decimal): The amount to be captured.
            order_id (str): The unique identifier for the order.
            **kwargs: Additional keyword arguments specific to the payment gateway.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel(self, order_id: str, **kwargs):
        """
        Cancel an authorized payment.

        Args:
            order_id (str): The unique identifier for the order.
            **kwargs: Additional keyword arguments specific to the payment gateway.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def refund(self, amount: Decimal, order_id: str, **kwargs):
        """
        Refund a captured payment.

        Args:
            amount (Decimal): The amount to be refunded.
            order_id (str): The unique identifier for the order.
            **kwargs: Additional keyword arguments specific to the payment gateway.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError
    

    @abstractmethod
    def normalize_response(self, raw_response: Any) -> PaymentResponse:
        """
        Normalize raw response to a consistent PaymentResponse.

        Args:
            raw_response (Any): The raw response received from the payment gateway.

        Returns:
            PaymentResponse: A standardized PaymentResponse object.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def special_serializer(self):
        """Return a serializer for handling client-side payloads in API views.

        This method returns a serializer specifically designed to handle payloads received from the client side for payment. 
        It is intended to be used in API views to serialize and validate data related to gateway payments, 
        ensuring seamless communication between the client and the server. 
        """
        raise NotImplementedError
    
    @abstractmethod
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
        raise NotImplementedError
    

   
    def payment_url_with_meta(self, order_alias: str, **kwargs) -> Dict[str, Any]:
        """
        Get payment URL and additional metadata based on the order ID.

        Args:
            order_alias (str): The unique identifier for the order.

        Keyword Args:
            **kwargs: Additional keyword arguments specific to the payment gateway.


        Returns:
            dict: A dictionary containing payment URL and other necessary metadata.

        Example:
            {
                'url': 'https://example.com/payment',  # URL for initiating the payment process
                'key1': 'value1',  # Additional metadata keys and values as required by the payment gateway
                'key2': 'value2',
                ...
            }
        """
        raise NotImplementedError
    
    
    def handle_webhook_event(self, request_data: Dict[str, Any]) -> PaymentResponse:
        """
        Handle a webhook event received from the payment gateway.

        Args:
            request_data (dict): Data received from the webhook event.

        Returns:
            PaymentResponse: Response indicating the result of handling the event.
        """
        raise NotImplementedError
    

    def create_payment_instance(self, payment_payload: Dict[str, Any], **kwargs):
        serializer = BasePaymentSerializer(data=payment_payload)
        if serializer.is_valid():
            serializer.save()
        return serializer.data
    
    def get_currency_code(self, **kwargs) -> str:
        """
        Get the currency code from the request.

        Args:
            request: The request object.
            **kwargs: Additional keyword arguments specific to the implementation.

        Returns:
            str: The currency code extracted from the request.
        """
        if self.context['request'].data.get('currency_code'):
            return self.context['request'].data.get('currency_code')
        else:
            return self.context['request'].currency
    
    def total_amount_in_subunit(self, **kwargs) -> int:
        """
            Adjust the decimal total amount by multiplying it by 100 and return as an integer.

            Args:
                amount (Decimal): The amount to be adjusted.

            Returns:
                int: The adjusted amount as an integer.
        """
        return self.to_subunit(self.context['request'].data.get('total_price'))
    
    def to_subunit(self, amount, **kwargs) -> int:
        """
            Convert a monetary amount from units to subunits based on the currency's precision.
            
            Args:
                amount (Decimal): The amount in units.
                currency (str): The currency code to determine the precision.
            
            Returns:
                int: The amount in subunits as an integer.
        """
        precision = get_currency_precision(self.get_currency_code())
        subunit_amount = int(amount * (10 ** precision))
        return subunit_amount
    
    def to_unit(self, amount, **kwargs) -> Decimal:
        """
            Adjust the decimal amount by multiplying it by 100 and return as an integer.
            Args:
                amount (Decimal): The amount to be adjusted.
            Returns:
                int: The adjusted amount as an integer.
        """
        precision = get_currency_precision(self.get_currency_code())
        unit_amount = Decimal(amount) / (10 ** precision)
        return unit_amount