from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from grade_change.models import GradeChange, SensorData
from recommendation.models import Recommendation
from feedback.models import Feedback


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    """
    Renders the main industrial command dashboard, compiling
    historical telemetry metrics, KPIs, and recommendations.
    """
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Core KPIs
        total_grade_changes = GradeChange.objects.count()
        total_sensor_data = SensorData.objects.count()
        
        # Recommendations and operator feedback metrics
        recommendations = Recommendation.objects.all()
        total_recommendations = recommendations.count()
        
        accepted_recs = recommendations.filter(status=Recommendation.Statuses.ACCEPTED).count()
        rejected_recs = recommendations.filter(status=Recommendation.Statuses.REJECTED).count()
        modified_recs = recommendations.filter(status=Recommendation.Statuses.MODIFIED).count()
        pending_recs = recommendations.filter(status=Recommendation.Statuses.PENDING).count()

        # Acceptance Rate Calculation: (Accepted + Modified) / Total Feedbacks
        feedback_count = accepted_recs + rejected_recs + modified_recs
        if feedback_count > 0:
            acceptance_rate = ((accepted_recs + modified_recs) / feedback_count) * 100
        else:
            acceptance_rate = 0.0

        # Recent Grade Changes list (last 10 runs)
        recent_grade_changes = GradeChange.objects.select_related('operator').all()[:10]

        # Populate Context
        context.update({
            'total_grade_changes': total_grade_changes,
            'total_sensor_data': total_sensor_data,
            'total_recommendations': total_recommendations,
            'acceptance_rate': round(acceptance_rate, 1),
            'accepted_count': accepted_recs,
            'rejected_count': rejected_recs,
            'modified_count': modified_recs,
            'pending_count': pending_recs,
            'recent_grade_changes': recent_grade_changes,
        })
        
        return context
