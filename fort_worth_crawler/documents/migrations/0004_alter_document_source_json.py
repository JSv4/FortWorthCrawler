# Generated by Django 4.0.8 on 2022-11-13 21:27

from django.db import migrations
import fort_worth_crawler.shared.defaults
import fort_worth_crawler.shared.fields


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_rename_last_updated_document_last_updated_locally_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='source_json',
            field=fort_worth_crawler.shared.defaults.NullableJSONField(default=fort_worth_crawler.shared.fields.jsonfield_default_value, null=True),
        ),
    ]
