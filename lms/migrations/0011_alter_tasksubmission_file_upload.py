# Generated by Django 5.1.7 on 2025-04-10 14:47

import Generic.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lms", "0010_rename_level_restiction_classroom_level_restriction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tasksubmission",
            name="file_upload",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=Generic.utils.task_submission_upload_path,
            ),
        ),
    ]
