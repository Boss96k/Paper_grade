from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('grade_change', 'timestamp', 'recommended_machine_speed', 'recommended_headbox_flow', 'recommended_steam_pressure', 'recommended_consistency', 'expected_improvement', 'status', 'created_at')
    list_filter = ('status', 'grade_change', 'created_at')
    search_fields = ('grade_change__grade_change_id',)
    ordering = ('-created_at',)
