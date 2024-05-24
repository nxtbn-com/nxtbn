import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from nxtbn.product.models import Product, ProductVariant
from nxtbn.order.models import Order, OrderLineItem, Address
from nxtbn.payment.models import Payment, PaymentMethod

fake = Faker()

class PaymentStatus:
    SUCCESS = 'Success'
    FAILED = 'Failed'

class Command(BaseCommand):
    help = 'Generate fake orders for selected products'
    
    def handle(self, *args, **options):
        selected_products = Product.objects.filter(variants__isnull=False).distinct().order_by('?')[:5]
        User = get_user_model()

        for product in selected_products:
            default_variant = product.variants.first()  
            if not default_variant:
                self.stdout.write(self.style.WARNING(f"Skipping product '{product.name}' because it doesn't have any variants defined"))
                continue

            shipping_address = Address.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                street_address=fake.street_address(),
                city=fake.city(),
                country=fake.country(),
                phone_number=fake.phone_number(),
                email_address=fake.email()
            )
            billing_address = Address.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                street_address=fake.street_address(),
                city=fake.city(),
                country=fake.country(),
                phone_number=fake.phone_number(),
                email_address=fake.email()
            )

            random_user = User.objects.order_by('?').first()

        
            payment_status = random.choice([PaymentStatus.SUCCESS, PaymentStatus.FAILED])
            paid_at = timezone.now() if payment_status == PaymentStatus.SUCCESS else None

            order = Order.objects.create(
                user=random_user, 
                vendor=product.vendor,
                payment_method=random.choice(['Credit Card', 'PayPal', 'Cash on Delivery']),  
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_price=default_variant.price,
                status=random.choice(['Pending', 'Confirmed', 'Shipped']) 
            )

            OrderLineItem.objects.create(
                order=order,
                variant=default_variant,
                quantity=random.randint(1, 5),  
                price_per_unit=default_variant.price,
                total_price=default_variant.price  
            )

            payment_status = random.choice([PaymentStatus.SUCCESS, PaymentStatus.FAILED]) 
            paid_at = timezone.now() if payment_status == PaymentStatus.SUCCESS else None

            payment = Payment.objects.create(
                order=order,
                payment_method=random.choice([PaymentMethod.CREDIT_CARD, PaymentMethod.PAYPAL]),  
                payment_amount=order.total_price,
                payment_status=payment_status,
                paid_at=paid_at,
            )

            self.stdout.write(self.style.SUCCESS(f"Fake order created for product '{product.name}'. Payment {'successful' if payment_status == PaymentStatus.SUCCESS else 'failed'}"))

        self.stdout.write(self.style.SUCCESS('Fake orders generation completed'))
