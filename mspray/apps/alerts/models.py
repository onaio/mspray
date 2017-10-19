from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import JSONField


class AlertLog(models.Model):
    """
    Model used to store notification logs
    """

    # notification types
    HF_FINISHED = '1'
    WEEKLY_DASHBOARD_UPDATE = '2'
    SO_DAILY_FORM = '3'
    GPS_OFF = '4'
    USER_DISTANCE = '5'

    NOTIFICATION_CHOICES = (
        (HF_FINISHED, _('Health Facility Catchment Finished')),
        (WEEKLY_DASHBOARD_UPDATE, _('Weekly Dashboard Update')),
        (SO_DAILY_FORM, _('SO Daily Form Completed')),
        (GPS_OFF, _('GPS OFF')),
        (USER_DISTANCE, _('User Distance')),
    )

    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_modified = models.DateTimeField(_("Date Modified"), auto_now=True)
    notification_type = models.CharField(_("Notification Type"), max_length=1,
                                         choices=NOTIFICATION_CHOICES,
                                         blank=False)
    get_data = JSONField(_("GET data"), default={})
    post_data = JSONField(_("POST data"), default={})
    success = models.BooleanField(_("Success"), default=False)

    class Meta:
        app_label = 'alerts'
        verbose_name = _("Alert Log")
        verbose_name_plural = _("Alert Logs")

    def __str__(self):
        return "{} - {}".format(self.date_created,
                                self.get_notification_type_display())

