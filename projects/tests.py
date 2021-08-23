from django.test import TestCase

from .models import Project


class ProjectTestCase(TestCase):
    def setUp(self):
        Project.objects.create(
            title="Test Site 1",
            url="https://test.com",
            short_description="This is fake test website",
            user_email="test1@test.com",
        )
        Project.objects.create(
            title="Example Site 1",
            url="https://example.com",
            short_description="This is fake example website",
            user_email="example1@example.com",
            published=True,
        )

    def test_Projects_have_email(self):
        """Projects that can speak are correctly identified"""
        test = Project.objects.get(title="Test Site 1")
        example = Project.objects.get(title="Example Site 1")
        self.assertEqual(test.user_email, "test1@test.com")
        self.assertEqual(example.user_email, "example1@example.com")

    def test_Projects_is_published(self):
        """Projects that can speak are correctly identified"""
        test = Project.objects.get(title="Test Site 1")
        example = Project.objects.get(title="Example Site 1")
        self.assertEqual(test.published, False)
        self.assertEqual(example.published, True)
