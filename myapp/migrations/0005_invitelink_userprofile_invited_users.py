# Generated by Django 5.1.3 on 2024-11-30 13:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0004_userprofile_activated_invite_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="InviteLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("activated_at", models.DateTimeField(auto_now_add=True)),
                (
                    "invited_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitations",
                        to="myapp.userprofile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invites",
                        to="myapp.userprofile",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="userprofile",
            name="invited_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="invited_by",
                through="myapp.InviteLink",
                to="myapp.userprofile",
            ),
        ),
    ]