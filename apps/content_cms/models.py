from django.conf import settings
from django.db import models
from django.utils import timezone


class CustomPage(models.Model):
    slug = models.SlugField(max_length=100, unique=True, help_text="e.g. 'privacy', 'terms', 'about'")
    title_en = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    content_en = models.TextField(blank=True)
    content_ar = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Custom Page'
        verbose_name_plural = 'Custom Pages'
        ordering = ['slug']

    def __str__(self):
        return f"{self.slug} ({self.title_en})"


class BlogPost(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=100, default='General')
    title_en = models.CharField(max_length=300)
    title_ar = models.CharField(max_length=300)
    content_en = models.TextField()
    content_ar = models.TextField()
    media_url = models.URLField(max_length=1000, blank=True)
    media_type = models.CharField(max_length=50, blank=True, help_text="image, video, etc.")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title_en or self.title_ar


class BlogComment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_comments')
    content = models.TextField()
    is_admin_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Blog Comment'
        verbose_name_plural = 'Blog Comments'
        ordering = ['created_at']

    def __str__(self):
        author = 'Admin' if self.is_admin_reply else (self.user.username if self.user else 'Guest')
        return f"Comment by {author} on {self.blog_post.slug}"


class SystemAnnouncement(models.Model):
    title_en = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    message_en = models.TextField()
    message_ar = models.TextField()
    banner_type = models.CharField(max_length=50, default='info', choices=[('info', 'Info'), ('warning', 'Warning'), ('success', 'Success')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'System Announcement'
        verbose_name_plural = 'System Announcements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title_en
