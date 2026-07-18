import pandas as pd
from typing import Dict, Any, List
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from grade_change.models import GradeChange, SensorData


class CSVImportService:
    """
    Service layer for parsing, validating, cleaning, and importing paper grade sensor data from CSV files.
    """
    REQUIRED_COLUMNS = {
        'timestamp',
        'machine speed',
        'headbox flow',
        'consistency',
        'steam pressure',
        'basis weight',
        'moisture',
        'grade',
        'grade change id'
    }

    def import_csv(self, file_wrapper) -> Dict[str, Any]:
        """
        Parses a CSV file object, validates the columns, cleans values, and bulk inserts sensor records.
        Automatically resolves or creates associated GradeChange entities.
        """
        try:
            # Read CSV
            df = pd.read_csv(file_wrapper)
        except Exception as e:
            raise ValidationError(f"Invalid CSV file format: {str(e)}")

        # Normalize column names (lowercase, stripped whitespace)
        original_cols = df.columns.tolist()
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Validate columns
        missing_cols = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValidationError(
                f"Missing required columns in CSV: {', '.join(missing_cols)}. "
                f"Found columns: {', '.join(original_cols)}"
            )

        # Clean/Validate Timestamp
        df['parsed_timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        invalid_timestamps = df['parsed_timestamp'].isna().sum()
        if invalid_timestamps > 0:
            # Drop rows with invalid timestamps
            df = df.dropna(subset=['parsed_timestamp'])
            if df.empty:
                raise ValidationError("CSV contains no valid timestamps.")

        # Localize timestamps to the active Django timezone
        if settings.USE_TZ:
            try:
                df['parsed_timestamp'] = df['parsed_timestamp'].dt.tz_localize(timezone.get_current_timezone())
            except Exception:
                # Fallback in case localization fails or timezone is already set
                df['parsed_timestamp'] = df['parsed_timestamp'].dt.tz_convert(timezone.get_current_timezone())

        # Sort by timestamp to ensure chronological order
        df = df.sort_values(by='parsed_timestamp')



        # Clean numeric fields (coerce errors to NaN and fill or drop)
        numeric_cols = ['machine speed', 'headbox flow', 'consistency', 'steam pressure', 'basis weight', 'moisture']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaNs with 0.0 or forward fill. Let's forward fill first, then fill remaining with 0.0
            df[col] = df[col].ffill().bfill().fillna(0.0)

        # Clean grade and grade change id strings
        df['grade'] = df['grade'].astype(str).str.strip()
        df['grade change id'] = df['grade change id'].astype(str).str.strip()

        # Let's run the import in a transaction to prevent partial imports
        stats = {
            'sensor_records_created': 0,
            'grade_changes_created': 0,
            'grade_changes_updated': 0
        }

        with transaction.atomic():
            # Group data by Grade Change ID to create/resolve GradeChange models
            grouped = df.groupby('grade change id')
            
            # Map of grade_change_id to GradeChange instance
            grade_changes_cache: Dict[str, GradeChange] = {}

            for gc_id, group in grouped:
                if not gc_id or str(gc_id).lower() == 'nan':
                    continue

                # Try to fetch existing GradeChange
                gc_instance = GradeChange.objects.filter(grade_change_id=gc_id).first()
                
                # Determine target grade and times from group
                min_time = group['parsed_timestamp'].min()
                max_time = group['parsed_timestamp'].max()
                target_grade = group['grade'].iloc[-1]  # Use the last grade in chronological sequence

                if not gc_instance:
                    # Create new GradeChange
                    gc_instance = GradeChange.objects.create(
                        grade_change_id=gc_id,
                        target_grade=target_grade,
                        start_time=min_time,
                        end_time=max_time,
                        status=GradeChange.Statuses.STABILIZED
                    )
                    stats['grade_changes_created'] += 1
                else:
                    # Update existing GradeChange times if they expanded
                    updated = False
                    if min_time < gc_instance.start_time:
                        gc_instance.start_time = min_time
                        updated = True
                    if not gc_instance.end_time or max_time > gc_instance.end_time:
                        gc_instance.end_time = max_time
                        updated = True
                    if updated:
                        gc_instance.save()
                        stats['grade_changes_updated'] += 1

                grade_changes_cache[gc_id] = gc_instance

            # Now bulk insert SensorData
            sensor_data_to_create: List[SensorData] = []
            for _, row in df.iterrows():
                gc_id = row['grade change id']
                if gc_id not in grade_changes_cache:
                    continue

                sensor_data_to_create.append(
                    SensorData(
                        grade_change=grade_changes_cache[gc_id],
                        timestamp=row['parsed_timestamp'],
                        machine_speed=row['machine speed'],
                        headbox_flow=row['headbox flow'],
                        consistency=row['consistency'],
                        steam_pressure=row['steam pressure'],
                        basis_weight=row['basis weight'],
                        moisture=row['moisture'],
                        grade=row['grade']
                    )
                )

            if sensor_data_to_create:
                # To avoid duplicates if the file is re-uploaded, we could filter or delete old records.
                # For Phase 1, we will clear existing sensor data for the grade changes in this upload.
                gc_ids = list(grade_changes_cache.keys())
                SensorData.objects.filter(grade_change_id__in=gc_ids).delete()
                
                # Bulk create
                created_objs = SensorData.objects.bulk_create(sensor_data_to_create)
                stats['sensor_records_created'] = len(created_objs)

        return stats
