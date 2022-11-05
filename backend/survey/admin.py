from django.contrib import admin
from django.forms import Textarea
from django.db.models.fields import TextField

from .models import Survey, Question, QuestionChoice, Answer


# =====================================================================


class _FlatText(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 60})},
    }


class _FlatTextInline(admin.StackedInline):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }


# =====================================================================


class QuestionInline(_FlatTextInline):
    model = Question
    fields = (("name", "order", "type"), )
    extra = 0


class QuestionChoiceInline(_FlatTextInline):
    model = QuestionChoice
    fields = (("name", "order"), )
    extra = 0


# =====================================================================


@admin.register(Survey)
class SurveyAdmin(_FlatText):
    fields = (
        "name",
        "description",
        ("date_start", "date_end"),
    )
    inlines = [QuestionInline, ]


@admin.register(Question)
class QuestionAdmin(_FlatText):
    fields = (
        ("survey", "order", "type"),
        "name",
    )
    inlines = [QuestionChoiceInline, ]


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(_FlatText):
    fields = (
        ("question", "order"),
        "name",
    )


@admin.register(Answer)
class AnswerAdmin(_FlatText):
    fields = (
        ("user", "question"),
        ("text", "choice"),
    )
