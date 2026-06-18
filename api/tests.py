import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from blog.models import Post, Tag
from projects.models import Like, Project


class LikeApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="owner", email="owner@example.com", password="password")
        self.other_user = User.objects.create_user(username="other", email="other@example.com", password="password")
        self.project = Project.objects.create(
            title="Django Packages",
            url="https://djangopackages.example.com",
            short_description="A useful Django directory.",
            published=True,
            active=True,
        )

    def test_list_likes_allows_anonymous_reads(self):
        Like.objects.create(author=self.user, project=self.project, like=True)

        response = self.client.get("/api/v1/like/", {"project": self.project.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["author"], self.user.id)

    def test_create_like_requires_authentication(self):
        response = self.client.post(
            "/api/v1/like/",
            data=json.dumps({"project": self.project.id, "like": True}),
            content_type="application/json",
        )

        self.assertIn(response.status_code, {401, 403})
        self.assertFalse(Like.objects.exists())

    def test_create_like_uses_authenticated_user_not_submitted_author(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/api/v1/like/",
            data=json.dumps({"author": self.other_user.id, "project": self.project.id, "like": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        like = Like.objects.get(project=self.project)
        self.assertEqual(like.author, self.user)
        self.assertTrue(like.like)
        self.assertEqual(response.json()["author"], self.user.id)

    def test_create_like_updates_existing_like_instead_of_creating_duplicate(self):
        Like.objects.create(author=self.user, project=self.project, like=False)
        self.client.force_login(self.user)

        response = self.client.post(
            "/api/v1/like/",
            data=json.dumps({"project": self.project.id, "like": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.filter(author=self.user, project=self.project).count(), 1)
        self.assertTrue(Like.objects.get(author=self.user, project=self.project).like)

    def test_update_like_is_limited_to_authenticated_users_own_like(self):
        other_like = Like.objects.create(author=self.other_user, project=self.project, like=True)
        self.client.force_login(self.user)

        response = self.client.put(
            f"/api/v1/like/{other_like.id}/",
            data=json.dumps({"project": self.project.id, "like": False}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        other_like.refresh_from_db()
        self.assertTrue(other_like.like)

    def test_update_like_only_toggles_value_not_project_or_author(self):
        second_project = Project.objects.create(
            title="Other Project",
            url="https://other-project.example.com",
            short_description="Another project.",
            published=True,
            active=True,
        )
        like = Like.objects.create(author=self.user, project=self.project, like=True)
        self.client.force_login(self.user)

        response = self.client.put(
            f"/api/v1/like/{like.id}/",
            data=json.dumps({"author": self.other_user.id, "project": second_project.id, "like": False}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        like.refresh_from_db()
        self.assertEqual(like.author, self.user)
        self.assertEqual(like.project, self.project)
        self.assertFalse(like.like)

    def test_project_like_toggle_requires_authentication(self):
        response = self.client.post(
            reverse("api_project_like_toggle", kwargs={"project_id": self.project.id}),
            data=json.dumps({"like": True}),
            content_type="application/json",
        )

        self.assertIn(response.status_code, {401, 403})
        self.assertFalse(Like.objects.exists())

    def test_project_like_toggle_creates_like_and_returns_count(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("api_project_like_toggle", kwargs={"project_id": self.project.id}),
            data=json.dumps({"like": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["like"], True)
        self.assertEqual(response.json()["like_count"], 1)
        self.assertTrue(Like.objects.get(author=self.user, project=self.project).like)

    def test_project_like_toggle_updates_existing_like_and_returns_count(self):
        Like.objects.create(author=self.user, project=self.project, like=True)
        Like.objects.create(author=self.other_user, project=self.project, like=True)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("api_project_like_toggle", kwargs={"project_id": self.project.id}),
            data=json.dumps({"like": False}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["like"], False)
        self.assertEqual(response.json()["like_count"], 1)
        self.assertFalse(Like.objects.get(author=self.user, project=self.project).like)

    def test_project_like_toggle_toggles_when_like_value_is_omitted(self):
        Like.objects.create(author=self.user, project=self.project, like=True)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("api_project_like_toggle", kwargs={"project_id": self.project.id}),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["like"], False)
        self.assertEqual(response.json()["like_count"], 0)


class SearchProjectsApiTests(TestCase):
    def test_search_projects_filters_to_public_active_projects_and_limits_results(self):
        for index in range(7):
            Project.objects.create(
                title=f"Django Tool {index}",
                url=f"https://tool-{index}.example.com",
                short_description="Searchable Django project.",
                published=True,
                active=True,
            )
        Project.objects.create(
            title="Django Draft",
            url="https://draft.example.com",
            short_description="Should not show.",
            published=False,
            active=True,
        )
        Project.objects.create(
            title="Django Inactive",
            url="https://inactive.example.com",
            short_description="Should not show.",
            published=True,
            active=False,
        )

        response = self.client.get(reverse("api_search_projects"), {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 5)
        self.assertTrue(all(result["title"].startswith("Django Tool") for result in data))

    def test_search_projects_returns_empty_list_for_blank_query(self):
        response = self.client.get(reverse("api_search_projects"), {"q": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class BlogPostApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="writer", email="writer@example.com", password="password")
        cls.staff_user = User.objects.create_user(
            username="staff-writer",
            email="staff-writer@example.com",
            password="password",
            is_staff=True,
        )
        cls.admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="password")
        cls.user_token = Token.objects.create(user=cls.user)
        cls.staff_token = Token.objects.create(user=cls.staff_user)
        cls.admin_token = Token.objects.create(user=cls.admin)

    def test_post_api_requires_superuser_token(self):
        payload = self.post_payload()

        anonymous_response = self.client.post(
            reverse("api_create_post"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertIn(anonymous_response.status_code, {401, 403})

        user_token_response = self.client.post(
            reverse("api_create_post"),
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers(self.user_token),
        )
        self.assertEqual(user_token_response.status_code, 403)

        staff_token_response = self.client.post(
            reverse("api_create_post"),
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers(self.staff_token),
        )
        self.assertEqual(staff_token_response.status_code, 403)

        self.client.force_login(self.admin)
        session_response = self.client.post(
            reverse("api_create_post"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertIn(session_response.status_code, {401, 403})

        self.assertFalse(Post.objects.filter(slug="testing-django").exists())

    def test_create_post_assigns_token_user_author_and_creates_tags(self):
        response = self.client.post(
            reverse("api_create_post"),
            data=json.dumps(self.post_payload()),
            content_type="application/json",
            **self.auth_headers(self.admin_token),
        )

        self.assertEqual(response.status_code, 201)
        post = Post.objects.get(slug="testing-django")
        self.assertEqual(post.author, self.admin)
        self.assertEqual(post.level, Post.INTERMEDIATE)
        self.assertEqual(post.unsplashID, "testing-image")
        self.assertEqual(set(post.tags.values_list("name", flat=True)), {"Django", "Testing"})
        self.assertTrue(Tag.objects.filter(name="Django", slug="django").exists())
        self.assertEqual(response.json()["author"], self.admin.id)

    def test_list_posts_returns_all_posts_to_superuser_token(self):
        draft = self.make_post(title="Draft Guide", slug="draft-guide", status=Post.DRAFT)
        published = self.make_post(title="Published Guide", slug="published-guide", status=Post.PUBLISHED)

        response = self.client.get(reverse("api_create_post"), **self.auth_headers(self.admin_token))

        self.assertEqual(response.status_code, 200)
        post_ids = {post["id"] for post in response.json()}
        self.assertEqual(post_ids, {draft.id, published.id})

    def test_retrieve_post_returns_post_detail_to_superuser_token(self):
        post = self.make_post(title="Agent Guide", slug="agent-guide")
        post.tags.add(Tag.objects.create(name="Agents", slug="agents"))

        response = self.client.get(reverse("api_post_detail", args=[post.id]), **self.auth_headers(self.admin_token))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], post.id)
        self.assertEqual(data["title"], "Agent Guide")
        self.assertEqual(data["tag_list"], [{"id": post.tags.first().id, "name": "Agents", "slug": "agents"}])

    def test_update_post_changes_fields_and_replaces_tags(self):
        post = self.make_post(title="Old Guide", slug="old-guide", status=Post.DRAFT)
        post.tags.add(Tag.objects.create(name="Old", slug="old"))

        response = self.client.patch(
            reverse("api_post_detail", args=[post.id]),
            data=json.dumps(
                {
                    "title": "Updated Guide",
                    "status": Post.PUBLISHED,
                    "level": Post.ADVANCED,
                    "tags": "Django, Agents",
                }
            ),
            content_type="application/json",
            **self.auth_headers(self.admin_token),
        )

        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated Guide")
        self.assertEqual(post.status, Post.PUBLISHED)
        self.assertEqual(post.level, Post.ADVANCED)
        self.assertEqual(set(post.tags.values_list("name", flat=True)), {"Django", "Agents"})

    def test_delete_post_removes_post(self):
        post = self.make_post(title="Delete Me", slug="delete-me")

        response = self.client.delete(reverse("api_post_detail", args=[post.id]), **self.auth_headers(self.admin_token))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def post_payload(self):
        return {
            "title": "Testing Django",
            "description": "A guide to testing Django projects.",
            "slug": "testing-django",
            "tags": "Django, Testing",
            "content": "Use tests to protect behavior.",
            "status": Post.PUBLISHED,
            "type": Post.TUTORIAL,
            "level": Post.INTERMEDIATE,
            "unsplashID": "testing-image",
        }

    def make_post(self, **kwargs):
        defaults = {
            "title": "Testing Django",
            "description": "A guide to testing Django projects.",
            "slug": "testing-django",
            "content": "Use tests to protect behavior.",
            "status": Post.PUBLISHED,
            "type": Post.TUTORIAL,
            "level": Post.BEGINNER,
            "author": self.admin,
        }
        defaults.update(kwargs)
        return Post.objects.create(**defaults)

    def auth_headers(self, token):
        return {"HTTP_AUTHORIZATION": f"Token {token.key}"}
