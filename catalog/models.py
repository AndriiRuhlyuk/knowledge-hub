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

    short_description = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="knowledge_bases",
        verbose_name="created_by",
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
    created_by = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="created_by",
    )

    class Meta:
        ordering = ["topic"]
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=["topic", "knowledge_base"],
                name="unique_category_per_kb"
            )
        ]

    def __str__(self):
        return f"{self.topic}"


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
        return self.full_name

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

        aggregation_result = self.articles.filter(
            is_published=True,
            ratings__isnull=False,
        ).aggregate(
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

    def save(self, *args, **kwargs):
        """Auto-calculate reading time based on content length."""

        word_count = len(self.content.split())
        self.reading_time = max(1, word_count // 60)
        super().save(*args, **kwargs)


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
        constraints = [
            models.UniqueConstraint(
                fields=["article", "employee"],
                name="unique_rating_per_article_employee"
            )
        ]

    def __str__(self):
        return (f"{self.employee.full_name} - "
                f"{self.article.title} ({self.rating}/5)")


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
