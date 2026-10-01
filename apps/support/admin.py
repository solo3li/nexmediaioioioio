from django.contrib import admin
from .models import SupportTicket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1
    fields = ('sender', 'is_admin_message', 'content', 'attachment_url', 'attachment_type', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__username', 'user__email')
    list_editable = ('status',)
    inlines = [TicketMessageInline]
    ordering = ('-updated_at',)


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'sender', 'is_admin_message', 'created_at')
    list_filter = ('is_admin_message', 'created_at')
    search_fields = ('content', 'ticket__subject', 'sender__username')
    ordering = ('-created_at',)
