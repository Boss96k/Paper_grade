from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class GradeChange(models.Model):
    """
    Represents a paper grade change event/run on the paper machine.
    """
    class Statuses(models.TextChoices):
        STABILIZING = 'STABILIZING', _('Stabilizing')
        STABILIZED = 'STABILIZED', _('Stabilized')
        FAILED = 'FAILED', _('Failed')

    grade_change_id = models.CharField(
        max_length=100,
        primary_key=True,
        help_text=_("Unique identifier for the grade change run (e.g. from CSV or historian).")
    )
    target_grade = models.CharField(
        max_length=100,
        help_text=_("The goal grade type being transitioned to.")
    )
    start_time = models.DateTimeField(
        help_text=_("Timestamp when the grade change initiated.")
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp when the grade change process finished or stabilized.")
    )
    status = models.CharField(
        max_length=20,
        choices=Statuses.choices,
        default=Statuses.STABILIZING,
        help_text=_("Current operational status of this grade change.")
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grade_changes',
        help_text=_("The operator presiding over this grade change.")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = _('Grade Change')
        verbose_name_plural = _('Grade Changes')

    def __str__(self) -> str:
        return f"GC {self.grade_change_id} (Target: {self.target_grade}, Status: {self.status})"


class SensorData(models.Model):
    """
    Stores high-resolution sensor metrics during a grade change process.
    """
    grade_change = models.ForeignKey(
        GradeChange,
        on_delete=models.CASCADE,
        related_name='sensor_data',
        help_text=_("The grade change run this sensor telemetry belongs to.")
    )
    timestamp = models.DateTimeField(
        help_text=_("Date and time of the sensor telemetry reading.")
    )
    machine_speed = models.FloatField(
        help_text=_("Speed of the paper machine (meters/min).")
    )
    headbox_flow = models.FloatField(
        help_text=_("Flow rate of pulp stock in headbox (liters/min).")
    )
    consistency = models.FloatField(
        help_text=_("Fiber consistency percentage in stock (%).")
    )
    steam_pressure = models.FloatField(
        help_text=_("Steam drying cylinder pressure (bar).")
    )
    basis_weight = models.FloatField(
        help_text=_("Measured basis weight of paper (g/m²).")
    )
    moisture = models.FloatField(
        help_text=_("Moisture percentage in the paper sheet (%).")
    )
    grade = models.CharField(
        max_length=100,
        help_text=_("Current paper grade reported by DCS.")
    )

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['grade_change', 'timestamp']),
        ]
        verbose_name = _('Sensor Telemetry')
        verbose_name_plural = _('Sensor Telemetries')

    def __str__(self) -> str:
        return f"{self.grade_change_id} @ {self.timestamp} - Speed: {self.machine_speed}, BW: {self.basis_weight}"
