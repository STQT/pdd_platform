from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="explanation_ru",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="question",
            name="explanation_kz",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="question",
            name="explanation_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="question",
            name="explanation2_media",
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
