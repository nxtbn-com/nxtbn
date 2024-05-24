import os
import json
from django.core.management.base import BaseCommand
from nxtbn.product.models import Category
from django.conf import settings
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Create categories and subcategories'

    def handle(self, *args, **options):
        json_file_path = os.path.join(settings.BASE_DIR, 'nxtbn', 'seeder_files', 'categories.json')
        
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            self.create_categories(data['categories'])

    def create_categories(self, categories_data, parent=None):
        for category_data in tqdm(categories_data):
            category_name = category_data['category']
            category, created = Category.objects.get_or_create(
                name=category_name,
                parent=parent
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category_name}'))

            subcategories_data = category_data.get('subcategories', [])
            for subcategory_data in subcategories_data:
                subcategory_name = subcategory_data['Subcategory']
                subcategory, sub_created = Category.objects.get_or_create(
                    name=subcategory_name,
                    parent=category
                )
                if sub_created:
                    self.stdout.write(self.style.SUCCESS(f'Created subcategory: {subcategory_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Subcategory already exists: {subcategory_name}'))

                subsubcategories_data = subcategory_data.get('subsubcategories', [])
                for subsubcategory_name in subsubcategories_data:
                    subsubcategory, subsub_created = Category.objects.get_or_create(
                        name=subsubcategory_name,
                        parent=subcategory
                    )
                    if subsub_created:
                        self.stdout.write(self.style.SUCCESS(f'Created subsubcategory: {subsubcategory_name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Subsubcategory already exists: {subsubcategory_name}'))
