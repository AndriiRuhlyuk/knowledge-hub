from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg


class KnowledgeBase(models.Model):
    """
    A model for organizing thematic knowledge bases.
    Each knowledge base can contain categories and articles.
    """

    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="knowledge base title"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created at"
    )


    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    A model for categories of articles within a knowledge base.
    Each category belongs to a specific KnowledgeBase.
    """

    topic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.PROTECT,
        related_name="categories",
    )

    class Meta:
        ordering = ["topic"]
        verbose_name = "category"
        verbose_name_plural = "categories"
        unique_together = ("topic", "knowledge_base")


    def __str__(self):
        return f"{self.knowledge_base.title} - {self.topic}"


class Employee(AbstractUser):
    """
    Employee model that inherits from AbstractUser.
    Extends the standard user model with additional fields.
    """

    project = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="project name",
    )

    position = models.CharField(
        max_length=255,
        verbose_name="position",
    )

    level = models.CharField(
        max_length=155,
        blank=True,
        verbose_name="level",
    )

    class Meta:
        ordering = ["username"]
        verbose_name = "employee"
        verbose_name_plural = "employees"

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def full_name(self):
        """Employee full name."""

        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def published_articles_count(self):
        """Number of articles published."""

        return self.articles.filter(is_published=True).count()

    @property
    def author_rating(self):
        """Rating of an author."""

        published_rating_articles = self.articles.filter(
            is_published=True,
            ratings__isnull=False,
        )

        aggregation_result = published_rating_articles.aggregate(
            avg_rating=Avg("ratings__rating"),
        )
        average_rating_value = aggregation_result["avg_rating"]

        return round(average_rating_value, 1) if average_rating_value else 0


class Article(models.Model):
    """
    Model for articles in the knowledge base.
    Each article belongs to a specific category and knowledge base.
    """

    title = models.CharField(
        max_length=255,
    )

    content = models.TextField()
    author = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="articles",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="articles",
    )

    is_published = models.BooleanField(default=False,)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reading_time = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        """Average rating for an article."""

        aggregation_result = self.ratings.aggregate(avg_rating=Avg("rating"))
        average_rating_value = aggregation_result["avg_rating"]
        return round(average_rating_value, 1) if average_rating_value else 0

    @property
    def rating_count(self):
        """Number of articles rated."""

        return self.ratings.count()

    @property
    def review_count(self):
        """Number of reviews for an article."""

        return self.comments.count()


    def increment_views(self):
        """Increment the views count"""

        self.views_count += 1
        self.save(update_fields=['views_count'])


class Rating(models.Model):
    """
    Model for article ratings.
    Each employee can give only ONE rating per article.
    """

    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Very Good"),
        (5, "5 - Excellent"),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES
    )

    class Meta:
        ordering = ["rating"]
        verbose_name = "rating"
        verbose_name_plural = "ratings"
        unique_together = ["article", "employee"]

    def __str__(self):
        return f"{self.employee.full_name} - {self.article.title} ({self.rating}/5)"


class Comment(models.Model):
    """
    Model for article reviews/comments.
    Employees can leave MULTIPLE reviews (comments) for articles.
    """

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    commentator = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    commentary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "review"
        verbose_name_plural = "reviews"

    def __str__(self):
        return f"{self.commentator.full_name} - {self.article.title}"
