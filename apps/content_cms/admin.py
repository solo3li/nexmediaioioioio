from django.contrib import admin
from .models import CustomPage, BlogPost, BlogComment, SystemAnnouncement


@admin.register(CustomPage)
class CustomPageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title_en', 'title_ar', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('slug', 'title_en', 'title_ar', 'content_en', 'content_ar')
    prepopulated_fields = {'slug': ('title_en',)}


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 1
    fields = ('user', 'is_admin_reply', 'content', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title_en', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('slug', 'title_en', 'title_ar', 'content_en')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [BlogCommentInline]


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog_post', 'user', 'is_admin_reply', 'created_at')
    list_filter = ('is_admin_reply', 'created_at')
    search_fields = ('content', 'blog_post__title_en', 'user__username')


@admin.register(SystemAnnouncement)
class SystemAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'banner_type', 'is_active', 'created_at')
    list_filter = ('banner_type', 'is_active')
    search_fields = ('title_en', 'title_ar', 'message_en', 'message_ar')
