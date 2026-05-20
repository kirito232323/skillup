from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_create_sample_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='skillupuser',
            name='track',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='provider',
            field=models.CharField(default='SkillUp Learning Registry', max_length=120),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='track',
            field=models.CharField(default='All Tracks', max_length=255),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=20),
        ),
        migrations.AddField(
            model_name='evaluationform',
            name='target_course',
            field=models.CharField(default='All Tracks', max_length=255),
        ),
        migrations.AddField(
            model_name='evaluationquestion',
            name='metadata',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
