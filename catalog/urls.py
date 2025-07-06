from django.urls import path, reverse_lazy

from django.contrib.auth import views as auth_views

from catalog.views import (
    HomeView,
    KnowledgeBaseListView,
    KnowledgeBaseDetailsView,
    CategoryListView,
    CategoriesByKnowledgeBaseView,
    EmployeeDetailsView,
    CategoryDetailsView,
    ArticleListView,
    ArticleByCategoryView,
    AuthorsByCategoryView,
    ArticleDetailsView,
    CommentaryUpdateView,
    CommentaryDeleteView,
    EmployeesListView,
    EmployeeUpdateView,
    EmployeeDeleteView,
    RegisterView,
)



urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("knowledge_list", KnowledgeBaseListView.as_view(), name="knowledge-list"),
    path("knowledge_base/<int:pk>/", KnowledgeBaseDetailsView.as_view(), name="knowledge-base-detail"),
    path("knowledge_base/<int:pk>/category_list/", CategoriesByKnowledgeBaseView.as_view(), name="kb-categories"),

    path("category_list", CategoryListView.as_view(), name="category-list"),
    path("category/<int:pk>/", CategoryDetailsView.as_view(), name="category-detail"),
    path("category/<int:pk>/article_list/", ArticleByCategoryView.as_view(), name="c-articles"),
    path("category/<int:pk>/author_list/", AuthorsByCategoryView.as_view(), name="c-authors"),


    path("article_list", ArticleListView.as_view(), name="article-list"),
    path("article/<int:pk>/", ArticleDetailsView.as_view(), name="article-detail"),
    path(
        "article/<int:article_pk>/comment/<int:pk>/update/",
        CommentaryUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "article/<int:article_pk>/comment/<int:pk>/delete/",
        CommentaryDeleteView.as_view(),
        name="comment-delete",
    ),

    path("employee_list/", EmployeesListView.as_view(), name="employee-list"),
    path("employee/<int:pk>/", EmployeeDetailsView.as_view(), name="employee-detail"),
    path("employee/<int:pk>/update/", EmployeeUpdateView.as_view(), name="employee-update"),
    path("employee/<int:pk>/delete/", EmployeeDeleteView.as_view(), name="employee-delete"),
    path("register/", RegisterView.as_view(), name="register"),

    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change_form.html",
        success_url=reverse_lazy("catalog:password-change-done")
    ), name="password-change"),

    path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html"
    ), name="password-change-done"),
]

app_name = "catalog"