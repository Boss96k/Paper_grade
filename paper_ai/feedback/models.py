from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from recommendation.models import Recommendation


class Feedback(models.Model):
    """
    Stores operator feedback on recommendations made by the AI.
    Tracks whether a recommendation was accepted, rejected, or modified.
    """
    class Choices(models.TextChoices):
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        MODIFIED = 'MODIFIED', _('Modified')

    recommendation = models.OneToOneField(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text=_("The recommendation this feedback is for.")
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text=_("The operator who submitted this feedback.")
    )
    status = models.CharField(
        max_length=20,
        choices=Choices.choices,
        help_text=_("Operator's final decision on this recommendation.")
    )
    modified_machine_speed = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Operator overridden setpoint for Machine Speed (if modified).")
    )
    modified_headbox_flow = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Operator overridden setpoint for Headbox Flow (if modified).")
    )
    modified_steam_pressure = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Operator overridden setpoint for Steam Pressure (if modified).")
    )
    modified_consistency = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Operator overridden setpoint for Stock Consistency (if modified).")
    )
    comments = models.TextField(
        blank=True,
        help_text=_("Operator comments or notes regarding their choice.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this feedback was submitted.")
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Operator Feedback')
        verbose_name_plural = _('Operator Feedbacks')

    def save(self, *args, **kwargs):
        # Automatically update the status of the associated recommendation
        super().save(*args, **kwargs)
        if self.recommendation.status != self.status:
            self.recommendation.status = self.status
            self.recommendation.save(update_fields=['status'])

    def __str__(self) -> str:
        return f"Feedback {self.id} for Rec {self.recommendation_id} ({self.status}) by {self.operator.username}"
