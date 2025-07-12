from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from catalog.admin import KnowledgeBaseAdmin, CategoryAdmin, ArticleAdmin
from catalog.models import KnowledgeBase, Category, Article, Rating, Comment


class AdminSiteTests(TestCase):
    """Test the admin site."""

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="passwordtest123",
        )
        self.client.force_login(self.admin_user)
        self.employee = get_user_model().objects.create_user(
            username="employee",
            password="123password",
            project="KYC",
            level="Senior",
            position="Python Engineer",
        )

    def test_employee_project_level_position_listed(self):
        """
        Test that employee project,
        level and position are in list display on employee admin page.
        """

        url = reverse("admin:catalog_employee_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.employee.project)
        self.assertContains(res, self.employee.level)
        self.assertContains(res, self.employee.position)

    def test_employee_detail_project_level_position_listed(self):
        """
        Test that employee's project,
        level and position are on employee detail admin page.
        """

        url = reverse(
            "admin:catalog_employee_change",
            args=[self.employee.id]
        )
        res = self.client.get(url)
        self.assertContains(res, self.employee.project)
        self.assertContains(res, self.employee.level)
        self.assertContains(res, self.employee.position)

    def test_employee_add_detail_project_level_position_listed(self):
        """
        Test that employee's project,
        level and position are on employee detail admin creation page.
        """

        url = reverse("admin:catalog_employee_add")
        res = self.client.get(url)
        self.assertContains(res, 'name="project"')
        self.assertContains(res, 'name="level"')
        self.assertContains(res, 'name="position"')


class AdminKnowledgeBaseTests(TestCase):
    """Test the admin KnowledgeBase model."""

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="passwordtest123",
        )
        self.client.force_login(self.admin_user)
        self.kn_base = KnowledgeBase.objects.create(
            title="Dogs",
            created_by=self.admin_user
        )
        Category.objects.create(
            topic="Hunting",
            knowledge_base=self.kn_base,
            created_by=self.admin_user
        )
        Category.objects.create(
            topic="Companion",
            knowledge_base=self.kn_base,
            created_by=self.admin_user
        )

        self.admin = KnowledgeBaseAdmin(KnowledgeBase, site)

    def test_count_categories_in_knowledge_base(self):
        """
        Test categories_count
        method returns correct number of categories.
        """

        amount = self.admin.categories_count(self.kn_base)
        self.assertEqual(amount, 2)

    def test_admin_list_view_shows_category_count(self):
        """Test that admin list
        view shows the correct number of categories.
        """

        url = reverse("admin:catalog_knowledgebase_changelist")
        response = self.client.get(url)
        self.assertContains(response, self.kn_base.title)
        self.assertContains(response, "2")


class AdminCategoryTests(TestCase):
    """Test the admin category model."""

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="passwordtest123",
        )
        self.client.force_login(self.admin_user)
        self.kn_base = KnowledgeBase.objects.create(
            title="Cities",
            created_by=self.admin_user
        )
        self.cat = Category.objects.create(
            topic="Capitals",
            knowledge_base=self.kn_base,
            created_by=self.admin_user
        )
        Article.objects.create(
            title="Kyiv",
            category=self.cat,
            author=self.admin_user
        )
        Article.objects.create(
            title="London",
            category=self.cat,
            author=self.admin_user
        )
        Article.objects.create(
            title="Paris",
            category=self.cat,
            author=self.admin_user
        )

        self.admin = CategoryAdmin(Category, site)

    def test_count_categories_in_knowledge_base(self):
        """
        Test categories_count
        method returns correct number of categories.
        """

        amount = self.admin.articles_count(self.cat)
        self.assertEqual(amount, 3)

    def test_admin_list_view_shows_category_count(self):
        """Test that admin list
        view shows the correct number of categories.
        """

        url = reverse("admin:catalog_category_changelist")
        response = self.client.get(url)
        self.assertContains(response, self.cat.topic)
        self.assertContains(response, "3")


class AdminArticleTests(TestCase):
    """Test the admin article model."""

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="passwordtest123",
        )
        self.client.force_login(self.admin_user)

        self.employee = get_user_model().objects.create_user(
            username="employee",
            password="123password",
            project="KYC",
            level="Senior",
            position="Python Engineer",
        )

        self.kn_base = KnowledgeBase.objects.create(
            title="Countries",
            created_by=self.employee
        )

        self.cat = Category.objects.create(
            topic="Capitals",
            knowledge_base=self.kn_base,
            created_by=self.employee
        )

        self.art = Article.objects.create(
            title="London",
            content="London is a capital of Great Britain.",
            category=self.cat,
            author=self.employee,
            is_published=False,
        )

        Rating.objects.create(
            article=self.art,
            employee=self.admin_user,
            rating=4
        )
        Rating.objects.create(
            article=self.art,
            employee=self.employee,
            rating=5
        )
        Comment.objects.create(
            article=self.art,
            commentator=self.admin_user,
            commentary="Great city"
        )

        self.admin = ArticleAdmin(Article, site)

    def test_average_rating(self):
        avg_rating = self.admin.average_rating(self.art)
        expected = round((4 + 5) / 2, 1)
        self.assertEqual(avg_rating, expected)

    def test_rating_count(self):
        self.assertEqual(self.admin.rating_count(self.art), 2)

    def test_comments_count(self):
        self.assertEqual(self.admin.comments_count(self.art), 1)

    def test_get_short_content(self):
        short_cont = self.admin.get_short_content(self.art)
        self.assertLessEqual(len(short_cont), 37)
