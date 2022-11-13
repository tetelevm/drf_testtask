from django.contrib import admin
from django.forms import Textarea
from django.db.models.fields import TextField

from .models import SurveyModel, QuestionModel, QuestionChoiceModel, AnswerModel


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
    model = QuestionModel
    fields = (("name", "order", "type"), )
    extra = 0


class QuestionChoiceInline(_FlatTextInline):
    model = QuestionChoiceModel
    fields = (("name", "order"), )
    extra = 0


# =====================================================================


@admin.register(SurveyModel)
class SurveyAdmin(_FlatText):
    fields = (
        "name",
        "description",
        ("date_start", "date_end"),
    )
    inlines = [QuestionInline, ]


@admin.register(QuestionModel)
class QuestionAdmin(_FlatText):
    fields = (
        ("survey", "order", "type"),
        "name",
    )
    inlines = [QuestionChoiceInline, ]


@admin.register(QuestionChoiceModel)
class QuestionChoiceAdmin(_FlatText):
    fields = (
        ("question", "order"),
        "name",
    )


@admin.register(AnswerModel)
class AnswerAdmin(_FlatText):
    fields = (
        ("user", "question"),
        ("text", "choice"),
    )
