from datetime import timedelta
from itertools import islice

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Avg, F, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.views import generic, View

from catalog.forms import (
    KnowledgeBaseSearchForm,
    CategorySearchForm,
    ArticleSearchForm,
    RatingForm,
    CommentForm,
    EmployeeSearchForm,
    EmployeeUpdateForm,
    EmployeeRegistrationForm,
    KnowledgeBaseForm,
    CategoryForm,
    ArticleForm
)
from catalog.models import (
    KnowledgeBase,
    Article,
    Category,
    Employee,
    Rating,
    Comment
)
from catalog.utils import (
    get_top_statistics,
    get_site_statistics
)


class HomeView(LoginRequiredMixin, generic.TemplateView):
    """Home page with general statistics and top content."""

    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Knowledge Hub"

        all_stats = get_site_statistics()

        context["site_stats"] = dict(islice(all_stats.items(), 3))
        context["top_stats"] = get_top_statistics()

        return context


def get_second_half_stats(stats_dict, skip=3):
    """General statistics about employees, comments, authors"""
    return dict(islice(stats_dict.items(), skip, None))


class KnowledgeBaseListView(
    LoginRequiredMixin,
    generic.ListView
):
    """Knowledge bases list page."""

    model = KnowledgeBase
    template_name = "catalog/knowledge_base_list.html"
    context_object_name = "knowledge_base_list"
    paginate_by = 3

    @cached_property
    def search_form(self):
        return KnowledgeBaseSearchForm(self.request.GET or None)

    @cached_property
    def filtered_queryset(self):
        queryset = KnowledgeBase.objects.all()

        if self.search_form.is_valid():
            title = self.search_form.cleaned_data.get("title")
            if title:
                queryset = queryset.filter(title__icontains=title)

        return queryset.annotate(
            categories_count=Count("categories", distinct=True),
            articles_count=Count(
                "categories__articles",
                filter=Q(categories__articles__is_published=True),
                distinct=True
            )
        ).order_by("title")

    def get_queryset(self):
        return self.filtered_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        title = self.request.GET.get("title", "")
        context["search_form"] = KnowledgeBaseSearchForm(
            initial={"title": title},
        )

        all_stats = get_site_statistics()
        context["site_stats"] = get_second_half_stats(all_stats)

        context["total_knowledge_bases"] = all_stats["total_knowledge_bases"]
        context["request"] = self.request
        return context


class KnowledgeBaseDetailsView(
    LoginRequiredMixin,
    generic.DetailView
):
    """Knowledge base detail page with categories and articles."""

    model = KnowledgeBase
    template_name = "catalog/knowledge_base_detail.html"
    context_object_name = "knowledge_base_detail"

    @cached_property
    def object_with_prefetch(self, queryset=None):

        return get_object_or_404(
            KnowledgeBase.objects.select_related(
                "created_by"
            ).prefetch_related(
                "categories__articles__author"
            ),
            pk=self.kwargs["pk"],
        )

    def get_object(self, queryset=None):
        return self.object_with_prefetch

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knowledge_base = self.object_with_prefetch

        context["categories"] = knowledge_base.categories.annotate(
            total_articles=Count("articles"),
            articles_count=Count(
                "articles",
                filter=Q(articles__is_published=True),
            ),
            recent_articles_count=Count(
                "articles",
                filter=Q(
                    articles__is_published=True,
                    articles__created_at__gte=timezone.now() - timedelta(
                        days=7
                    )
                ),
            )
        ).order_by("topic")
        return context


class KnowledgeBaseCreateView(
    LoginRequiredMixin,
    generic.CreateView
):
    """Knowledge Base create page."""

    model = KnowledgeBase
    form_class = KnowledgeBaseForm
    template_name = "catalog/knowledge_base_form.html"
    success_url = reverse_lazy("catalog:knowledge-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class KnowledgeBaseUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    """Knowledge Base update page."""

    model = KnowledgeBase
    form_class = KnowledgeBaseForm
    template_name = "catalog/knowledge_base_form.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def get_success_url(self):
        return reverse(
            "catalog:knowledge-base-detail",
            kwargs={"pk": self.get_object().pk}
        )

    def test_func(self):
        knowledge_base = self.get_object()
        user = self.request.user

        return knowledge_base.created_by == user or user.is_superuser


class KnowledgeBaseDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """Knowledge Base delete view."""

    model = KnowledgeBase
    template_name = "catalog/knowledge_base_delete_confirm.html"
    success_url = reverse_lazy("catalog:knowledge-list")

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def test_func(self):
        user = self.request.user
        knowledge_base = self.get_object()

        return (
                knowledge_base.created_by == user or user.is_superuser
        ) and not knowledge_base.categories.exists()

    def handle_no_permission(self):
        messages.error(
            self.request,
            "You can only delete empty knowledge bases that you created."
        )
        return redirect(
            "catalog:knowledge-base-detail",
            pk=self._object.pk
        )


class CategoriesByKnowledgeBaseView(
    LoginRequiredMixin,
    generic.ListView
):
    """Categories by knowledge base view."""

    model = Category
    template_name = "catalog/categories_by_kb.html"
    context_object_name = "categories"
    paginate_by = 1

    def get_queryset(self):
        self.knowledge_base_by_kb = get_object_or_404(
            KnowledgeBase, pk=self.kwargs["pk"]
        )
        return Category.objects.filter(
            knowledge_base=self.knowledge_base_by_kb
        ).annotate(
            authors_count=Count(
                "articles__author",
                filter=Q(articles__is_published=True),
                distinct=True
            ),
            articles_count=Count(
                "articles",
                filter=Q(articles__is_published=True),
                distinct=True
            ),
            comments_count=Count(
                "articles__comments",
                filter=Q(articles__is_published=True),
                distinct=True
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["knowledge_base"] = self.knowledge_base_by_kb
        return context


class CategoryListView(
    LoginRequiredMixin,
    generic.ListView
):
    """Category list page."""

    model = Category
    template_name = "catalog/category_list.html"
    context_object_name = "category_list"
    paginate_by = 3

    @cached_property
    def search_form(self):
        return CategorySearchForm(self.request.GET or None)

    @cached_property
    def filtered_queryset(self):
        queryset = Category.objects.all()

        if self.search_form.is_valid():
            topic = self.search_form.cleaned_data.get("topic")
            if topic:
                queryset = queryset.filter(topic__icontains=topic)

        return queryset.annotate(
            articles_count=Count("articles", distinct=True),
            authors_count=Count(
                "articles__author",
                filter=Q(articles__is_published=True),
                distinct=True
            )
        ).order_by("topic")

    def get_queryset(self):
        return self.filtered_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["search_form"] = self.search_form
        context["total_articles"] = context["page_obj"].paginator.count
        context["request"] = self.request
        return context


class CategoryDetailsView(
    LoginRequiredMixin,
    generic.DetailView
):
    """Category detail page."""

    model = Category
    template_name = "catalog/category_detail.html"
    context_object_name = "category_detail"

    def get_object(self, queryset=None):
        self.cat = get_object_or_404(
            Category.objects.select_related("created_by").prefetch_related(
                "articles__author"
            ),
            pk=self.kwargs["pk"],
        )
        return self.cat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.cat

        articles = category.articles.filter(
            is_published=True
        ).select_related("author")

        context["articles"] = articles
        context["reading_time_sum"] = articles.aggregate(
            total=Count("reading_time")
        )["total"]
        return context


class CategoryCreateView(
    LoginRequiredMixin,
    generic.CreateView
):
    """Category create page."""

    model = Category
    form_class = CategoryForm
    template_name = "catalog/category_form.html"
    success_url = reverse_lazy("catalog:category-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    """Category update page."""

    model = Category
    form_class = CategoryForm
    template_name = "catalog/category_form.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def get_success_url(self):
        return reverse_lazy(
            "catalog:category-detail",
            kwargs={"pk": self.get_object().pk}
        )

    def test_func(self):
        category = self.get_object()
        user = self.request.user

        return category.created_by == user or user.is_superuser


class CategoryDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """Category delete view."""

    model = Category
    template_name = "catalog/catalog_delete_confirm.html"
    success_url = reverse_lazy("catalog:category-list")

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def test_func(self):
        user = self.request.user
        category = self.get_object()

        return (
                category.created_by == user or user.is_superuser
        ) and not category.articles.exists()

    def handle_no_permission(self):
        messages.error(
            self.request,
            "You can only delete empty category that you created."
        )
        return redirect(
            "catalog:category-detail",
            pk=self.get_object().pk
        )


class ArticleByCategoryView(
    LoginRequiredMixin,
    generic.ListView
):
    """Articles in current category."""
    model = Article
    template_name = "catalog/articles_by_category.html"
    context_object_name = "articles_by_category"
    paginate_by = 1

    def get_queryset(self):
        self.cat = get_object_or_404(Category, pk=self.kwargs["pk"])
        return Article.objects.filter(
            category=self.cat,
            is_published=True,
        ).select_related("author").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.cat
        return context


class AuthorsByCategoryView(
    LoginRequiredMixin,
    generic.ListView
):
    """Authors in current category."""
    model = Employee
    template_name = "catalog/authors_by_category.html"
    context_object_name = "authors_by_category"
    paginate_by = 1

    def get_queryset(self):
        self.cat = get_object_or_404(Category, pk=self.kwargs["pk"])
        return Employee.objects.filter(
            articles__category=self.cat,
            articles__is_published=True,
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.cat
        return context


class ArticleDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """Article delete view."""

    model = Article
    template_name = "catalog/article_delete_confirm.html"
    context_object_name = "article"
    success_url = reverse_lazy("catalog:article-list")

    def get_queryset(self):
        return Article.objects.select_related("author")

    def get_object(self, queryset=None):
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def test_func(self):
        article = self.get_object()
        return (article.author == self.request.user or
                self.request.user.is_superuser)

    def handle_no_permission(self):
        messages.error(
            self.request,
            "You can only delete article that you created."
        )
        return redirect(
            "catalog:category-detail",
            pk=self.get_object().pk
        )


class ArticleListView(
    LoginRequiredMixin,
    generic.ListView
):
    """Article list page."""

    model = Article
    template_name = "catalog/article_list.html"
    context_object_name = "article_list"
    paginate_by = 3

    @cached_property
    def search_form(self):
        return ArticleSearchForm(self.request.GET or None)

    @cached_property
    def filtered_queryset(self):
        queryset = (
            Article.objects
            .select_related("author", "category")
            .annotate(
                avg_rating=Avg("ratings__rating"),
                comments_count=Count("comments")
            )
        )

        if self.search_form.is_valid():
            title = self.search_form.cleaned_data.get("title")
            if title:
                queryset = queryset.filter(title__icontains=title)

        return queryset.order_by("-created_at")

    def get_queryset(self):
        return self.filtered_queryset

    def get_context_data(self, **kwargs):
        """For use 'count' ones  + search form in template context"""
        context = super().get_context_data(**kwargs)
        context["search_form"] = self.search_form
        context["total_articles"] = context["page_obj"].paginator.count
        return context


class ArticleDetailsView(
    LoginRequiredMixin,
    generic.DetailView
):
    """Article details page."""
    model = Article
    template_name = "catalog/article_detail.html"
    context_object_name = "article_detail"

    def get_queryset(self):
        return (
            Article.objects.select_related(
                "author", "category", "category__knowledge_base"
            ).prefetch_related(
                "ratings", "comments__commentator"
            ).annotate(
                average_rating=Avg("ratings__rating"),
                rating_count=Count("ratings"),
                comments_total=Count("comments"))
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Article.objects.filter(
            pk=obj.pk
        ).update(views_count=F("views_count") + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        employee = self.request.user

        user_rating = article.ratings.filter(
            employee=employee
        ).first()

        context["comments"] = article.comments.all()
        context["comment_form"] = CommentForm()
        context["rating_form"] = RatingForm()
        context["rating_info"] = {
            "average_rating": round(article.average_rating or 0, 1),
            "rating_count": article.rating_count
        }
        context["user_rating"] = user_rating
        context["comments_total"] = article.comments_total

        return context

    def post(self, request, *args, **kwargs):
        """Comment create and rating submit method."""
        self.object = self.get_object()
        article = self.object
        employee = request.user

        if "submit_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.article = article
                comment.commentator = employee
                comment.save()
                messages.success(request, "Your comment has been submitted.")
            else:
                messages.error(request, "Comment could not be posted.")

        if "submit_rating" in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating_value = rating_form.cleaned_data["rating"]
                Rating.objects.update_or_create(
                    article=article,
                    employee=employee,
                    defaults={"rating": rating_value}
                )
                messages.success(request, "Your rating has been submitted.")
            else:
                messages.error(request, "Rating could not be submitted.")

        return redirect("catalog:article-detail", pk=article.pk)


class ArticleUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    """Article create page."""

    model = Article
    form_class = ArticleForm
    template_name = "catalog/article_form.html"

    def get_queryset(self):
        return Article.objects.select_related("author")

    def get_object(self, queryset=None):
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def get_success_url(self):
        return reverse_lazy(
            "catalog:article-detail",
            kwargs={"pk": self.get_object().pk}
        )

    def test_func(self):
        article = self.get_object()
        user = self.request.user

        return article.author == user or user.is_superuser


class ArticleCreateView(
    LoginRequiredMixin,
    generic.CreateView
):
    """Article create page."""

    model = Article
    form_class = ArticleForm
    template_name = "catalog/article_form.html"
    success_url = reverse_lazy("catalog:article-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["author"].queryset = Employee.objects.all()
        form.fields["category"].queryset = Category.objects.order_by("topic")
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CommentaryUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    """Comment can be updated by commentator"""
    model = Comment
    fields = ["commentary"]
    template_name = "catalog/comment_form.html"

    def get_success_url(self):
        return reverse(
            "catalog:article-detail",
            kwargs={"pk": self.kwargs["article_pk"]}
        )

    def test_func(self):
        comment = self.get_object()
        return comment.commentator == self.request.user


class CommentaryDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """Comment can be deleted by commentator on Article detail page."""
    model = Comment
    template_name = "catalog/comment_confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "catalog:article-detail",
            kwargs={"pk": self.kwargs["article_pk"]}
        )

    def test_func(self):
        comment = self.get_object()
        return comment.commentator == self.request.user


class EmployeesListView(
    LoginRequiredMixin,
    generic.ListView
):
    """
    Page for listing employees,
    with search on Name and Surname and
    filtering by publishing articles (author or employee).
    """
    model = Employee
    template_name = "catalog/employees_list.html"
    context_object_name = "employee_list"
    paginate_by = 3

    def get_queryset(self):
        queryset = Employee.objects.annotate(
            published_articles_total=Count(
                "articles", filter=Q(
                    articles__is_published=True,
                )
            )
        )

        filter_type = self.request.GET.get("filter")

        if filter_type == "authors":
            queryset = queryset.filter(published_articles_total__gt=0)

        form = EmployeeSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            if query:
                queryset = queryset.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query)
                )
        return queryset.order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["filter"] = self.request.GET.get("filter", "all")
        context["search_form"] = EmployeeSearchForm(self.request.GET)
        return context


class EmployeeDetailsView(
    LoginRequiredMixin,
    generic.DetailView
):
    """
    Detail view for an employee with info from
    related tables.
    """

    model = Employee
    template_name = "catalog/employee_detail.html"
    context_object_name = "employee_detail"

    def get_queryset(self):
        return (
            Employee.objects
            .prefetch_related(
                Prefetch(
                    "articles",
                    queryset=Article.objects.select_related(
                        "category", "category__knowledge_base"
                    ).annotate(
                        avg_rating=Avg("ratings__rating")
                    )
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employer = self.object

        published_articles = [
            article for article in employer.articles.all()
            if article.is_published
        ]

        context["articles"] = sorted(
            published_articles, key=lambda a: a.created_at, reverse=True
        )
        context["articles_count"] = len(published_articles)
        context["average_rating"] = round(
            sum(
                a.avg_rating or 0 for a in published_articles
            ) / len(published_articles),
            1
        ) if published_articles else None

        return context


class EmployeeUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    """
    View for updating an employee,
    with validation of user.
    """
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "catalog/employee_form.html"

    def get_object(self, queryset=None):
        if hasattr(self, "_cached_object"):
            return self._cached_object
        self._cached_object = super().get_object(queryset)
        return self._cached_object

    def get_success_url(self):
        return reverse(
            "catalog:employee-detail",
            kwargs={"pk": self.get_object().pk}
        )

    def test_func(self):
        return self.request.user.pk == self.get_object().pk


class EmployeeDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """
    Delete an employee (validate: delete can admin)
    """
    model = Employee
    template_name = "catalog/employee_confirm_delete.html"
    success_url = reverse_lazy("catalog:employee-list")

    def test_func(self):
        return self.request.user.is_superuser


class RegisterView(View):
    """
    Registration view
    with API methods: Get and Post
    for Django (to render template with right method)
    """
    def get(self, request):
        form = EmployeeRegistrationForm()
        return render(request, "registration/register.html", {"form": form})

    def post(self, request):
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("catalog:home")
        return render(request, "registration/register.html", {"form": form})
