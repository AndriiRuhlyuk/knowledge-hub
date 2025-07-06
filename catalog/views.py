from datetime import timedelta
from itertools import islice

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic, View

from catalog.forms import (
    KnowledgeBaseSearchForm,
    CategorySearchForm,
    ArticleSearchForm,
    RatingForm,
    CommentForm,
    EmployeeSearchForm,
    EmployeeUpdateForm, EmployeeRegistrationForm
)
from catalog.models import (
    KnowledgeBase,
    Article,
    Category,
    Employee,
    Rating,
    Comment
)
from catalog.utils import get_top_statistics, get_site_statistics


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
    return dict(islice(stats_dict.items(), skip, None))

class KnowledgeBaseListView(LoginRequiredMixin, generic.ListView):
    """Knowledge bases list page."""

    model = KnowledgeBase
    template_name = "catalog/knowledge_base_list.html"
    context_object_name = "knowledge_base_list"
    paginate_by = 3

    def get_queryset(self):
        queryset = KnowledgeBase.objects.all()
        form = KnowledgeBaseSearchForm(self.request.GET)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            if title:
                queryset = queryset.filter(
                    title__icontains=form.cleaned_data["title"]
                )

        return queryset.annotate(
            categories_count=Count("categories", distinct=True),
            articles_count=Count(
                "categories__articles",
                filter=Q(categories__articles__is_published=True),
                distinct=True
            )
        ).order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        title = self.request.GET.get("title", "")
        context["search_form"] = KnowledgeBaseSearchForm(
            initial={"title": title},
        )

        all_stats = get_site_statistics()
        context["site_stats"] = get_second_half_stats(all_stats)

        context["total_knowledge_bases"] = self.get_queryset().count()
        context["request"] = self.request
        return context


class KnowledgeBaseDetailsView(LoginRequiredMixin, generic.DetailView):
    """Knowledge base detail page with categories and articles."""

    model = KnowledgeBase
    template_name = "catalog/knowledge_base_detail.html"
    context_object_name = "knowledge_base_detail"

    def get_object(self):
        return get_object_or_404(
            KnowledgeBase.objects.prefetch_related(
                "categories__articles__author"
            ),
            pk=self.kwargs["pk"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knowledge_base = self.get_object()

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
                    articles__created_at__gte=timezone.now() - timedelta(days=7)
                ),
            )
        ).order_by("topic")
        return context


class CategoryListView(LoginRequiredMixin, generic.ListView):
    """Category list page."""

    model = Category
    template_name = "catalog/category_list.html"
    context_object_name = "category_list"
    paginate_by = 3

    def get_queryset(self):
        queryset = Category.objects.all()
        form = CategorySearchForm(self.request.GET)
        if form.is_valid():
            topic = form.cleaned_data.get("topic")
            if topic:
                queryset = queryset.filter(
                    topic__icontains=form.cleaned_data["topic"]
                )

        return queryset.annotate(
            articles_count=Count("articles", distinct=True),
            authors_count=Count(
                "articles__author",
                filter=Q(articles__is_published=True),
                distinct=True
            )
        ).order_by("topic")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        topic = self.request.GET.get("topic", "")
        context["search_form"] = CategorySearchForm(
            initial={"topic": topic},
        )

        context["total_categories"] = self.get_queryset().count()
        context["request"] = self.request
        return context


class CategoriesByKnowledgeBaseView(LoginRequiredMixin, generic.ListView):
    """Categories by knowledge base view."""

    model = Category
    template_name = "catalog/categories_by_kb.html"
    context_object_name = "categories"
    paginate_by = 1

    def get_queryset(self):
        self.knowledge_base_by_kb = get_object_or_404(KnowledgeBase, pk=self.kwargs["pk"])
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


class CategoryDetailsView(LoginRequiredMixin, generic.DetailView):
    """Category detail page."""

    model = Category
    template_name = "catalog/category_detail.html"
    context_object_name = "category_detail"

    def get_object(self):
        self.cat = get_object_or_404(
            Category.objects.prefetch_related(
                "articles__author"
            ),
            pk=self.kwargs["pk"],
        )
        return self.cat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.cat

        articles = category.articles.filter(is_published=True).select_related("author")

        context["articles"] = articles

        context["authors_count"] = articles.values("author").distinct().count()

        context["reading_time_sum"] = articles.aggregate(total=Count("reading_time"))["total"]
        return context


class ArticleListView(LoginRequiredMixin, generic.ListView):
    """Article list page."""

    model = Article
    template_name = "catalog/article_list.html"
    context_object_name = "article_list"
    paginate_by = 3

    def get_queryset(self):
        queryset = Article.objects.all()
        form = ArticleSearchForm(self.request.GET)
        if form.is_valid():
            topic = form.cleaned_data.get("title")
            if topic:
                queryset = queryset.filter(
                    title__icontains=form.cleaned_data["title"]
                )
        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        title = self.request.GET.get("title", "")
        context["search_form"] = ArticleSearchForm(
            initial={"title": title},
        )

        context["total_articles"] = self.get_queryset().count()
        return context


class ArticleByCategoryView(LoginRequiredMixin, generic.ListView):
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


class AuthorsByCategoryView(LoginRequiredMixin, generic.ListView):
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


class ArticleDetailsView(LoginRequiredMixin, generic.DetailView):
    model = Article
    template_name = "catalog/article_detail.html"
    context_object_name = "article_detail"

    def get_queryset(self):
        return Article.objects.prefetch_related(
            "comments", "ratings", "comments__commentator"
        ).select_related("author", "category")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        employee = self.request.user

        context["comments"] = article.comments.all()
        context["average_rating"] = article.average_rating
        context["rating_count"] = article.rating_count

        context["comment_form"] = CommentForm()
        context["rating_form"] = RatingForm()

        context["user_rating"] = Rating.objects.filter(article=article, employee=employee).first()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        article = self.get_object()
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
                rating, created = Rating.objects.update_or_create(
                    article=article,
                    employee=employee,
                    defaults={"rating": rating_value}
                )
                messages.success(request, "Your rating has been submitted.")
            else:
                messages.error(request, "Rating could not be submitted.")

        return redirect("catalog:article-detail", pk=article.pk)


class EmployeesListView(LoginRequiredMixin, generic.ListView):
    model = Employee
    template_name = "catalog/employees_list.html"
    context_object_name = "employee_list"
    paginate_by = 3

    def get_queryset(self):
        queryset = Employee.objects.annotate(
            published_articles_total =Count(
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


class EmployeeDetailsView(LoginRequiredMixin, generic.DetailView):
    model = Employee
    template_name = "catalog/employee_detail.html"
    context_object_name = "employee_detail"

    def get_object(self):
        self.emp = get_object_or_404(
            Employee.objects.prefetch_related(
                "articles__category__knowledge_base"
            ),
            pk=self.kwargs["pk"],
        )
        return self.emp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employer = self.emp

        articles = employer.articles.filter(is_published=True).select_related("author")
        context["articles"] = articles.order_by("-created_at")
        context["articles_count"] = articles.count()
        context["average_rating"] = articles.aggregate(avg=Avg("ratings__rating"))["avg"]
        return context


class CommentaryUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    model = Comment
    fields = ["commentary"]
    template_name = "catalog/comment_form.html"

    def get_success_url(self):
        return reverse("catalog:article-detail", kwargs={"pk": self.kwargs["article_pk"]})

    def test_func(self):
        comment = self.get_object()
        return comment.commentator == self.request.user

class CommentaryDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    model = Comment
    template_name = "catalog/comment_confirm_delete.html"

    def get_success_url(self):
        return reverse("catalog:article-detail", kwargs={"pk": self.kwargs["article_pk"]})

    def test_func(self):
        comment = self.get_object()
        return comment.commentator == self.request.user


class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "catalog/employee_form.html"

    def get_success_url(self):
        return reverse("catalog:employee-detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        return self.request.user.pk == self.get_object().pk


class EmployeeDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    model = Employee
    template_name = "catalog/employee_confirm_delete.html"
    success_url = reverse_lazy("catalog:employee-list")

    def test_func(self):
        return self.request.user.is_superuser

class RegisterView(View):
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

