from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Mirrors Moodle's mdl_user table with additional fields.
    """
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_MODERATOR, 'Moderator'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=2, blank=True)
    timezone = models.CharField(max_length=100, default='UTC')
    lang = models.CharField(max_length=10, default='en')
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    idnumber = models.CharField(max_length=255, blank=True, help_text='Institutional ID number')
    department = models.CharField(max_length=255, blank=True)
    institution = models.CharField(max_length=255, blank=True)
    is_suspended = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'elening_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})

    @property
    def is_teacher(self):
        return self.role in [self.ROLE_TEACHER, self.ROLE_MODERATOR, self.ROLE_ADMIN]

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_moderator(self):
        return self.role in [self.ROLE_MODERATOR, self.ROLE_ADMIN]

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    @property
    def full_name(self):
        return self.get_full_name() or self.username


class UserProfile(models.Model):
    """Extended profile information for users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    website = models.URLField(blank=True)
    interests = models.TextField(blank=True)
    skype = models.CharField(max_length=50, blank=True)
    aim = models.CharField(max_length=50, blank=True)
    msn = models.CharField(max_length=50, blank=True)
    yahoo = models.CharField(max_length=50, blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'elening_user_profiles'

    def __str__(self):
        return f'Profile of {self.user}'


class UserPreference(models.Model):
    """User preferences (mirrors mdl_user_preferences)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences')
    name = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        db_table = 'elening_user_preferences'
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.user.username}: {self.name}'
