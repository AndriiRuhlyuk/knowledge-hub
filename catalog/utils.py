from django.db.models import Avg, Count, Q
from .models import Article, KnowledgeBase, Category, Employee, Comment


def get_site_statistics() -> dict[str, int]:
    """Return a dictionary of statistics about the current site."""

    return {
        "total_knowledge_bases": KnowledgeBase.objects.count(),
        "total_categories": Category.objects.count(),
        "total_articles": Article.objects.filter(is_published=True).count(),
        "total_employees": Employee.objects.count(),
        "total_comments": Comment.objects.count(),
        "active_authors": Employee.objects.filter(
            articles__is_published=True
        ).distinct().count(),
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
