from .models import Category, UserNotification

def categories(request):
    context = {'categories': Category.objects.all()}

    if request.user.is_authenticated:
        notifications = UserNotification.objects.filter(user=request.user)
        context.update({
            'user_notifications': notifications[:5],
            'unread_notification_count': notifications.filter(is_read=False).count(),
        })
    else:
        context.update({
            'user_notifications': [],
            'unread_notification_count': 0,
        })

    return context
