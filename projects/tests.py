from django.test import TestCase
from .models import Project


class ProjectTestCase(TestCase):
    def setUp(self):
        Project.objects.create(
            website_title="Test Site 1",
            website_url="https://test.com",
            website_short_description="This is fake test website",
            user_email="test1@test.com",
        )
        Project.objects.create(
            website_title="Example Site 1",
            website_url="https://example.com",
            website_short_description="This is fake example website",
            user_email="example1@example.com",
            published=True,
        )

    def test_Projects_have_email(self):
        """Projects that can speak are correctly identified"""
        test = Project.objects.get(website_title="Test Site 1")
        example = Project.objects.get(website_title="Example Site 1")
        self.assertEqual(test.user_email, "test1@test.com")
        self.assertEqual(example.user_email, "example1@example.com")

    def test_Projects_is_published(self):
        """Projects that can speak are correctly identified"""
        test = Project.objects.get(website_title="Test Site 1")
        example = Project.objects.get(website_title="Example Site 1")
        self.assertEqual(test.published, False)
        self.assertEqual(example.published, True)
