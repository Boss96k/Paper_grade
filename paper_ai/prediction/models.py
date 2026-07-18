from django.db import models
from django.utils.translation import gettext_lazy as _
from grade_change.models import GradeChange, SensorData


class Prediction(models.Model):
    """
    Stores target predictions made by the ML models during a grade change process.
    """
    grade_change = models.ForeignKey(
        GradeChange,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text=_("The grade change run for which this prediction was made.")
    )
    sensor_data = models.ForeignKey(
        SensorData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions',
        help_text=_("The specific sensor data telemetry point this prediction is based on (if any).")
    )
    timestamp = models.DateTimeField(
        help_text=_("The timestamp for which the prediction is valid (or made).")
    )
    predicted_basis_weight = models.FloatField(
        help_text=_("Predicted Basis Weight (BW) of the paper (g/m²).")
    )
    predicted_stabilization_time = models.FloatField(
        help_text=_("Predicted time (minutes) until the grade change process stabilizes.")
    )
    quality_deviation_probability = models.FloatField(
        help_text=_("Probability of Basis Weight deviation outside the target limits (0.0 to 1.0).")
    )
    confidence_score = models.FloatField(
        help_text=_("Confidence score of the AI prediction (0.0 to 1.0).")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the prediction record was created.")
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Prediction')
        verbose_name_plural = _('Predictions')

    def __str__(self) -> str:
        return f"Pred for {self.grade_change_id} (BW: {self.predicted_basis_weight:.2f}, Stable: {self.predicted_stabilization_time:.1f}m)"
