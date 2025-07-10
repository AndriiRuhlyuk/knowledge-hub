from django import forms
from django.contrib.auth.models import User

from catalog.models import Rating, Comment, Employee, KnowledgeBase, Category, Article

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_select2.forms import ModelSelect2Widget


class KnowledgeBaseSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by title",
            "class": "form-control",

        }),
    )


class CategorySearchForm(forms.Form):
    topic = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by topic",
            "class": "form-control",

        }),
    )


class ArticleSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by title",
            "class": "form-control",

        }),
    )


class EmployeeSearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by name",
            "class": "form-control",
        })
    )


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating"]
        widgets = {
            "rating": forms.RadioSelect(choices=Rating.RATING_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].empty_label = None


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["commentary"]
        labels = {"commentary": ""}
        widgets = {

            "commentary": forms.Textarea(attrs={
                "placeholder": "Comment text",
                "class": "form-control",
                "rows": 2,
            })
        }


class EmployeeUpdateForm(UserChangeForm):
    class Meta:
        model = Employee
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "level",
            "project",
            "position"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "password" in self.fields:
            self.fields.pop("password")

        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "")

            if isinstance(widget, forms.RadioSelect):
                widget.attrs["class"] = f"{existing_classes} form-check-input border border-dark".strip()

            else:
                widget.attrs["class"] = f"{existing_classes} form-control border border-dark".strip()


class EmployeeRegistrationForm(UserCreationForm):
    """
    Registration form for Employee model with:
    - required email field
    - border-design for every field
    - email validation
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = Employee
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "project",
            "position",
            "level",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "")

            if isinstance(widget, forms.RadioSelect):
                widget.attrs["class"] = f"{existing_classes} form-check-input border border-dark".strip()

            else:
                widget.attrs["class"] = f"{existing_classes} form-control border border-dark".strip()

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Employee.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class KnowledgeBaseForm(forms.ModelForm):
    created_by = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.RadioSelect
    )

    class Meta:
        model = KnowledgeBase
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "")

            if isinstance(widget, forms.RadioSelect):
                widget.attrs["class"] = f"{existing_classes} form-check-input border border-dark".strip()

            else:
                widget.attrs["class"] = f"{existing_classes} form-control border border-dark".strip()


class CategoryForm(forms.ModelForm):
    knowledge_base = forms.ModelChoiceField(
        queryset=KnowledgeBase.objects.all(),
        widget=forms.RadioSelect
    )
    created_by = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.RadioSelect
    )

    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "")

            if isinstance(widget, forms.RadioSelect):
                widget.attrs["class"] = f"{existing_classes} form-check-input border border-dark".strip()

            else:
                widget.attrs["class"] = f"{existing_classes} form-control border border-dark".strip()


class ArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().none(),
        widget=forms.RadioSelect
    )


    class Meta:
        model = Article
        fields = ("title", "content", "category", "author")
        widgets = {
            "author": ModelSelect2Widget(
                search_fields=["first_name__icontains", "last_name__icontains"],
                attrs={
                    "class": "form-control border border-dark",
                    "data-minimum-input-length": 1,
                    "data-placeholder": "Start input name..."
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "")

            if isinstance(widget, forms.RadioSelect):
                widget.attrs["class"] = f"{existing_classes} form-check-input border border-dark".strip()

            else:
                widget.attrs["class"] = f"{existing_classes} form-control border border-dark".strip()
