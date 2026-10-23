from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0055_job_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorprofile',
            name='working_hours',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'Vendor-managed weekly schedule, custom arrival slots, booking '
                    'limits, date-specific days off, and unavailable slots.'
                ),
            ),
        ),
    ]
