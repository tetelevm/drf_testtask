import datetime as dt

from django.db.models import Manager


class SurveyManager(Manager):
    def active(self):
        """
        Returns only active surveys (started, not finished, not hidden).
        """
        today = dt.date.today()
        return self.filter(
            date_start__lte=today,
            date_end__gte=today,
            is_hidden=False,
        )
