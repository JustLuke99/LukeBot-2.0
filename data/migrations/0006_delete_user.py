# Generated by Django 4.2.4 on 2023-08-31 20:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0005_redditimage_last_sent_alter_redditimage_date_created"),
    ]

    operations = [
        migrations.DeleteModel(
            name="User",
        ),
    ]
