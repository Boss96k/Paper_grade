from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('grade_change', 'timestamp', 'predicted_basis_weight', 'predicted_stabilization_time', 'quality_deviation_probability', 'confidence_score', 'created_at')
    list_filter = ('grade_change', 'created_at')
    search_fields = ('grade_change__grade_change_id',)
    ordering = ('-created_at',)
