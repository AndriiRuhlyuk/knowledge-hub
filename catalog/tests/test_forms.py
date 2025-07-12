from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.forms import (
    EmployeeRegistrationForm,
    KnowledgeBaseSearchForm,
    CategorySearchForm,
    ArticleSearchForm,
    EmployeeSearchForm,
    KnowledgeBaseForm,
    CategoryForm,
    ArticleForm,
    RatingForm,
    CommentForm
)
from catalog.models import (
    KnowledgeBase,
    Category
)


class FormsTest(TestCase):
    """Test the forms."""

    def test_employee_registration_form_with_position_level_project(self):
        """Test Employee Registration Form with valid data"""

        form_data = {
            "username": "test",
            "email": "mail@mail.com",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "password1": "strongPASSWORD123!",
            "password2": "strongPASSWORD123!",
            "project": "KYC",
            "position": "Employee",
            "level": "Senior",
        }
        form = EmployeeRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_knowledge_base_creation_form(self):
        """Test KnowledgeBase Creation Form"""

        self.user = get_user_model().objects.create_user(
            username="employee",
            password="passtestTEST123!",
            position="Employee"
        )

        form_data = {
            "title": "test_title",
            "short_description": "test_short_description",
            "created_by": self.user.id,
        }
        form = KnowledgeBaseForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["title"],
            "test_title")
        self.assertEqual(
            form.cleaned_data["short_description"],
            "test_short_description"
        )
        self.assertEqual(
            form.cleaned_data["created_by"],
            self.user
        )

    def test_category_creation_form(self):
        """Test Category Creation Form"""

        self.user = get_user_model().objects.create_user(
            username="employee",
            password="passtestTEST123!",
            position="Employee"
        )
        self.knowledge_base = KnowledgeBase.objects.create(
            title="test_title",
            created_by=self.user,
        )

        form_data = {
            "topic": "test_topic",
            "knowledge_base": self.knowledge_base.id,
            "created_by": self.user.id,
        }
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["knowledge_base"],
            self.knowledge_base
        )
        self.assertEqual(
            form.cleaned_data["created_by"],
            self.user
        )

    def test_article_creation_form(self):
        """Test Article Creation Form"""

        self.user = get_user_model().objects.create_user(
            username="employee",
            password="passtestTEST123!",
            position="Employee"
        )
        self.knowledge_base = KnowledgeBase.objects.create(
            title="test_title",
            created_by=self.user,
        )
        self.category = Category.objects.create(
            topic="test_topic",
            created_by=self.user,
            knowledge_base=self.knowledge_base,
        )

        form_data = {
            "title": "test_title",
            "category": self.category.id,
            "author": self.user.id,
            "content": "test_content",
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["category"],  self.category)
        self.assertEqual(form.cleaned_data["author"], self.user)
        self.assertEqual(form.cleaned_data["content"], "test_content")

    def test_rating_form_valid_data(self):
        """Test RatingForm with valid data"""
        form_data = {"rating": 4}
        form = RatingForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["rating"], 4)

    def test_comment_form_valid_data(self):
        """Test CommentForm with valid data"""
        form_data = {"commentary": "This is a helpful comment."}
        form = CommentForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["commentary"],
            "This is a helpful comment."
        )


class SearchFormsTest(TestCase):
    """Test the search forms."""

    def test_knowledge_base_search_form_valid_data(self):
        """Test KnowledgeBaseSearchForm with valid data"""

        form_data = {"title": "Django Tutorial"}
        form = KnowledgeBaseSearchForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Django Tutorial")

    def test_category_search_form_valid_data(self):
        """Test CategorySearchForm with valid data"""

        form_data = {"topic": "Python Programming"}
        form = CategorySearchForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["topic"], "Python Programming")

    def test_article_search_form_valid_data(self):
        """Test ArticleSearchForm with valid data"""
        form_data = {"title": "How to use Django Forms"}
        form = ArticleSearchForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "How to use Django Forms")

    def test_employee_search_form_valid_data(self):
        """Test EmployeeSearchForm with valid data"""
        form_data = {"query": "John Doe"}
        form = EmployeeSearchForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], "John Doe")
