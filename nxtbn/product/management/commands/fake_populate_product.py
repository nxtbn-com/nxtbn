from django.core.management.base import BaseCommand
import requests
from nxtbn.product.models import Category, Collection, Product, ProductVariant
from django.contrib.auth import get_user_model
from nxtbn.product import ProductType, StockStatus, WeightUnits
from faker import Faker
from nxtbn.filemanager.models import Image
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create fake products with multiple variants'

    def add_arguments(self, parser):
        parser.add_argument('--num_products', type=int, default=10, help='Number of fake products to create')

    def fetch_random_image_url(self, width=300, height=200):
        response = requests.get(f'https://source.unsplash.com/random/{width}x{height}')
        if response.status_code == 200:
            return response.content
        else:
            return None

    def handle(self, *args, **options):
        fake = Faker()

        num_products = options['num_products']
        categories = Category.objects.all()
        collections = Collection.objects.all()

        for _ in range(num_products):
            category = random.choice(categories)
            collection = random.choice(collections)
            product_type = random.choice(ProductType.choices)
            weight_unit = random.choice(WeightUnits.choices)

            superuser = User.objects.filter(username='admin').first()
            if not superuser:
                self.stdout.write(self.style.NOTICE('Creating superuser with username "admin" and password "admin"...'))
                superuser = User.objects.create_superuser('admin', 'admin@example.com', 'admin')


            image_object = self.fetch_random_image_url()
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(image_object)
            img_temp.flush()
            image_file = File(
                img_temp,
                name=f'{fake.word()}.jpg'
            )
         
            name = fake.word() 
            image = Image.objects.create(
                created_by=superuser,
                name=name,
                image=image_file,  
                image_alt_text=fake.sentence()
            )

            product = Product.objects.create(
                name=fake.word(),
                summary=fake.sentence(),
                description=fake.paragraph(),
                brand=fake.company(),
                category=category,
                created_by=superuser,
                last_modified_by=None,
                type=product_type[0],
                
            )

            product.collections.set([collection])

            default_variant = ProductVariant.objects.create(
                product=product,
                name='Default',
                price=random.uniform(10, 1000),
                cost_per_unit=random.uniform(5, 500),
                compare_at_price=random.uniform(15, 1500),
                sku=fake.uuid4(),
                weight_unit=weight_unit[0],
                weight_value=random.uniform(1, 1000),
            )

            default_variant.variant_image.add(image)

            product.default_variant = default_variant

            for _ in range(random.randint(1, 5)):
                weight_unit = random.choice(WeightUnits.choices)
                variant = ProductVariant.objects.create(
                    product=product,
                    name=fake.word(),
                    price=random.uniform(10, 1000),
                    cost_per_unit=random.uniform(5, 500),
                    compare_at_price=random.uniform(15, 1500),
                    sku=fake.uuid4(),
                    weight_unit=weight_unit[0],
                    weight_value=random.uniform(1, 1000),
                )

            product.save()

        self.stdout.write(self.style.SUCCESS(f'Created {num_products} fake products with multiple variants'))
