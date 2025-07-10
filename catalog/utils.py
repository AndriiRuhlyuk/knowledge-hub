from django.db.models import Avg, Count, Q
from .models import Article, KnowledgeBase, Category, Employee, Comment


def get_site_statistics() -> dict[str, int]:
    """Return a dictionary of statistics about the current site."""

    data = KnowledgeBase.objects.aggregate(
        total_knowledge_bases=Count("id"),
        total_categories=Count("categories"),
    )
    articles_stats = Article.objects.aggregate(
        total_articles=Count("id", filter=Q(is_published=True)),
        total_comments=Count("comments"),
        total_authors=Count("author", filter=Q(is_published=True), distinct=True),
    )
    employee_count = Employee.objects.count()

    return {
        **data,
        **articles_stats,
        "total_employees": employee_count,
    }


def get_top_statistics()-> dict[str, any]:
    """Return most viewed, top-rated, most active author, and largest category."""
    return {
        "most_viewed_article": Article.objects.filter(
            is_published=True,
        ).select_related(
            "author", "category"
        ).order_by("-views_count").first(),

        "top_rated_article": Article.objects.filter(
            is_published=True,
            ratings__isnull=False,
        ).annotate(
            avg_rating=Avg("ratings__rating"),
        ).select_related(
            "author", "category"
        ).order_by("-avg_rating").first(),

        "most_active_author": Employee.objects.filter(
            articles__is_published=True,
        ).annotate(
            articles_count=Count(
                "articles",
                filter=Q(articles__is_published=True),
                distinct=True,
            )
        ).order_by("-articles_count").first(),

        "largest_category": Category.objects.annotate(
            articles_count=Count(
                "articles",
                filter=Q(articles__is_published=True),
                distinct=True,
            )
        ).order_by("-articles_count").first(),
    }
