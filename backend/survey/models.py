from enum import Enum

from django.db.models import Model, Index, CASCADE, Q, F
from django.db.models import (
    ForeignKey,
    ManyToManyField,
    TextField,
    DateField,
    IntegerField,
    CharField,
    UUIDField,
    BooleanField,
)
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.core.validators import MinValueValidator


__all__ = [
    "Survey",
    "Question",
    "QuestionChoice",
    "Answer",
    "AnswerChoice",
]


class Survey(Model):
    name = TextField(
        verbose_name="Survey name",
        null=False,
    )
    description = TextField(
        verbose_name="Description",
        null=False,
    )
    date_start = DateField(
        verbose_name="Start date",
        null=False,
    )
    date_end = DateField(
        verbose_name="End date",
        null=True,
    )

    class Meta:
        indexes = [
            Index("date_start", name="date_start_idx"),
            Index("date_end", name="date_end_idx"),
        ]
        get_latest_by = "date_start"
        constraints = [
            CheckConstraint(
                check=Q(date_end=None) | Q(date_end__gt=F("date_start")),
                name="end_after_start"
            ),
        ]

    def __str__(self):
        return (
            f"\"{self.name[:30]}\""
            f" / {self.date_start:%d.%m.%y}"
            f" - {self.date_end:%d.%m.%y}"
        )


class Question(Model):
    class Types(Enum):
        STR = "string"
        SIN = "single choice"
        MUL = "multiple choice"

    survey = ForeignKey(
        Survey,
        on_delete=CASCADE,
        verbose_name="Survey",
        related_name="questions",
        null=False,
    )
    name = TextField(
        verbose_name="Question name",
        null=False,
    )
    order = IntegerField(
        verbose_name="Question order",
        null=False,
        default=0,
        validators=[MinValueValidator(0)],
    )
    type = CharField(
        verbose_name="Question type",
        max_length=3,
        choices=tuple((t.name, t.value) for t in Types)
    )

    class Meta:
        constraints = [
            UniqueConstraint("survey", "order", name="question_order_in_survey"),
        ]
        indexes = [
            Index(fields=["survey", "order"]),
        ]
        order_with_respect_to = "survey"

    def __str__(self):
        return (
            f"\"{self.name[:30]}\""
            f" - <{self.get_type_display()}>"
            f" || [{self.survey}]"
        )


class QuestionChoice(Model):
    question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Question to which is attached",
        related_name="choices",
        null=False,
    )
    name = TextField(
        verbose_name="Choice name",
        null=False,
    )
    order = IntegerField(
        verbose_name="Choice order",
        null=False,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        constraints = [
            UniqueConstraint("question", "order", name="choice_order_in_question"),
        ]
        indexes = [
            Index(fields=["question", "order"]),
        ]
        order_with_respect_to = "question"

    def __str__(self):
        return f"\"{self.name[:30]}\" || [{self.question.name[:20]}]"


class Answer(Model):
    user = UUIDField(
        verbose_name="User identifier",
        null=False,
    )
    question = ForeignKey(
        Question,
        on_delete=CASCADE,
        verbose_name="Question to which is answered",
        related_name="answers",
        null=False,
    )
    text = TextField(
        verbose_name="Answer (if textual)",
        null=True,
    )
    choice = ManyToManyField(
        QuestionChoice,
        verbose_name="Answer (if choice)",
        related_name="+",
    )

    class Meta:
        indexes = [
            Index("user", name="user_idx")
        ]
        constraints = [
            UniqueConstraint("user", "question", name="answer_for_question"),
        ]
        order_with_respect_to = "question"

    def __str__(self):
        return (
            f"user"
        )


AnswerChoice = Answer.choice.through
