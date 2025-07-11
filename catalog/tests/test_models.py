from django.test import TestCase

from catalog.models import (
    KnowledgeBase,
    Employee,
    Category,
    Article,
    Rating,
    Comment
)


class ModelsTests(TestCase):
    """Models tests."""

    def setUp(self):
        """Set up test data."""
        self.employee = Employee.objects.create(
            username="test",
            first_name="first_name",
            last_name="last_name",
            position="position",
            password="123password",
            level="senior",
            project="KYC"
        )

    def test_knowledgebase_str(self):

        knowledgebase = KnowledgeBase.objects.create(
            title="test",
            created_by=self.employee,
        )
        self.assertEqual(str(knowledgebase), "test")

    def test_category_str(self):
        knowledge_base = KnowledgeBase.objects.create(
            title="test_kb",
            created_by=self.employee,
        )
        category = Category.objects.create(
            topic="test_c",
            created_by=self.employee,
            knowledge_base=knowledge_base,
        )
        self.assertEqual(str(category), "test_c")

    def test_article_str(self):
        knowledge_base = KnowledgeBase.objects.create(
            title="test_kb",
            created_by=self.employee,
        )
        category = Category.objects.create(
            topic="test_name_c",
            created_by=self.employee,
            knowledge_base=knowledge_base,
        )
        article = Article.objects.create(
            title="test_a",
            content="test_content",
            category=category,
            author=self.employee,
        )
        self.assertEqual(str(article), "test_a")

    def test_employee_str(self):
        employee = self.employee

        self.assertEqual(str(employee), employee.full_name)

    def test_rating_str(self):
        knowledge_base = KnowledgeBase.objects.create(
            title="test_kb",
            created_by=self.employee,
        )
        category = Category.objects.create(
            topic="test_name_c",
            created_by=self.employee,
            knowledge_base=knowledge_base,
        )
        article = Article.objects.create(
            title="test_a",
            category=category,
            author=self.employee,
        )
        rating = Rating.objects.create(
            article=article,
            employee=self.employee,
            rating=5,
        )
        self.assertEqual(
            str(rating),
            f"{rating.employee.full_name} "
            f"- {rating.article.title} ({rating.rating}/5)")

    def test_comment_str(self):
        knowledge_base = KnowledgeBase.objects.create(
            title="test_kb",
            created_by=self.employee,
        )
        category = Category.objects.create(
            topic="test_name_c",
            created_by=self.employee,
            knowledge_base=knowledge_base,
        )
        article = Article.objects.create(
            title="test_a",
            category=category,
            author=self.employee,
        )
        comment = Comment.objects.create(
            article=article,
            commentator=self.employee,
            commentary="tets - test"
        )
        self.assertEqual(
            str(comment),
            f"{comment.commentator.full_name} - "
            f"{comment.article.title}")

    def test_employee_with_level_and_project(self):
        employee = self.employee

        self.assertEqual(employee.project, "KYC")
        self.assertEqual(employee.level, "senior")

    def test_article_reading_time(self):
        content = "a " * 360
        knowledge_base = KnowledgeBase.objects.create(
            title="test_kb",
            created_by=self.employee,
        )
        category = Category.objects.create(
            topic="test_name_c",
            created_by=self.employee,
            knowledge_base=knowledge_base,
        )
        article = Article.objects.create(
            title="test_a",
            content=content,
            category=category,
            author=self.employee,
        )

        self.assertEqual(article.reading_time, 6)

    def test_employee_author_rating(self):
        rating_1 = 3
        rating_2 = 5

        employee = self.employee
        knowledge_base = KnowledgeBase.objects.create(
            title="test_kb",
            created_by=employee,
        )
        category = Category.objects.create(
            topic="test_name_c",
            created_by=employee,
            knowledge_base=knowledge_base,
        )
        article_first = Article.objects.create(
            title="test_a_f",
            category=category,
            author=employee,
            is_published=True,
        )

        article_second = Article.objects.create(
            title="test_a_s",
            category=category,
            author=employee,
            is_published=True,
        )
        Rating.objects.create(
            article=article_first,
            employee=employee,
            rating=rating_1,
        )

        Rating.objects.create(
            article=article_second,
            employee=employee,
            rating=rating_2,
        )

        self.assertEqual(employee.author_rating, 4)
