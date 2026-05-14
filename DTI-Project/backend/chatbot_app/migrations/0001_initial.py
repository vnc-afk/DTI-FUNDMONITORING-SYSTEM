from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(help_text="User's question/message")),
                ("detected_intent", models.CharField(blank=True, help_text="Detected intent from message processing", max_length=50)),
                ("confidence_score", models.FloatField(default=0.0, help_text="Confidence score for intent detection (0-1)")),
                ("response", models.TextField(help_text="Chatbot's response")),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("is_resolved", models.BooleanField(default=True, help_text="Whether the response satisfied the user's query")),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_histories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Chat History",
                "verbose_name_plural": "Chat Histories",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.AddIndex(
            model_name="chathistory",
            index=models.Index(fields=["-timestamp"], name="chatbot_ch_timestamp_idx"),
        ),
        migrations.AddIndex(
            model_name="chathistory",
            index=models.Index(fields=["user", "-timestamp"], name="chatbot_ch_user_ts_idx"),
        ),
        migrations.AddIndex(
            model_name="chathistory",
            index=models.Index(fields=["detected_intent", "-timestamp"], name="chatbot_ch_intent_ts_idx"),
        ),
    ]
