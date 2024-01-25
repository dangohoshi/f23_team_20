from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldError
from django.shortcuts import render, redirect, reverse
from lifesync.expense.models import ExpenseItem
from django.utils import timezone
from django.db.models import Sum

from lifesync.utils import post_required
from lifesync.views import set_default_preferences


@login_required
def get_expense_home(request):
    """
        URI: /expense
        Method: GET
        View the expense addition form
    """
    context = {'added': request.session.pop('added', None),
               'categories': ['Food', 'Transportation', 'Housing', 'Entertainment', 'Shopping', 'Bills', 'Misc'],
               'userPreferences': set_default_preferences(request)}
    # Update added var to use in template
    return render(request, 'expense/expense_home.html', context)


@login_required
@post_required
def add_expense(request):
    """
        URI: /expense/add-expense
        Method: POST
        Add a new expense item
    """
    # Handle missing input data
    if 'expenseTitle' not in request.POST or 'expenseAmount' not in request.POST or 'expenseDescription' not in request.POST or 'expenseCategory' not in request.POST:
        return render(request, 'errors/400.html', status=400)

    # Handle incorrect expense category
    if request.POST['expenseCategory'] not in ['Food', 'Transportation', 'Housing', 'Entertainment', 'Shopping', 'Bills', 'Misc']:
        return render(request, 'errors/400.html', status=400)

    # Creating new expense item
    new_expense = ExpenseItem(expense_title=request.POST['expenseTitle'],
                              amount=request.POST['expenseAmount'],
                              created_time=timezone.now(),
                              description=request.POST['expenseDescription'],
                              category=request.POST['expenseCategory'],
                              user=request.user)
    new_expense.save()
    request.session['added'] = True
    request.session['expenseTitle'] = request.POST['expenseTitle']
    return redirect(reverse('expense'))


@login_required
def generate_report(request):
    """
        URI: /expense/report
        Method: GET
        Generate pie chart with expense category aggregates
    """
    context = {}

    # Get all categories and total amt sums for each category
    try:
        category_expense = (
            ExpenseItem.objects.filter(user=request.user).values('category')
            .annotate(total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        # Convert to array
        category_expense_array = [
            {'category': item['category'], 'total_amount': item['total_amount']}
            for item in category_expense
        ]
        context['category_expense'] = category_expense_array
    except FieldError:
        return render(request, 'errors/500.html', status=500)

    context['userPreferences'] = set_default_preferences(request)
    return render(request, 'expense/expense_report.html', context)


@login_required
def get_expense_table(request):
    """
        URI: /expense/view-expense
        Method: GET
        View all expense items in a tabular format
    """
    try:
        context = {'expense_items': ExpenseItem.objects.filter(user=request.user),
                   'userPreferences': set_default_preferences(request)}
    except FieldError:
        return render(request, 'errors/500.html', status=500)
    # Retrieve all expense items
    return render(request, 'expense/expense_table.html', context)


@login_required
@post_required
def delete_expense(request):
    """
        URI: /expense/delete-expense
        Method: POST
        Deletes the expense item based on id
    """
    # Handle missing input data
    if 'expenseId' not in request.POST:
        return render(request, 'errors/400.html', status=400)

    # Retrieve item to be deleted
    expense_id = request.POST['expenseId']
    try:
        expense_item = ExpenseItem.objects.get(id=expense_id)
        # Delete item
        expense_item.delete()
    except ExpenseItem.DoesNotExist:
        return render(request, 'errors/500.html', status=500)

    return redirect(reverse('view-expense'))
