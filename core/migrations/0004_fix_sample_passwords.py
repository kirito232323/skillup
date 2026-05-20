from django.contrib.auth.hashers import make_password
from django.db import migrations


def update_sample_user_passwords(apps, schema_editor):
    SkillUpUser = apps.get_model('core', 'SkillUpUser')
    samples = [
        {
            'email': 'ca.delarama@email.com',
            'password': 'kP9$vB2#mX!q',
            'track': 'Full-Stack Engineering Framework Track',
        },
        {
            'email': 'jm.rosales@email.com',
            'password': 'tZ4*fW7&gQ#s',
            'track': 'Full-Stack Engineering Framework Track',
        },
        {
            'email': 'a.sicat@email.com',
            'password': 'rN2!yK9$xL*b',
            'track': 'Administration',
        },
    ]
    for sample in samples:
        try:
            user = SkillUpUser.objects.get(email=sample['email'])
            user.password = make_password(sample['password'])
            user.track = sample['track']
            user.save(update_fields=['password', 'track'])
        except SkillUpUser.DoesNotExist:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_add_persistence_fields'),
    ]

    operations = [
        migrations.RunPython(update_sample_user_passwords),
    ]
