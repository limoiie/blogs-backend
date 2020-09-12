# Generated by Django 3.0.3 on 2020-02-23 12:40

import blogs.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='A',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='markdown/%Y/%m/%d')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('folder', models.CharField(max_length=200)),
                ('abstract', models.TextField()),
                ('md_doc', models.FileField(upload_to=blogs.models.upload_to_markdown)),
                ('html_doc', models.FileField(upload_to=blogs.models.upload_to_html)),
                ('create_time', models.DateTimeField(verbose_name='date published')),
                ('edit_time', models.DateTimeField(verbose_name='date edited')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blogs.User')),
                ('tags', models.ManyToManyField(to='blogs.Tag')),
            ],
        ),
    ]