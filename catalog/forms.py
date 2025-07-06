from django import forms
from django.contrib.auth.models import User

from catalog.models import Rating, Comment, Employee

from django.contrib.auth.forms import UserCreationForm, UserChangeForm


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


class EmployeeRegistrationForm(UserCreationForm):
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
