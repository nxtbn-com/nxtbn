from django.core.management.base import BaseCommand
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi
from drf_yasg.renderers import SwaggerYAMLRenderer
from nxtbn.swagger_views import DASHBOARD_PATTERNS, STOREFRONT_PATTERNS

class Command(BaseCommand):
    help = 'Generate Swagger documentation for both Dashboard and Storefront APIs'

    def handle(self, *args, **kwargs):
        self.generate_dashboard_schema()
        self.generate_storefront_schema()

    def generate_dashboard_schema(self):
        generator = OpenAPISchemaGenerator(
            info=openapi.Info(
                title="nxtbn Dashboard API",
                default_version='v1',
                description="API documentation for nxtbn Dashboard",
            ),
            patterns=DASHBOARD_PATTERNS,
        )
        schema = generator.get_schema(request=None, public=True)
        yaml_string = SwaggerYAMLRenderer().render(schema, renderer_context={})
        output_file = 'dashboard_openapi.yaml'
        with open(output_file, 'w') as f:
            f.write(yaml_string.decode('utf-8'))
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {output_file}'))

    def generate_storefront_schema(self):
        generator = OpenAPISchemaGenerator(
            info=openapi.Info(
                title="nxtbn Storefront API",
                default_version='v1',
                description="API documentation for nxtbn Storefront",
            ),
            patterns=STOREFRONT_PATTERNS,
        )
        schema = generator.get_schema(request=None, public=True)
        yaml_string = SwaggerYAMLRenderer().render(schema, renderer_context={})
        output_file = 'storefront_openapi.yaml'
        with open(output_file, 'w') as f:
            f.write(yaml_string.decode('utf-8'))
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {output_file}'))
