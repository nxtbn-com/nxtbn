import factory
import random

from nxtbn.users.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name).lower())
    username = factory.LazyAttribute(lambda a: '{0}.{1}example.com'.format(a.first_name, a.last_name).lower())
    is_active = True
    is_staff = True
    is_superuser = True
