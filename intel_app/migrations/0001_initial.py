# Generated by Django 4.2.4 on 2024-10-31 10:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=250, unique=True)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('wallet', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('status', models.CharField(choices=[('User', 'User'), ('Agent', 'Agent'), ('Super Agent', 'Super Agent')], default='User', max_length=250)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
        ),
        migrations.CreateModel(
            name='AdminInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('phone_number', models.BigIntegerField(blank=True, null=True)),
                ('momo_number', models.PositiveBigIntegerField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('payment_channel', models.CharField(choices=[('MTN Mobile Money', 'MTN Mobile Money'), ('Vodafone Cash', 'Vodafone Cash'), ('AT Money', 'AT Money')], max_length=250)),
                ('ishare_channel', models.CharField(blank=True, choices=[('Geosams', 'Geosams'), ('Gyasi', 'Gyasi'), ('Value4Moni', 'Value4Moni')], default='Geosams', max_length=250, null=True)),
                ('afa_price', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AgentBigTimeBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='AgentIshareBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='AgentMTNBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='AgentTelecelBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, max_length=500, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='BigTimeBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='IshareBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='MTNBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SuperAgentBigTimeBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SuperAgentIshareBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SuperAgentMTNBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SuperAgentTelecelBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TelecelBundlePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('bundle_volume', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TopUpRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=250)),
                ('amount', models.FloatField()),
                ('status', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('credited_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TelecelTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bundle_number', models.BigIntegerField()),
                ('amount', models.FloatField(default=0.0)),
                ('offer', models.CharField(max_length=250)),
                ('reference', models.CharField(blank=True, max_length=20)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Canceled and Refunded', 'Canceled and Refunded'), ('Failed', 'Failed')], default='Pending', max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=256)),
                ('amount', models.FloatField(blank=True, null=True)),
                ('payment_description', models.CharField(blank=True, max_length=500, null=True)),
                ('transaction_status', models.CharField(blank=True, default='Unfinished', max_length=256, null=True)),
                ('transaction_date', models.CharField(blank=True, max_length=250, null=True)),
                ('message', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MTNTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bundle_number', models.BigIntegerField()),
                ('amount', models.FloatField(default=0.0)),
                ('offer', models.CharField(max_length=250)),
                ('reference', models.CharField(blank=True, max_length=20)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Canceled and Refunded', 'Canceled and Refunded'), ('Failed', 'Failed')], default='Pending', max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IShareBundleTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bundle_number', models.BigIntegerField()),
                ('amount', models.FloatField(default=0.0)),
                ('offer', models.CharField(max_length=250)),
                ('reference', models.CharField(blank=True, max_length=20)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_status', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BigTimeTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bundle_number', models.BigIntegerField()),
                ('amount', models.FloatField(default=0.0)),
                ('offer', models.CharField(max_length=250)),
                ('reference', models.CharField(blank=True, max_length=20)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Canceled and Refunded', 'Canceled and Refunded'), ('Failed', 'Failed')], default='Pending', max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AFARegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.BigIntegerField()),
                ('gh_card_number', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=250)),
                ('amount', models.FloatField(default=0.0)),
                ('occupation', models.CharField(blank=True, max_length=250)),
                ('reference', models.CharField(blank=True, max_length=250)),
                ('date_of_birth', models.DateField()),
                ('transaction_status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Canceled and Refunded', 'Canceled and Refunded'), ('Failed', 'Failed')], default='Pending', max_length=100)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.CheckConstraint(check=models.Q(('wallet__gte', 0)), name='wallet_non_negative'),
        ),
    ]
