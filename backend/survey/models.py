from enum import Enum
from functools import partial

from django.db.models import Model, Index, CASCADE, Q, F
from django.db.models import (
    ForeignKey,
    ManyToManyField,
    TextField,
    DateField,
    IntegerField,
    CharField,
    BooleanField,
)
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.core.validators import MinValueValidator
from django.utils.crypto import get_random_string

from .managers import SurveyManager


__all__ = [
    "SurveyModel",
    "QuestionModel",
    "QuestionChoiceModel",
    "UserTokenModel",
    "AnswerModel",
    "AnswerQuestionModel",
    "AnswerChoiceModel",
]


date_format = "%d.%m.%Y"


class SurveyModel(Model):
    """
    Survey model.
    The main model, all other entities are attached to it (questions,
    answers, choices...).
    """

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
    is_hidden = BooleanField(
        verbose_name="Hidden",
        null=False,
        default=False,
    )

    objects = SurveyManager()

    class Meta:
        indexes = [
            Index("date_start", name="date_start_idx"),
            Index("date_end", name="date_end_idx"),
            Index("is_hidden", name="is_hidden_idx"),
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
            f" : {self.date_start:{date_format}}"
            f" - {self.date_end:{date_format}}"
        )


class QuestionModel(Model):
    """
    Question model.
    The question is attached to the survey model, it can be a
    string/single choice/multiple choice.
    If the question is a choice, the choices are attached to it through
    the choices model (not checked through the database, only through
    the implemented business logic).
    """

    class Types(Enum):
        STR = "string"
        SIN = "single choice"
        MUL = "multiple choice"

    survey = ForeignKey(
        SurveyModel,
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
            f" : <{self.get_type_display()}>"
            f" : {self.survey}"
        )


class QuestionChoiceModel(Model):
    """
    Model of one choice for a question, attaches to the question.
    """

    question = ForeignKey(
        QuestionModel,
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
        return f"\"{self.name[:30]}\" : {self.question.name[:20]}"


class UserTokenModel(Model):
    """
    Model to identify the user who answered the question.
    This generates a random token and links to this token for all
    responses by this user. The token is also written to a cookie/store
    to associate responses to different surveys.
    """

    _generate_token = partial(get_random_string, 36)

    token = CharField(
        verbose_name="User token",
        max_length=36,
        default=_generate_token,
        unique=True,
        null=False,
        editable=False,
    )
    date_issuance = DateField(
        verbose_name="Issuance date",
        null=False,
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            Index("token", name="token_idx"),
            Index("date_issuance", name="date_issuance_idx"),
        ]

    def __str__(self):
        return f"{self.token} : {self.date_issuance:{date_format}}"


class AnswerModel(Model):
    """
    Survey response model, answers to individual questions are attached
    to this model.
    """

    user = ForeignKey(
        UserTokenModel,
        on_delete=CASCADE,
        verbose_name="User",
        null=False,
    )
    survey = ForeignKey(
        SurveyModel,
        on_delete=CASCADE,
        verbose_name="Survey to which is answered",
        related_name="answers",
        null=False,
    )
    date_answer = DateField(
        verbose_name="Response date",
        null=False,
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            Index("date_answer", name="date_answer_idx"),
        ]
        order_with_respect_to = "survey"

    def __str__(self):
        return (
            f"{self.user.token[:16]}"
            f" : {self.survey.name[:20]}"
            f" : {self.date_answer:{date_format}}"
        )


class AnswerQuestionModel(Model):
    """
    Model answer to a separate question, attaches to the survey answer
    model.
    It has 2 fields for answers - text field and m2m-relationship with
    choices model. In the case of the string answer, the answer is
    written in the string field, in the case of the choice answer, the
    answer is an m2m-ratio. By logic, the answer can be either there or
    there, but it is impossible to check it, so it is expected that the
    writing is correct.
    """

    answer = ForeignKey(
        AnswerModel,
        on_delete=CASCADE,
        verbose_name="Survey",
        related_name="questions",
        null=False,
    )
    question = ForeignKey(
        QuestionModel,
        on_delete=CASCADE,
        verbose_name="Question",
        related_name="answers",
        null=False,
    )
    text = TextField(
        verbose_name="Answer (if textual)",
        null=True,
        blank=True,
    )
    choice = ManyToManyField(
        QuestionChoiceModel,
        verbose_name="Answer (if choice)",
        related_name="+",
        blank=True,
    )

    class Meta:
        constraints = [
            UniqueConstraint("answer", "question", name="answer_for_question"),
        ]
        order_with_respect_to = "answer"

    def __str__(self):
        return f"{self.answer.user.token[:16]} : {self.question}"


AnswerChoiceModel = AnswerQuestionModel.choice.through
