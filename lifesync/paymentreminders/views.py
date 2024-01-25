from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldError
from django.shortcuts import render, redirect, reverse
from datetime import datetime, timedelta
from lifesync.paymentreminders.models import ReminderItem
from lifesync.utils import post_required
from lifesync.views import set_default_preferences


@login_required
def get_reminders_home(request):
    """
        URI: /reminders
        Method: GET
        View all payment reminders
    """
    context = {}

    today = datetime.now().date()
    week_from_today = today + timedelta(days=7)
    # Retrieve items that have due dates in 7 days
    try:
        payments = ReminderItem.objects.filter(
            user=request.user,
            due_date__range=[today, week_from_today]
        ).order_by('due_date')
    except FieldError:
        return render(request, 'errors/500.html', status=500)

    # Add them to context
    if payments:
        context['exist'] = True
        context['payments'] = payments
    context['userPreferences'] = set_default_preferences(request)
    return render(request, 'paymentreminders/reminders_home.html', context)


@login_required
def add_reminders_page(request):
    """
        URI: /reminders/add-reminder-page
        Method: GET
        View add reminders form
    """
    context = {'added': request.session.pop('added', None), 'error': request.session.pop('error', None),
               'userPreferences': set_default_preferences(request)}
    # Update added var to use in template
    return render(request, 'paymentreminders/reminders_add.html', context)


@login_required
@post_required
def add_reminder(request):
    """
        URI: /reminders/add-reminder
        Method: POST
        Add a new payment reminder
    """
    # Handle missing input data
    if 'paymentTitle' not in request.POST or 'amount' not in request.POST or 'paymentDescription' not in request.POST or 'paymentDueDate' not in request.POST:
        return render(request, 'errors/400.html', status=400)

    # Validate that due date is not in the past
    payment_due_date = datetime.strptime(request.POST['paymentDueDate'], '%Y-%m-%d').date()
    current_date = datetime.now().date()
    if payment_due_date < current_date:
        request.session['error'] = True
        request.session['errorMsg'] = 'The due date cannot be in the past.'
        return redirect(reverse('add-reminder-page'))

    # Creating new payment reminder
    new_reminder = ReminderItem(reminder_title=request.POST['paymentTitle'],
                                amount=request.POST['amount'],
                                due_date=request.POST['paymentDueDate'],
                                description=request.POST['paymentDescription'],
                                user=request.user)
    new_reminder.save()
    request.session['added'] = True
    request.session['paymentTitle'] = request.POST['paymentTitle']
    return redirect(reverse('add-reminder-page'))


@login_required
@post_required
def update_reminder(request):
    """
        URI: /reminders/paid
        Method: POST
        Delete a reminder that is paid
    """
    # Handle missing input data
    if 'paymentId' not in request.POST:
        return render(request, 'errors/400.html', status=400)

    # Retrieve item to be deleted
    payment_id = request.POST['paymentId']
    try:
        payment_item = ReminderItem.objects.get(id=payment_id)
        # Delete item
        payment_item.delete()
    except ReminderItem.DoesNotExist:
        return render(request, 'errors/500.html', status=500)

    return redirect(reverse('reminders'))
