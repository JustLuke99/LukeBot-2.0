# Oprava výchozích hodnot modelů (callable místo pevné hodnoty)
# + indexy pro výkon + unique_together pro RunningCommand

import data.models
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0010_alter_redditimage_date_created"),
    ]

    operations = [
        # Oprava date_created — byl hardcoded datetime, nyní callable timezone.now
        migrations.AlterField(
            model_name="redditimage",
            name="date_created",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        # Oprava last_sent — byl hardcoded datetime, nyní callable
        migrations.AlterField(
            model_name="redditimage",
            name="last_sent",
            field=models.DateTimeField(default=data.models._default_last_sent),
        ),
        # Index na url pro rychlejší vyhledávání při deduplikaci
        migrations.AlterField(
            model_name="redditimage",
            name="url",
            field=models.CharField(db_index=True, max_length=255),
        ),
        # Index na subreddit pro filtrování
        migrations.AlterField(
            model_name="redditimage",
            name="subreddit",
            field=models.CharField(db_index=True, max_length=100),
        ),
        # Index na room_id pro rychlejší lookup RunningCommand
        migrations.AlterField(
            model_name="runningcommand",
            name="room_id",
            field=models.IntegerField(db_index=True),
        ),
        # Unique constraint zabraňuje duplikátním záznamům
        migrations.AlterUniqueTogether(
            name="runningcommand",
            unique_together={("room_id", "command_name")},
        ),
    ]
