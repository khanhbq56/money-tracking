# Generated by Django 5.2.2 on 2025-06-14 10:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transaction_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='monthlytotal',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='monthlytotal',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monthly_totals', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterUniqueTogether(
            name='monthlytotal',
            unique_together={('user', 'year', 'month')},
        ),
        migrations.AddIndex(
            model_name='monthlytotal',
            index=models.Index(fields=['user', 'year', 'month'], name='transaction_user_id_bc28bc_idx'),
        ),
        migrations.AddIndex(
            model_name='monthlytotal',
            index=models.Index(fields=['user', '-year', '-month'], name='transaction_user_id_bee7e3_idx'),
        ),
    ]
