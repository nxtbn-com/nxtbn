from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from nxtbn.core import PublishableStatus
from nxtbn.product.tests import ProductFactory, CategoryFactory, ProductTypeFactory, ProductVariantFactory
from nxtbn.tax.tests import TaxClassFactory, TaxRateFactory
from nxtbn.discount.tests import PromoCodeFactory, PromoCodeCustomerFactory, PromoCodeProductFactory
from nxtbn.home.base_tests import BaseTestCase
from nxtbn.core.utils import normalize_amount_currencywise
from nxtbn.users.tests import UserFactory
from faker import Faker
from datetime import timedelta
fake = Faker()
from django.test.utils import override_settings


@override_settings(RESERVE_STOCK_ON_ORDER=False)
class OrderCreateMultiplePromoCodesTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.adminLogin()

        # Common setup
        self.country = 'US'
        self.state = 'NY'

        # Tax classes
        self.tax_class_15 = TaxClassFactory()
        self.tax_class_5 = TaxClassFactory()

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def _create_order_with_promo(self, promo_code, currency, params):
        """
        Helper method to create orders with a specific promo code.
        """
        # Set up tax rates
        TaxRateFactory(tax_class=self.tax_class_15, is_active=True, rate=15, country=self.country, state=self.state)
        TaxRateFactory(tax_class=self.tax_class_5, is_active=True, rate=5, country=self.country, state=self.state)

        # Create products
        product_1 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type non-trackable, taxable 15% - {promo_code}",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_15,
            status=PublishableStatus.PUBLISHED,
            category=CategoryFactory(
                name="cate1",
                description = "cate 1 description"
            )
        )
        product_2 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type non-trackable, non-taxable - {promo_code}",
                track_stock=False,
                taxable=False,
            ),
            tax_class=None,
            status=PublishableStatus.PUBLISHED,
            category=CategoryFactory(
                name="cate2",
                description = "cate 2 description"
            )
        )
        product_3 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type non-trackable, taxable 5% - {promo_code}",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_5,
            status=PublishableStatus.PUBLISHED,
            category=CategoryFactory(
                name="cate3",
                description = "cate 3 description"
            )
        )
        product_4 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type 000 1 - {promo_code}",
                track_stock=True,
                taxable=False,
            ),
            tax_class=None,
            status=PublishableStatus.PUBLISHED,
            category=CategoryFactory(
                name="cate4",
                description = "cate 4 description"
            )
        )
        product_5 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type 2 - {promo_code}",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_5,
            status=PublishableStatus.PUBLISHED,
            category=CategoryFactory(
                name="cate5",
                description = "cate 5 description"
            )
        )
        product_6 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type 4 - {promo_code}",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_15,
            status=PublishableStatus.PUBLISHED,
            category=CategoryFactory(
                name="cate6",
                description = "cate 6 description"
            )

        )

        variant_payload = {}

        if params.get("applicable_variant") and params.get("applicable_product"):
            applicable_product = params.get("applicable_product")
            applicable_variant = ProductVariantFactory(
                product=applicable_product, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['applicable_variant']['price'], currency),
                cost_per_unit=params['applicable_variant']['cost_per_unit']
            )
            variant_payload = {
                "variants": [
                    {"alias": applicable_variant.alias, "quantity": 2}
                ]
            }
        else:
            variant_1 = ProductVariantFactory(
                product=product_1, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['variant_1']['price'], currency),
                cost_per_unit=params['variant_1']['cost_per_unit']
            )
            variant_2 = ProductVariantFactory(
                product=product_2, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['variant_2']['price'], currency),
                cost_per_unit=params['variant_2']['cost_per_unit']
            )
            variant_3 = ProductVariantFactory(
                product=product_3, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['variant_3']['price'], currency),
                cost_per_unit=params['variant_3']['cost_per_unit']
            )
            variant_4 = ProductVariantFactory(
                product=product_4, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['variant_4']['price'], currency),
                cost_per_unit=params['variant_4']['cost_per_unit']
            )
            variant_5 = ProductVariantFactory(
                product=product_5, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['variant_5']['price'], currency),
                cost_per_unit=params['variant_5']['cost_per_unit']
            )
            variant_6 = ProductVariantFactory(
                product=product_6, 
                track_inventory=False,
                currency=currency,
                price=normalize_amount_currencywise(params['variant_6']['price'], currency),
                cost_per_unit=params['variant_6']['cost_per_unit']
            )
            variant_payload = {
                "variants": [
                    {"alias": variant_1.alias, "quantity": 2},
                    {"alias": variant_2.alias, "quantity": 3},
                    {"alias": variant_3.alias, "quantity": 4},
                    {"alias": variant_4.alias, "quantity": 5},
                    {"alias": variant_5.alias, "quantity": 6},
                    {"alias": variant_6.alias, "quantity": 7}
                ]
            }


        promocode_payload = {}

        if type(promo_code) == dict:
            promocode_payload = {
                'custom_discount_amount': promo_code
            }
        else:
            promocode_payload = {
                'promocode': promo_code
            }

        customer_payload = {}

        if params.get("customer_id"):
            customer_payload = {
                "customer_id": params.get("customer_id")
            }
        else:
            customer_payload = {}


        order_payload = {
            "shipping_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "billing_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            **customer_payload,
            **promocode_payload,  # Applying promo code
            **variant_payload
        }


        # Estimate Test
        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY})
        print(order_estimate_response.json(), "[[[[[[[[]]]]]]]]")
        self.assertEqual(order_estimate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_estimate_response.data['subtotal'], params['subtotal'])
        self.assertEqual(order_estimate_response.data['total'], params['total'])
        self.assertEqual(order_estimate_response.data['estimated_tax'], params['tax'])

        # Order Create Test
        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY})
        print(order_response.json(), "999999")
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['subtotal'], params['subtotal'])
        self.assertEqual(order_response.data['total'], params['total'])
        self.assertEqual(order_response.data['estimated_tax'], params['tax'])




    def test_order_create_with_promo_20all(self):
        """
        Test Order creation with various promo codes and products having 6 properties.
        We will test 6 different promo codes for the order with 6 different products.
        """

        # Promo Codes
        promo_20all = PromoCodeFactory(
            code="20ALL", 
            code_type="PERCENTAGE", 
            value=20,    # 20% discount
            is_active=True,
            min_purchase_amount=0,
            min_purchase_period=None,
            redemption_limit=None,
            new_customers_only=False
        ) 

        if settings.BASE_CURRENCY == 'USD':
            self._create_order_with_promo(
                promo_code= promo_20all.code,
                currency="USD",
                params={
                    "subtotal": "$78.00",
                    "total": "$65.62",
                    "tax": "$3.22",
                    "variant_1": {"price": 2.00, "cost_per_unit": 2.00}, #*2
                    "variant_2": {"price": 3.00, "cost_per_unit": 4.00}, #*3
                    "variant_3": {"price": 2.50, "cost_per_unit": 3.00}, #*4
                    "variant_4": {"price": 3.50, "cost_per_unit": 2.00}, #*5
                    "variant_5": {"price": 4.50, "cost_per_unit": 1.00}, #*6
                    "variant_6": {"price": 1.50, "cost_per_unit": 1.00} #*7
                }
            )

        if settings.BASE_CURRENCY == 'JPY':
            self._create_order_with_promo(
                promo_code= promo_20all.code,
                currency="JPY",
                params={
                    "subtotal": "¥131,600",
                    "total": "¥111,942",  
                    "tax": "¥6,662",
                    "variant_1": {"price": 5000, "cost_per_unit": 4000},
                    "variant_2": {"price": 3000, "cost_per_unit": 2500}, 
                    "variant_3": {"price": 4550, "cost_per_unit": 3500}, 
                    "variant_4": {"price": 6550, "cost_per_unit": 3500}, 
                    "variant_5": {"price": 5550, "cost_per_unit": 3500}, 
                    "variant_6": {"price": 4050, "cost_per_unit": 3500}, 
                }
            )

        if settings.BASE_CURRENCY == 'KWD':
            self._create_order_with_promo(
                promo_code= promo_20all.code,
                currency="KWD",
                params={
                    "subtotal": "KWD78.000",
                    "total": "KWD65.620",  
                    "tax": "KWD3.220",
                    "variant_1": {"price": 2.00, "cost_per_unit": 2.00}, 
                    "variant_2": {"price": 3.00, "cost_per_unit": 4.00},
                    "variant_3": {"price": 2.50, "cost_per_unit": 3.00},
                    "variant_4": {"price": 3.50, "cost_per_unit": 2.00}, 
                    "variant_5": {"price": 4.50, "cost_per_unit": 1.00}, 
                    "variant_6": {"price": 1.50, "cost_per_unit": 1.00}, 
                }
            )

    def test_order_create_with_promo_flat200(self):
      
        if settings.BASE_CURRENCY == 'USD':

            promo_flat200 = PromoCodeFactory(
                code="FLAT200", 
                code_type="FIXED", 
                value=200,   
                is_active=True,
                min_purchase_amount=None,
                min_purchase_period=None,
                redemption_limit=None,
                new_customers_only=False
            )
            
            self._create_order_with_promo(
                promo_code=promo_flat200.code,
                currency="USD",
                params={
                    "subtotal": "$348.00",
                    "total": "$157.58",
                    "tax": "$9.58",
                    "variant_1": {"price": 12.00, "cost_per_unit": 2.00}, 
                    "variant_2": {"price": 13.00, "cost_per_unit": 4.00},
                    "variant_3": {"price": 12.50, "cost_per_unit": 3.00},
                    "variant_4": {"price": 13.50, "cost_per_unit": 2.00}, 
                    "variant_5": {"price": 14.50, "cost_per_unit": 1.00}, 
                    "variant_6": {"price": 11.50, "cost_per_unit": 1.00}
                }
            )

        if settings.BASE_CURRENCY == 'JPY':
            promo_flat200 = PromoCodeFactory(
                code="FLAT200", 
                code_type="FIXED", 
                value=300,   
                is_active=True,
                min_purchase_amount=None,
                min_purchase_period=None,
                redemption_limit=None,
                new_customers_only=False
            )
            
            self._create_order_with_promo(
                promo_code=promo_flat200.code,
                currency="JPY",
                params={
                    "subtotal": "¥131,600",
                    "total": "¥139,609",  
                    "tax": "¥8,309",
                    "variant_1": {"price": 5000, "cost_per_unit": 4000},
                    "variant_2": {"price": 3000, "cost_per_unit": 2500}, 
                    "variant_3": {"price": 4550, "cost_per_unit": 3500}, 
                    "variant_4": {"price": 6550, "cost_per_unit": 3500}, 
                    "variant_5": {"price": 5550, "cost_per_unit": 3500}, 
                    "variant_6": {"price": 4050, "cost_per_unit": 3500}, 
                }
            )

        if settings.BASE_CURRENCY == 'KWD':
            promo_flat200 = PromoCodeFactory(
                code="FLAT200", 
                code_type="FIXED", 
                value=200,   
                is_active=True,
                min_purchase_amount=None,
                min_purchase_period=None,
                redemption_limit=None,
                new_customers_only=False
            )
            
            self._create_order_with_promo(
                promo_code= promo_flat200.code,
                currency="KWD",
                params={
                    "subtotal": "KWD348.000",
                    "total": "KWD157.580",  
                    "tax": "KWD9.580",
                    "variant_1": {"price": 12.00, "cost_per_unit": 2.00}, 
                    "variant_2": {"price": 13.00, "cost_per_unit": 4.00},
                    "variant_3": {"price": 12.50, "cost_per_unit": 3.00},
                    "variant_4": {"price": 13.50, "cost_per_unit": 2.00}, 
                    "variant_5": {"price": 14.50, "cost_per_unit": 1.00}, 
                    "variant_6": {"price": 11.50, "cost_per_unit": 1.00}, 
                }
            )


    def test_order_create_with_promo_gold5(self):
        user = UserFactory(
            username = f"test_user_3"
        )
        promo_gold5 = PromoCodeFactory(
            code="GOLDCUSTOMER5", 
            code_type="PERCENTAGE", 
            value=5, # 5% for Gold customers
            is_active=True, 
            min_purchase_amount=None, 
            min_purchase_period=None, 
            new_customers_only=False
        )  
        apply_customer = PromoCodeCustomerFactory(
            promo_code = promo_gold5,
            customer = user
        )

        if apply_customer and promo_gold5:
            if settings.BASE_CURRENCY == 'USD':
                self._create_order_with_promo(
                    promo_code= promo_gold5.code,
                    currency="USD",
                    params={
                        "subtotal": "$78.00",
                        "total": "$77.92",
                        "tax": "$3.82",
                        "customer_id": user.id,
                        "variant_1": {"price": 2.00, "cost_per_unit": 2.00}, 
                        "variant_2": {"price": 3.00, "cost_per_unit": 4.00},
                        "variant_3": {"price": 2.50, "cost_per_unit": 3.00},
                        "variant_4": {"price": 3.50, "cost_per_unit": 2.00}, 
                        "variant_5": {"price": 4.50, "cost_per_unit": 1.00}, 
                        "variant_6": {"price": 1.50, "cost_per_unit": 1.00}
                    }
                )

            if settings.BASE_CURRENCY == 'JPY':
                self._create_order_with_promo(
                    promo_code= promo_gold5.code,
                    currency="JPY",
                    params={
                        "subtotal": "¥131,600",
                        "total": "¥132,931",  
                        "tax": "¥7,911",
                        "customer_id": user.id,
                        "variant_1": {"price": 5000, "cost_per_unit": 4000},
                        "variant_2": {"price": 3000, "cost_per_unit": 2500}, 
                        "variant_3": {"price": 4550, "cost_per_unit": 3500}, 
                        "variant_4": {"price": 6550, "cost_per_unit": 3500}, 
                        "variant_5": {"price": 5550, "cost_per_unit": 3500}, 
                        "variant_6": {"price": 4050, "cost_per_unit": 3500}, 
                    }
                )

            if settings.BASE_CURRENCY == 'KWD':
                self._create_order_with_promo(
                    promo_code= promo_gold5.code,
                    currency="KWD",
                    params={
                        "subtotal": "KWD78.000",
                        "total": "KWD77.924",  
                        "tax": "KWD3.824",
                        "customer_id": user.id,
                        "variant_1": {"price": 2.00, "cost_per_unit": 2.00}, 
                        "variant_2": {"price": 3.00, "cost_per_unit": 4.00},
                        "variant_3": {"price": 2.50, "cost_per_unit": 3.00},
                        "variant_4": {"price": 3.50, "cost_per_unit": 2.00}, 
                        "variant_5": {"price": 4.50, "cost_per_unit": 1.00}, 
                        "variant_6": {"price": 1.50, "cost_per_unit": 1.00}, 
                    }
                )


    def test_order_create_with_promo_sell5(self):
        user = UserFactory(
            username="test_user_4"
        )
        product = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"Product Type non-trackable, taxable 15%",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_15,
            status=PublishableStatus.PUBLISHED,
        )
        variant = ProductVariantFactory(
                product=product, 
                track_inventory=False,
                currency= settings.BASE_CURRENCY,
                price=normalize_amount_currencywise(10000, settings.BASE_CURRENCY),
                cost_per_unit=3
            )

        order_payload = {
            "shipping_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "billing_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "customer_id": user.id,
            "variants" : [
                {"alias": variant.alias, "quantity": 2},
            ]
        }

        order_placed = self.auth_client.post(self.order_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY})
        alias = order_placed.json()['order_alias']
        order_status = reverse('order-update', kwargs={'alias': alias})
        order_payload["status"] = "SHIPPED"
        shipped = self.auth_client.put(order_status, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY})
 
        if shipped:
            promo_sell5 = PromoCodeFactory(
                code="SELL5", 
                code_type="PERCENTAGE", 
                value=5,  
                is_active=True,
                min_purchase_amount=4,
                min_purchase_period=timedelta(days=10), 
                redemption_limit=None,
                new_customers_only=False
            )

            ProductFactory(
                product_type=ProductTypeFactory(
                    name = f"{settings.BASE_CURRENCY} product type",
                    track_stock = True,
                    taxable = True
                ),
                status = PublishableStatus.PUBLISHED,
                category=CategoryFactory(
                    name="cat-min-purchase",
                    description = "cate-min-purchase description"
                )
            )

            apply_customer = PromoCodeCustomerFactory(
                promo_code = promo_sell5,
                customer = user
            )

            if apply_customer:

                if settings.BASE_CURRENCY == 'USD':
                    self._create_order_with_promo(
                        promo_code= promo_sell5.code,
                        currency="USD",
                        params={
                            "subtotal": "$1,316.00",
                            "total": "$1,329.31",
                            "tax": "$79.11",
                            "customer_id": user.id,
                            "variant_1": {"price": 50.00, "cost_per_unit": 40.00},
                            "variant_2": {"price": 30.00, "cost_per_unit": 25.00}, 
                            "variant_3": {"price": 45.50, "cost_per_unit": 35.00}, 
                            "variant_4": {"price": 65.50, "cost_per_unit": 35.00}, 
                            "variant_5": {"price": 55.50, "cost_per_unit": 35.00}, 
                            "variant_6": {"price": 40.50, "cost_per_unit": 35.00}, 
                        }
                    )

                if settings.BASE_CURRENCY == 'JPY':
                    self._create_order_with_promo(
                        promo_code= promo_sell5.code,
                        currency="JPY",
                        params={
                            "subtotal": "¥131,600",
                            "total": "¥132,931",  
                            "tax": "¥7,911",
                            "customer_id": user.id,
                            "variant_1": {"price": 5000, "cost_per_unit": 4000},
                            "variant_2": {"price": 3000, "cost_per_unit": 2500}, 
                            "variant_3": {"price": 4550, "cost_per_unit": 3500}, 
                            "variant_4": {"price": 6550, "cost_per_unit": 3500}, 
                            "variant_5": {"price": 5550, "cost_per_unit": 3500}, 
                            "variant_6": {"price": 4050, "cost_per_unit": 3500}, 
                        }
                    )

                if settings.BASE_CURRENCY == 'KWD':
                    self._create_order_with_promo(
                        promo_code= promo_sell5.code,
                        currency="KWD",
                        params={
                            "subtotal": "KWD78.000",
                            "total": "KWD77.924",  
                            "tax": "KWD3.824",
                            "customer_id": user.id,
                            "variant_1": {"price": 2.00, "cost_per_unit": 2.00}, 
                            "variant_2": {"price": 3.00, "cost_per_unit": 4.00},
                            "variant_3": {"price": 2.50, "cost_per_unit": 3.00},
                            "variant_4": {"price": 3.50, "cost_per_unit": 2.00}, 
                            "variant_5": {"price": 4.50, "cost_per_unit": 1.00}, 
                            "variant_6": {"price": 1.50, "cost_per_unit": 1.00}, 
                        }
                    )

    def test_order_create_with_promo_clearance20(self):
        product = ProductFactory(
            product_type = ProductTypeFactory(
                taxable = True,
                track_stock = True
            ),
            tax_class=self.tax_class_15,
            status=PublishableStatus.PUBLISHED,
        )
        promo_clearance20 = PromoCodeFactory(
            code="CLEARANCE20", 
            code_type="PERCENTAGE", 
            value=20, 
            is_active=True,
            min_purchase_amount=0,
            min_purchase_period=None,
            redemption_limit=None,
            new_customers_only=False
        )
        apply_product = PromoCodeProductFactory(
            promo_code=promo_clearance20,
            product=product
        )

        if promo_clearance20 and apply_product:
            if settings.BASE_CURRENCY == 'USD':
                self._create_order_with_promo(
                    promo_code= promo_clearance20.code,
                    currency="USD",
                    params={
                        "subtotal": "$7.00",
                        "total": "$6.44",
                        "tax": "$0.84",
                        "applicable_variant": {"price": 3.50, "cost_per_unit": 1.00},
                        "applicable_product" : product
                    }
                )

            if settings.BASE_CURRENCY == 'JPY':
                self._create_order_with_promo(
                    promo_code= promo_clearance20.code,
                    currency="JPY",
                    params={
                        "subtotal": "¥7,000",
                        "total": "¥6,440",  
                        "tax": "¥840",
                        "applicable_variant": {"price": 3500, "cost_per_unit": 1.00},
                        "applicable_product" : product
                    }
                )

            if settings.BASE_CURRENCY == 'KWD':
                self._create_order_with_promo(
                    promo_code= promo_clearance20.code,
                    currency="KWD",
                    params={
                        "subtotal": "KWD7.000",
                        "total": "KWD6.440",  
                        "tax": "KWD0.840",
                        "applicable_variant": {"price": 3.50, "cost_per_unit": 1.00},
                        "applicable_product" : product 
                    }
                )


    def test_order_create_with_custom_discount(self):
        if settings.BASE_CURRENCY == 'USD':
            self._create_order_with_promo(
                promo_code={"name": "500USD", "price": "500"}, # Custom discount add
                currency="USD",
                params={
                    "subtotal": "$13,160.00",
                    "total": "$13,461.11",
                    "tax": "$801.11",
                    "variant_1": {"price": 500, "cost_per_unit": 40},
                    "variant_2": {"price": 300, "cost_per_unit": 25}, 
                    "variant_3": {"price": 455, "cost_per_unit": 35}, 
                    "variant_4": {"price": 655, "cost_per_unit": 35}, 
                    "variant_5": {"price": 555, "cost_per_unit": 35}, 
                    "variant_6": {"price": 405, "cost_per_unit": 35}, 
                }
            )
        if settings.BASE_CURRENCY == 'JPY':
            self._create_order_with_promo(
                promo_code={"name": "500JPY", "price": "500"},
                currency="JPY",
                params={
                    "subtotal": "¥131,600",
                    "total": "¥139,396",  
                    "tax": "¥8,296",
                    "variant_1": {"price": 5000, "cost_per_unit": 400},
                    "variant_2": {"price": 3000, "cost_per_unit": 250}, 
                    "variant_3": {"price": 4550, "cost_per_unit": 350}, 
                    "variant_4": {"price": 6550, "cost_per_unit": 350}, 
                    "variant_5": {"price": 5550, "cost_per_unit": 350}, 
                    "variant_6": {"price": 4050, "cost_per_unit": 350}, 
                }
            )
        if settings.BASE_CURRENCY == 'KWD':
            self._create_order_with_promo(
                promo_code={"name": "700KWD", "price": "700"},
                currency="KWD",
                params={
                    "subtotal": "KWD131,600.000",
                    "total": "KWD139,183.205",  
                    "tax": "KWD8,283.205",
                    "variant_1": {"price": 5000, "cost_per_unit": 400},
                    "variant_2": {"price": 3000, "cost_per_unit": 250}, 
                    "variant_3": {"price": 4550, "cost_per_unit": 350}, 
                    "variant_4": {"price": 6550, "cost_per_unit": 350}, 
                    "variant_5": {"price": 5550, "cost_per_unit": 350}, 
                    "variant_6": {"price": 4050, "cost_per_unit": 350}, 
                }
            )
