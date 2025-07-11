from django.test import TestCase

from django.contrib.auth import get_user_model

from catalog.models import KnowledgeBase, Category, Article, Comment
from catalog.utils import get_site_statistics, get_top_statistics


class UtilsTests(TestCase):
    """Test the utility functions."""

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
        self.article_1 = Article.objects.create(
            title="BMW",
            author=self.user,
            category=self.category,
            content="This is a article about BMW.",
            is_published=True,
            views_count=1
        )

        self.article_2 = Article.objects.create(
            title="AUDI",
            content="This is a article about AUDI.",
            author=self.user,
            category=self.category,
            is_published=True,
            views_count=5
        )

        self.comment = Comment.objects.create(
            article=self.article_1,
            commentator=self.user,
            commentary="Helpful!"
        )

        self.article_1.ratings.create(employee=self.user, rating=5)
        self.article_2.ratings.create(employee=self.user, rating=3)

    def test_get_site_statistics(self):
        stats = get_site_statistics()
        self.assertEqual(stats["total_knowledge_bases"], 1)
        self.assertEqual(stats["total_categories"], 1)
        self.assertEqual(stats["total_articles"], 2)
        self.assertEqual(stats["total_comments"], 1)
        self.assertEqual(stats["total_employees"], 1)
        self.assertEqual(stats["total_authors"], 1)

    def test_get_top_statistics(self):
        stats = get_top_statistics()

        self.assertEqual(stats["most_viewed_article"], self.article_2)
        self.assertEqual(stats["top_rated_article"], self.article_1)
        self.assertEqual(stats["most_active_author"], self.user)
        self.assertEqual(stats["largest_category"], self.category)
