from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'operator', 'status', 'created_at')
    list_filter = ('status', 'operator', 'created_at')
    search_fields = ('recommendation__grade_change__grade_change_id', 'comments')
    ordering = ('-created_at',)
    raw_id_fields = ('recommendation', 'operator')
