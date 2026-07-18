import io
import pandas as pd
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from grade_change.models import GradeChange, SensorData
from data_ingestion.services import CSVImportService

User = get_user_model()


class CSVImportServiceTests(TestCase):
    def setUp(self):
        self.service = CSVImportService()
        self.user = User.objects.create_user(
            username='test_operator',
            password='testpassword123',
            role=User.Roles.OPERATOR
        )

    def test_import_valid_csv(self):
        # Create a valid in-memory CSV
        csv_content = (
            "Timestamp,Machine Speed,Headbox Flow,Consistency,Steam Pressure,Basis Weight,Moisture,Grade,Grade Change ID\n"
            "2026-07-15 12:00:00,1200.5,14500.0,0.85,4.2,80.1,6.5,GradeA,GC_001\n"
            "2026-07-15 12:01:00,1201.0,14550.0,0.86,4.3,80.3,6.4,GradeA,GC_001\n"
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))

        stats = self.service.import_csv(csv_file)

        # Check returned stats
        self.assertEqual(stats['grade_changes_created'], 1)
        self.assertEqual(stats['sensor_records_created'], 2)

        # Check DB records
        gc = GradeChange.objects.get(grade_change_id='GC_001')
        self.assertEqual(gc.target_grade, 'GradeA')
        self.assertEqual(gc.status, GradeChange.Statuses.STABILIZED)

        telemetries = SensorData.objects.filter(grade_change=gc)
        self.assertEqual(telemetries.count(), 2)
        self.assertEqual(telemetries.first().machine_speed, 1200.5)

    def test_import_missing_columns(self):
        # Create an invalid CSV missing 'Machine Speed'
        csv_content = (
            "Timestamp,Headbox Flow,Consistency,Steam Pressure,Basis Weight,Moisture,Grade,Grade Change ID\n"
            "2026-07-15 12:00:00,14500.0,0.85,4.2,80.1,6.5,GradeA,GC_001\n"
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))

        with self.assertRaises(ValidationError) as ctx:
            self.service.import_csv(csv_file)

        self.assertIn("Missing required columns in CSV", ctx.exception.message)
        self.assertIn("machine speed", ctx.exception.message)

    def test_import_handles_corrupt_data(self):
        # Create a CSV with some corrupt numeric values to check imputation / forward filling
        csv_content = (
            "Timestamp,Machine Speed,Headbox Flow,Consistency,Steam Pressure,Basis Weight,Moisture,Grade,Grade Change ID\n"
            "2026-07-15 12:00:00,1200.0,14500.0,0.85,4.2,80.0,6.5,GradeA,GC_002\n"
            "2026-07-15 12:01:00,invalid_number,14550.0,0.86,4.3,80.2,6.4,GradeA,GC_002\n"
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))

        stats = self.service.import_csv(csv_file)
        self.assertEqual(stats['sensor_records_created'], 2)

        # The second row's machine speed should be forward-filled from the first row (1200.0)
        telemetries = list(SensorData.objects.filter(grade_change_id='GC_002').order_by('timestamp'))
        self.assertEqual(telemetries[1].machine_speed, 1200.0)
