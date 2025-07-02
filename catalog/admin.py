from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from catalog.models import KnowledgeBase, Article, Comment, Category, Rating, Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    """Admin configuration for Employee model."""

    list_display = UserAdmin.list_display + ("project", "position", "level",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "Employee information",
            {"fields": ("project", "position", "level",)}
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Employee information",
            {"fields": ("project", "position", "level",)}
        ),
    )
    list_filter = ("username", "position",)
    search_fields = ("username", "position", "first_name", "last_name",)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    """Admin configuration for KnowledgeBase model."""

    list_display = ("title", "created_at", "categories_count",)
    search_fields = ("title",)
    readonly_fields = ("created_at",)

    def categories_count(self, obj):
        """Number of categories in this knowledge base."""

        return obj.categories.count()
    categories_count.short_description = "categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""

    list_display = ("topic", "created_at", "articles_count")
    list_filter = ("topic", "created_at",)
    search_fields = ("topic", "knowledge_base__title")
    readonly_fields = ('created_at',)

    def articles_count(self, obj):
        """Number of articles in this category."""

        return obj.articles.count()
    articles_count.short_description = "articles"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for Article model."""

    list_display = (
        "title",
        "category",
        "author",
        "get_short_content",
        "is_published",
        "created_at",
        "views_count",
        "average_rating",
    )
    list_filter = (
        "is_published",
        "title",
        "author",
        "created_at",
        "views_count",
        "category",
    )
    search_fields = (
        "title",
        "author__username",
        "author__first_name",
        "author__last_name",
    )
    readonly_fields = (
        "created_at",
        "views_count",
        "average_rating",
        "rating_count",
        "comments_count",
        "updated_at",
    )

    fieldsets = (
        ("article Information", {
            "fields": ("title", "content", "author", "category")
        }),
        ("publishing", {
            "fields": ("is_published", "reading_time")
        }),
        ("timestamp", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
        ("statistics", {
            "fields": ("views_count", "comments_count", "average_rating"),
        })
    )
    actions = ["publish_articles", "unpublish_articles"]

    def get_short_content(self, obj):
        """Get shortened content for list display."""

        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    get_short_content.short_description = "Content"

    def publish_articles(self, request, queryset):
        """Publish selected articles."""

        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            f"{updated} articles were published."
        )
    publish_articles.short_description = "Publish selected articles"

    def unpublish_articles(self, request, queryset):
        """Unpublish selected articles."""

        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            f"{updated} articles were unpublished."
        )
    unpublish_articles.short_description = "Unpublish selected articles"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin configuration for Rating model."""
    list_display = (
        "article",
        "employee",
        "rating",
        "get_article_author",
    )
    list_filter = (
        "rating",
        "article",
        "article__category"
    )
    search_fields = (
        "article__title",
        "employee__username",
    )
    readonly_fields = ("article", "employee",)

    def get_article_author(self, obj):
        """Get article author."""
        return obj.article.author.full_name

    get_article_author.short_description = "Article Author"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model."""

    list_display = (
        "get_short_commentary",
        "article",
        "commentator",
        "created_at",
    )
    list_filter = (
        "commentator",
        "article",
        "created_at",
    )
    search_fields = (
        "commentator__username",
        "article__title",
        "commentary"
    )
    readonly_fields = ("created_at",)
    formfield_overrides = {
        "commentary": {"widget": admin.widgets.AdminTextareaWidget(
            attrs={"rows": 4, "columns": 60},
        )},
    }

    def get_short_commentary(self, obj):
        """Get shortened commentary for list display."""

        return obj.commentary[:50] + '...' if len(obj.commentary) > 50 else obj.commentary

    get_short_commentary.short_description = "Commentary"


admin.site.site_header = "Knowledge Hub Administration"
admin.site.site_title = "Knowledge Hub Admin"
admin.site.index_title = "Welcome to Knowledge Hub Administration"
