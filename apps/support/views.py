import asyncio
import json
import redis
import redis.asyncio as aioredis
from asgiref.sync import sync_to_async

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import SupportTicket, TicketMessage


def publish_ticket_event(ticket_id, event_data):
    """Publish real-time ticket event to Redis channel"""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.publish(f"ticket_{ticket_id}", json.dumps(event_data, ensure_ascii=False))
    except Exception as e:
        pass


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
            msg = TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=message_content,
                attachment_url=attachment_url or None,
                is_admin_message=request.user.is_staff
            )
            messages.success(request, f'تم فتح تذكرة الدعم رقم #{ticket.id} بنجاح! سيقوم فريق الدعم بالرد قريباً.')
            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'support/tickets_list.html', {
        'tickets': tickets,
    })


@login_required
def ticket_detail_view(request, ticket_id):
    """View ticket conversation and post replies"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    if ticket.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    messages_list = ticket.messages.select_related('sender').order_by('created_at')

    if request.method == 'POST':
        reply_content = request.POST.get('content', '').strip()
        attachment_url = request.POST.get('attachment_url', '').strip()

        if reply_content:
            is_staff = request.user.is_staff
            msg = TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=reply_content,
                attachment_url=attachment_url or None,
                is_admin_message=is_staff
            )
            if is_staff and ticket.status == 'Open':
                ticket.status = 'InProgress'
                ticket.save(update_fields=['status', 'updated_at'])
            elif not is_staff and ticket.status == 'Closed':
                ticket.status = 'Open'
                ticket.save(update_fields=['status', 'updated_at'])
            else:
                ticket.save(update_fields=['updated_at'])

            # Publish real-time SSE event via Redis
            event_data = {
                'id': msg.id,
                'sender': msg.sender.username if msg.sender else 'User',
                'is_admin': msg.is_admin_message,
                'content': msg.content,
                'attachment_url': msg.attachment_url,
                'created_at': msg.created_at.strftime('%d %b %Y %H:%M'),
                'ticket_status': ticket.status,
                'status_display': ticket.get_status_display(),
            }
            publish_ticket_event(ticket.id, event_data)

            # AJAX response support
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
                return JsonResponse({'success': True, 'message': event_data})

            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'messages': messages_list,
    })


@sync_to_async
def check_ticket_access(request, ticket_id):
    """Synchronously verify authentication and permission in worker thread"""
    if not request.user.is_authenticated:
        return False, "Authentication required"
    try:
        ticket = SupportTicket.objects.select_related('user').get(id=ticket_id)
        if ticket.user_id != request.user.id and not request.user.is_staff:
            return False, "Access denied"
        return True, None
    except SupportTicket.DoesNotExist:
        return False, "Ticket not found"


async def ticket_events_stream(request, ticket_id):
    """Server-Sent Events (SSE) stream for real-time ticket updates"""
    has_access, error_msg = await check_ticket_access(request, ticket_id)
    if not has_access:
        return HttpResponseForbidden(error_msg or "Access denied")

    async def event_generator():
        r = aioredis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        channel = f"ticket_{ticket_id}"
        await pubsub.subscribe(channel)
        yield ": connected\n\n"
        try:
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=10.0)
                if msg and msg.get('type') == 'message':
                    data = msg.get('data')
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    yield f"data: {data}\n\n"
                else:
                    yield ": ping\n\n"
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            try:
                await pubsub.unsubscribe(channel)
                await r.aclose()
            except Exception:
                pass

    response = StreamingHttpResponse(event_generator(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
