# Generated by Django 5.1.6 on 2025-06-11 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_event_duration_minutes_alter_event_event_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='learner_course_progress',
            old_name='completed',
            new_name='is_completed',
        ),
        migrations.RenameField(
            model_name='learner_module_progress',
            old_name='completed',
            new_name='is_completed',
        ),
        migrations.RenameField(
            model_name='learner_specialization_progress',
            old_name='completed',
            new_name='is_completed',
        ),
    ]
