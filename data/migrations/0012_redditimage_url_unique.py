from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0011_fix_model_defaults_and_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="redditimage",
            name="url",
            field=models.CharField(
                verbose_name="URL obrázku",
                help_text="Přímá URL na obrázek (png, jpg, gif). Musí být unikátní.",
                max_length=255,
                unique=True,
            ),
        ),
    ]
