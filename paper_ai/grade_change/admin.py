from django.contrib import admin
from .models import GradeChange, SensorData


class SensorDataInline(admin.TabularInline):
    model = SensorData
    extra = 0
    fields = ('timestamp', 'machine_speed', 'headbox_flow', 'consistency', 'steam_pressure', 'basis_weight', 'moisture', 'grade')
    readonly_fields = fields
    show_change_link = True
    max_num = 10  # Limit inline to prevent page lag with large timeseries datasets


@admin.register(GradeChange)
class GradeChangeAdmin(admin.ModelAdmin):
    list_display = ('grade_change_id', 'target_grade', 'start_time', 'end_time', 'status', 'operator')
    list_filter = ('status', 'target_grade', 'operator')
    search_fields = ('grade_change_id', 'target_grade')
    inlines = [SensorDataInline]
    raw_id_fields = ('operator',)
    ordering = ('-start_time',)


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('grade_change', 'timestamp', 'machine_speed', 'basis_weight', 'moisture', 'grade')
    list_filter = ('grade', 'grade_change')
    search_fields = ('grade_change__grade_change_id', 'grade')
    ordering = ('-timestamp',)
