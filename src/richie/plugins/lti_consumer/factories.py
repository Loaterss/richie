"""
LTIConsumer CMS plugin factories
"""
import factory

from richie.apps.courses.factories import CourseFactory

from .models import LTIConsumer


class LTIConsumerFactory(factory.django.DjangoModelFactory):
    """
    Factory to create random instances of LTIConsumer for testing.
    """

    class Meta:
        model = LTIConsumer

    url = factory.Faker("url")
    course = factory.SubFactory(CourseFactory)
