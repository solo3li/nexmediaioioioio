from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import SupportTicket, TicketMessage


@login_required
def support_list_view(request):
    """Lists user tickets and handles new ticket creation"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-updated_at')

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message_content = request.POST.get('content', '').strip()
        attachment_url = request.POST.get('attachment_url', '').strip()

        if not subject or not message_content:
            messages.error(request, 'يرجى كتابة عنوان للتذكرة وتفاصيل المشكلة أو الاستفسار.')
        else:
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                status='Open'
            )
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=message_content,
                attachment_url=attachment_url or None,
                is_admin_message=False
            )
            messages.success(request, f'تم فتح تذكرة الدعم رقم #{ticket.id} بنجاح! سيقوم فريق الدعم بالرد قريباً.')
            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'support/tickets_list.html', {
        'tickets': tickets,
    })


@login_required
def ticket_detail_view(request, ticket_id):
    """View ticket conversation and post replies"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    messages_list = ticket.messages.select_related('sender').order_by('created_at')

    if request.method == 'POST':
        reply_content = request.POST.get('content', '').strip()
        attachment_url = request.POST.get('attachment_url', '').strip()

        if reply_content:
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=reply_content,
                attachment_url=attachment_url or None,
                is_admin_message=False
            )
            if ticket.status == 'Closed':
                ticket.status = 'Open'
                ticket.save(update_fields=['status', 'updated_at'])
            else:
                ticket.save(update_fields=['updated_at'])

            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'messages': messages_list,
    })
