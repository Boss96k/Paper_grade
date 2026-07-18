from django import forms
from django.core.validators import FileExtensionValidator


class CSVUploadForm(forms.Form):
    """
    Form to upload a CSV containing process sensor telemetry records.
    """
    csv_file = forms.FileField(
        label="Select CSV Process Log File",
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'accept': '.csv',
                'id': 'csv-file-input'
            }
        ),
        help_text="Upload a CSV process log with columns: Timestamp, Machine Speed, Headbox Flow, Consistency, Steam Pressure, Basis Weight, Moisture, Grade, Grade Change ID."
    )
