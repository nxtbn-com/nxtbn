import os
import json
from django.core.management.base import BaseCommand
from nxtbn.product.models import Collection
from django.conf import settings
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Create Collections'

    def handle(self, *args, **options):
        ecom_collections = [
            "New Arrivals",
            "Best Sellers",
            "Clearance",
            "Featured",
            "Summer Collection",
            "Winter Collection",
            "Outdoor Equipment",
            "Home Appliances",
            "Electronics",
            "Fashion",
            "Footwear",
            "Accessories",
            "Sports Gear",
            "Toys & Games",
            "Beauty & Personal Care"
        ]

        for collection in tqdm(ecom_collections):
            if not Collection.objects.filter(name=collection).exists():
                Collection.objects.create(name=collection)

        self.stdout.write(self.style.SUCCESS('Collections created successfully.'))