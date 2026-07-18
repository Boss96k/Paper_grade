from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .forms import CSVUploadForm
from .services import CSVImportService


class CSVUploadView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    Handles CSV log file uploads and processes the ingestion.
    Only allows users with Admin or Process Engineer roles.
    """
    template_name = 'data_ingestion/import.html'
    form_class = CSVUploadForm
    success_url = reverse_lazy('dashboard:index')

    def test_func(self) -> bool:
        user = self.request.user
        return user.is_authenticated and (user.is_admin or user.is_process_engineer)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have the required permissions to upload historical logs.")
        return redirect('dashboard:index')

    def form_valid(self, form):
        csv_file = self.request.FILES['csv_file']
        import_service = CSVImportService()
        
        try:
            stats = import_service.import_csv(csv_file)
            messages.success(
                self.request,
                f"Successfully ingested data! "
                f"Created {stats['grade_changes_created']} grade changes, "
                f"updated {stats['grade_changes_updated']}, "
                f"and imported {stats['sensor_records_created']} sensor log rows."
            )
        except ValidationError as e:
            form.add_error('csv_file', e.message)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error('csv_file', f"An unexpected error occurred during processing: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)
