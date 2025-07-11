from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.forms import EmployeeRegistrationForm
from catalog.models import (
    KnowledgeBase,
    Category,
    Article,
    Employee,
    Comment
)

KNOWLEDGE_BASE_LIST_URL = reverse("catalog:knowledge-list")
CATEGORY_LIST_URL = reverse("catalog:category-list")
ARTICLE_LIST_URL = reverse("catalog:article-list")
EMPLOYEE_LIST_URL = reverse("catalog:employee-list")
HOME_PAGE_URL = reverse("catalog:home")


class HomeTest(TestCase):
    """Test the home page view."""

    def test_login_home_required(self):
        res = self.client.get(HOME_PAGE_URL)
        self.assertNotEqual(res.status_code, 200)

    def test_login_home(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="test123",
            position="HR_BP"
        )
        self.client.force_login(self.user)
        response = self.client.get(HOME_PAGE_URL)
        self.assertEqual(response.status_code, 200)


class PublicKnowledgeBaseTest(TestCase):
    """Test the knowledge base list and detail without login."""

    def test_login_kn_base_list_required(self):
        res = self.client.get(KNOWLEDGE_BASE_LIST_URL)
        self.assertNotEqual(res.status_code, 200)

    def test_login_kn_base_detail_required(self):
        res = self.client.get(
            reverse(
                "catalog:knowledge-base-detail",
                kwargs={"pk": 1}
            )
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateKnowledgeBaseTest(TestCase):
    """Test the knowledge base views with login."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="test123",
            position="HR_BP"
        )
        self.client.force_login(self.user)

    def test_retrieve_knowledge_bases(self):
        KnowledgeBase.objects.create(
            title="On_boarding",
            created_by=self.user,
        )
        KnowledgeBase.objects.create(
            title="Off_boarding",
            created_by=self.user,
        )
        response = self.client.get(KNOWLEDGE_BASE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        knowledge_bases = KnowledgeBase.objects.all()
        self.assertEqual(
            list(response.context["knowledge_base_list"]),
            list(knowledge_bases)
        )
        self.assertTemplateUsed(response, "catalog/knowledge_base_list.html")

    def test_retrieve_knowledge_base(self):
        kn_base = KnowledgeBase.objects.create(
            title="On_boarding",
            created_by=self.user,
        )

        response = self.client.get(
            reverse(
                "catalog:knowledge-base-detail",
                kwargs={"pk": kn_base.pk})
        )

        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            response.context["knowledge_base_detail"],
            kn_base
        )
        self.assertTemplateUsed(
            response,
            "catalog/knowledge_base_detail.html"
        )

    def test_create_knowledge_base(self):
        form_data = {
            "title": "On_boarding",
            "created_by": self.user.id,
        }

        response = self.client.post(
            reverse("catalog:knowledge-base-create"),
            data=form_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            KnowledgeBase.objects.filter(title="On_boarding").exists()
        )
        self.assertRedirects(response, KNOWLEDGE_BASE_LIST_URL)

    def test_update_knowledge_base_by_owner(self):
        kn_base = KnowledgeBase.objects.create(
            title="On_boarding",
            created_by=self.user
        )

        response = self.client.post(
            reverse(
                "catalog:knowledge-base-update",
                kwargs={"pk": kn_base.pk}
            ),
            {
                "title": "Updated On_boarding",
                "created_by": self.user.id,
            }
        )

        self.assertEqual(response.status_code, 302)
        kn_base.refresh_from_db()
        self.assertEqual(
            kn_base.title,
            "Updated On_boarding"
        )

    def test_update_knowledge_base_forbidden_for_non_owner(self):
        other_user = get_user_model().objects.create_user(
            username="other",
            password="pass1word234"
        )
        kn_base = KnowledgeBase.objects.create(
            title="Zero_HR",
            created_by=other_user
        )

        response = self.client.post(
            reverse("catalog:knowledge-base-update", args=[kn_base.pk]),
            {
                "title": "Hacked!",
                "created_by": other_user.id,
             }
        )

        self.assertEqual(response.status_code, 403)
        kn_base.refresh_from_db()
        self.assertNotEqual(kn_base.title, "Hacked!")

    def test_delete_knowledge_base_without_categories(self):
        kn_base = KnowledgeBase.objects.create(
            title="Off_boarding",
            created_by=self.user
        )

        response = self.client.post(
            reverse(
                "catalog:knowledge-base-delete",
                kwargs={"pk": kn_base.pk}
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            KnowledgeBase.objects.filter(pk=kn_base.pk).exists()
        )

    def test_delete_knowledge_base_with_categories(self):
        kn_base = KnowledgeBase.objects.create(
            title="Off_boarding",
            created_by=self.user
        )
        Category.objects.create(
            topic="Compensation",
            created_by=self.user,
            knowledge_base=kn_base
        )

        response = self.client.post(
            reverse(
                "catalog:knowledge-base-delete",
                kwargs={"pk": kn_base.pk}
            )
        )

        self.assertTrue(KnowledgeBase.objects.filter(pk=kn_base.pk).exists())
        self.assertEqual(response.status_code, 302)

    def test_kn_base_list_contains_paginated_objects(self):
        for i in range(7):
            KnowledgeBase.objects.create(
                title=f"KB {i}",
                created_by=self.user
            )
        response = self.client.get(KNOWLEDGE_BASE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(len(response.context["knowledge_base_list"]), 3)
        response = self.client.get(KNOWLEDGE_BASE_LIST_URL + "?page=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["knowledge_base_list"]), 1)


class PublicCategoryTest(TestCase):
    """Test the category list and details without login."""

    def test_login_category_list_required(self):
        res = self.client.get(CATEGORY_LIST_URL)
        self.assertNotEqual(res.status_code, 200)

    def test_login_category_detail_required(self):
        res = self.client.get(
            reverse(
                "catalog:category-detail",
                kwargs={"pk": 1}
            )
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateCategoryTest(TestCase):
    """Test the category views with login."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="test123",
            position="Employee"
        )
        self.client.force_login(self.user)

        self.knowledge_base = KnowledgeBase.objects.create(
            title="Hobby",
            created_by=self.user,
        )

    def test_retrieve_categories(self):
        Category.objects.create(
            topic="Running",
            created_by=self.user,
            knowledge_base=self.knowledge_base,
        )
        Category.objects.create(
            topic="Singing",
            created_by=self.user,
            knowledge_base=self.knowledge_base,
        )
        response = self.client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, 200)
        categories = Category.objects.all()
        self.assertEqual(
            list(response.context["category_list"]),
            list(categories)
        )
        self.assertTemplateUsed(
            response,
            "catalog/category_list.html"
        )

    def test_retrieve_category(self):
        category = Category.objects.create(
            topic="Running",
            created_by=self.user,
            knowledge_base=self.knowledge_base,
         )

        response = self.client.get(
            reverse(
                "catalog:category-detail",
                kwargs={"pk": category.pk}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["category_detail"],
            category
        )
        self.assertTemplateUsed(
            response,
            "catalog/category_detail.html"
        )

    def test_create_category(self):
        form_data = {
            "topic": "Lifting",
            "created_by": self.user.id,
            "knowledge_base": self.knowledge_base.id,
        }

        response = self.client.post(
            reverse("catalog:category-create"),
            data=form_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Category.objects.filter(topic="Lifting").exists()
        )
        self.assertRedirects(response, CATEGORY_LIST_URL)

    def test_update_category_owner(self):
        category = Category.objects.create(
            topic="Sport",
            created_by=self.user,
            knowledge_base=self.knowledge_base
        )

        response = self.client.post(
            reverse(
                "catalog:category-update",
                kwargs={"pk": category.pk}
            ),
            {
                "topic": "Updated Sport",
                "created_by": self.user.id,
                "knowledge_base": self.knowledge_base.id,
            }
        )

        self.assertEqual(response.status_code, 302)
        category.refresh_from_db()
        self.assertEqual(category.topic, "Updated Sport")

    def test_update_category_forbidden_for_non_owner(self):
        other_user = get_user_model().objects.create_user(
            username="other",
            password="pass1word234"
        )
        category = Category.objects.create(
            topic="Run",
            created_by=other_user,
            knowledge_base=self.knowledge_base
        )

        response = self.client.post(
            reverse("catalog:category-update", args=[category.pk]),
            {
                "topic": "Hacked!",
                "created_by": other_user.id,
                "knowledge_base": self.knowledge_base.id,
             }
        )

        self.assertEqual(response.status_code, 403)
        category.refresh_from_db()
        self.assertNotEqual(category.topic, "Hacked!")

    def test_delete_category_without_articles(self):
        category = Category.objects.create(
            topic="Reading",
            created_by=self.user,
            knowledge_base=self.knowledge_base
        )

        response = self.client.post(
            reverse(
                "catalog:category-delete",
                kwargs={"pk": category.pk}
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Category.objects.filter(
                pk=category.pk
            ).exists())

    def test_delete_category_with_categories(self):
        category = Category.objects.create(
            topic="Reading",
            created_by=self.user,
            knowledge_base=self.knowledge_base
        )
        Article.objects.create(
            title="The who",
            author=self.user,
            content="The who content...",
            category=category,
        )

        response = self.client.post(
            reverse(
                "catalog:knowledge-base-delete",
                kwargs={"pk": category.pk}
            )
        )

        self.assertTrue(Category.objects.filter(pk=category.pk).exists())
        self.assertEqual(response.status_code, 302)

    def test_category_list_contains_paginated_objects(self):
        for i in range(7):
            Category.objects.create(
                topic=f"CAT {i}",
                created_by=self.user,
                knowledge_base=self.knowledge_base
            )
        response = self.client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(len(response.context["category_list"]), 3)
        response = self.client.get(CATEGORY_LIST_URL + "?page=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["category_list"]), 1)


class PublicArticleTest(TestCase):
    """Test the article list and detail without login."""

    def test_login_article_list_required(self):
        res = self.client.get(ARTICLE_LIST_URL)
        self.assertNotEqual(res.status_code, 200)

    def test_login_article_detail_required(self):
        res = self.client.get(
            reverse(
                "catalog:article-detail",
                kwargs={"pk": 1}
            )
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateArticleTest(TestCase):
    """Test the article views with login."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="test123",
            position="Employee"
        )
        self.client.force_login(self.user)

        self.knowledge_base = KnowledgeBase.objects.create(
            title="Cars",
            created_by=self.user,
        )
        self.category = Category.objects.create(
            topic="Germany",
            created_by=self.user,
            knowledge_base=self.knowledge_base
        )

    def test_retrieve_articles(self):
        Article.objects.create(
            title="BMW",
            author=self.user,
            category=self.category,
            content="BMW_Content",
        )
        Article.objects.create(
            title="AUDI",
            author=self.user,
            category=self.category,
            content="AUDI_Content",
        )
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        articles = Article.objects.all()
        self.assertEqual(
            list(response.context["article_list"]),
            list(articles)
        )
        self.assertTemplateUsed(response, "catalog/article_list.html")

    def test_retrieve_category(self):
        article = Article.objects.create(
            title="BMW",
            author=self.user,
            category=self.category,
            content="BMW_Content",
         )

        response = self.client.get(
            reverse(
                "catalog:article-detail",
                kwargs={"pk": article.pk}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["article_detail"], article)
        self.assertTemplateUsed(
            response,
            "catalog/article_detail.html"
        )

    def test_create_article(self):
        form_data = {
            "title": "BMW",
            "author": self.user.id,
            "category": self.category.id,
            "content": "BMW_Content",
        }

        response = self.client.post(
            reverse("catalog:article-create"),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title="BMW").exists())
        self.assertRedirects(response, ARTICLE_LIST_URL)

    def test_update_article_with_author(self):
        article = Article.objects.create(
             title="BMW",
             author=self.user,
             category=self.category,
             content="BMW_Content",
         )

        response = self.client.post(
            reverse(
                "catalog:article-update",
                kwargs={"pk": article.pk}
            ),
            {
                "title": "AUDI",
                "author": self.user.id,
                "category": self.category.id,
                "content": "AUDI_Content",
            }
        )

        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.title, "AUDI")

    def test_update_article_forbidden_for_non_author(self):
        other_user = get_user_model().objects.create_user(
            username="other",
            password="pass1word234"
        )
        article = Article.objects.create(
            title="Tesla",
            author=other_user,
            category=self.category,
            content="Tesla_Content",
        )

        response = self.client.post(
            reverse("catalog:article-update", args=[article.pk]),
            {
                "title": "Hacked!",
                "author": other_user.id,
                "category": self.category.id,
                "content": "Hacked_Content",
             }
        )

        self.assertEqual(response.status_code, 403)
        article.refresh_from_db()
        self.assertNotEqual(article.title, "Hacked_Content")

    def test_delete_article_by_author_another(self):
        other_user = get_user_model().objects.create_user(
            username="other",
            password="pass1word234"
        )

        article_1 = Article.objects.create(
            title="Tesla",
            author=self.user,
            category=self.category,
            content="Tesla_Content",
        )

        article_2 = Article.objects.create(
            title="BMW",
            author=other_user,
            category=self.category,
            content="BMW_Content",
        )

        response = self.client.post(
            reverse(
                "catalog:article-delete",
                kwargs={"pk": article_1.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Article.objects.filter(pk=article_1.pk).exists())

        response_2 = self.client.post(
            reverse("catalog:article-delete", kwargs={"pk": article_2.pk})
        )
        self.assertEqual(response_2.status_code, 302)
        self.assertTrue(Article.objects.filter(pk=article_2.pk).exists())
        self.assertTrue(Article.objects.filter(pk=article_2.pk).exists())

    def test_article_list_contains_paginated_objects(self):
        for i in range(7):
            Article.objects.create(
                title=f"ART {i}",
                author=self.user,
                category=self.category,
                content="ART_Content",
            )
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(len(response.context["article_list"]), 3)
        response = self.client.get(ARTICLE_LIST_URL + "?page=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["article_list"]), 1)


class PublicEmployeeTest(TestCase):
    """Test the employee list and detail without login."""

    def test_login_employee_list_required(self):
        res = self.client.get(EMPLOYEE_LIST_URL)
        self.assertNotEqual(res.status_code, 200)

    def test_login_employee_detail_required(self):
        res = self.client.get(
            reverse(
                "catalog:employee-detail",
                kwargs={"pk": 1}
            )
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateEmployeeTest(TestCase):
    """Test the employee views with login."""

    def test_retrieve_employees(self):
        self.user_1 = get_user_model().objects.create_user(
            username="employee_1",
            password="test123",
            position="Employee"
        )
        self.user_2 = get_user_model().objects.create_user(
            username="employee_2",
            password="test1234",
            position="Employee"
        )
        self.client.force_login(self.user_1)
        self.client.force_login(self.user_1)

        response = self.client.get(EMPLOYEE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        employees = Employee.objects.all()
        self.assertEqual(
            list(response.context["employee_list"]),
            list(employees)
        )
        self.assertTemplateUsed(response, "catalog/employees_list.html")

    def test_retrieve_employee(self):
        self.user = get_user_model().objects.create_user(
            username="employee_1",
            password="test123",
            position="Employee"
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "catalog:employee-detail",
                kwargs={"pk": self.user.pk}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["employee_detail"],
            self.user
        )
        self.assertTemplateUsed(
            response,
            "catalog/employee_detail.html"
        )

    def test_employee_can_update_self(self):
        self.user = get_user_model().objects.create_user(
            username="employee_1",
            password="test123",
            position="Employee"
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("catalog:employee-update", kwargs={"pk": self.user.pk}),
            {
                "username": "employee_2",
                "position": "Employee Update",
            }
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.position, "Employee Update")

    def test_employee_update_forbidden_for_other(self):
        self.user = get_user_model().objects.create_user(
            username="employee_1",
            password="test123",
            position="Employee"
        )
        other = get_user_model().objects.create_user(
            username="employee_2",
            password="test123",
            position="hacker"
        )
        self.client.force_login(other)

        response = self.client.post(
            reverse("catalog:employee-update", kwargs={"pk": self.user.pk}),
            {"username": "hacked", "position": "profile_hacked"}
        )

        self.assertEqual(response.status_code, 403)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, "hacked")
        self.assertNotEqual(self.user.position, "profile_hucked")

    def test_delete_employee_by_admin(self):
        self.user = get_user_model().objects.create_superuser(
            username="employee_1",
            password="test123",
            position="Employee"
        )
        other = get_user_model().objects.create_user(
            username="employee_2",
            password="test123",
            position="hacker"
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("catalog:employee-delete", kwargs={"pk": other.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Employee.objects.filter(pk=other.pk).exists())

    def test_employee_list_contains_paginated_objects(self):
        user = get_user_model().objects.create_user(
            username="employee",
            password="test123",
            position="HR_BP"
        )
        self.client.force_login(user)

        for i in range(6):
            get_user_model().objects.create_user(
                username=f"Emp {i}",
                password=f"password{i}{i}{i}",
                position=f"position{i}",
            )

        response = self.client.get(EMPLOYEE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(len(response.context["employee_list"]), 3)
        response = self.client.get(EMPLOYEE_LIST_URL + "?page=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["employee_list"]), 1)


class RegistrationTest(TestCase):
    """Test the registration page."""

    def test_register_view_get(self):
        response = self.client.get(reverse("catalog:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "registration/register.html"
        )
        self.assertIsInstance(
            response.context["form"],
            EmployeeRegistrationForm
        )

    def test_register_view_post_valid(self):
        form_data = {
            "username": "testuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "position": "QA",
            "email": "email@email.com",
            "first_name": "test_first",
            "last_name": "test_last",
            "project": "test_project",
            "level": "test_senior",
        }

        response = self.client.post(
            reverse("catalog:register"),
            data=form_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, HOME_PAGE_URL)
        self.assertTrue(get_user_model().objects.filter(
            username="testuser"
        ).exists())


class CommentTest(TestCase):
    """Test the comment update and delete views."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="test123",
            position="Employee"
        )
        self.client.force_login(self.user)

        self.knowledge_base = KnowledgeBase.objects.create(
            title="Cars",
            created_by=self.user,
        )
        self.category = Category.objects.create(
            topic="Germany",
            created_by=self.user,
            knowledge_base=self.knowledge_base
        )
        self.article = Article.objects.create(
            title="BMW",
            author=self.user,
            category=self.category,
            content="This is a article about BMW.",
            is_published=True,
        )

    def test_comment_update_commentator(self):
        comment = Comment.objects.create(
            article=self.article,
            commentator=self.user,
            commentary="some commentary",
        )
        response = self.client.post(
            reverse(
                "catalog:comment-update",
                kwargs={"article_pk": self.article.pk, "pk": comment.pk}
            ),
            {
                "commentary": "update_content",
            }
        )
        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.commentary, "update_content")

    def test_comment_update_forbidden_oter(self):
        other = get_user_model().objects.create_user(
            username="employee_2",
            password="pass122333",
            position="Employee"
        )
        comment = Comment.objects.create(
            article=self.article,
            commentator=other,
            commentary="some commentary",
        )
        response = self.client.post(
            reverse(
                "catalog:comment-update",
                kwargs={"article_pk": self.article.pk, "pk": comment.pk}
            ),
            {
                "commentary": "update_content",
            }
        )
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.commentary, "update_content")

    def test_comment_delete_commentator(self):
        comment = Comment.objects.create(
            article=self.article,
            commentator=self.user,
            commentary="some commentary",
        )
        response = self.client.post(
            reverse(
                "catalog:comment-delete",
                kwargs={"article_pk": self.article.pk, "pk": comment.pk}
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_comment_delete_forbidden_other(self):
        other = get_user_model().objects.create_user(
            username="employee_2",
            password="pass122333",
            position="Employee"
        )
        comment = Comment.objects.create(
            article=self.article,
            commentator=other,
            commentary="some commentary",
        )
        response = self.client.post(
            reverse(
                "catalog:comment-delete",
                kwargs={"article_pk": self.article.pk, "pk": comment.pk}
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(pk=comment.pk).exists())
