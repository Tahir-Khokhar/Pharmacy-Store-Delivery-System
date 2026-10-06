from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Notification

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })


@login_required
@require_POST
def mark_notification_read_ajax(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        'success': True,
        'unread_count': unread_count
    })


@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')
