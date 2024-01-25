from cryptography.fernet import Fernet, InvalidToken
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from lifesync.todo.models import ToDoList, ToDoItem
from lifesync.utils import post_required
from lifesync.views import set_default_preferences


@login_required
def get_to_do_lists(request):
    """
    URI: ~/
    Method: GET

    This function returns the to-do list for the current user.

    A user could have multiple to-do lists, and a to-do list could be shared among different users.

    For more details, refer to models.ToDoList.
    """
    lists = ToDoList.objects.filter(users=request.user)

    rows = []
    for to_do_list in lists:
        row = {
            'name': to_do_list.name,
            'date': to_do_list.date,
            'description': to_do_list.description,
            'id': str(to_do_list.id),
            'uri': '/to-do/' + str(to_do_list.id) + '/',
            'drop_uri': '/to-do/drop/' + str(to_do_list.id) + '/',
        }
        rows.append(row)

    return render(request, 'to-do/home.html', context={'rows': rows, 'userPreferences': set_default_preferences(request)})


@login_required
def view_to_do_list(request, id):
    """
    URI: ~/<to_do_list_id>
    """
    try:
        to_do_list = ToDoList.objects.get(id=id)
        if request.user not in to_do_list.users.all():
            return render(request, 'errors/403.html', status=403)
    except ToDoList.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    items = to_do_list.items.all()
    rows = []
    for item in items:
        row = {
            'id': item.id,
            'status': 'checked' if item.status else '',
            'deadline': item.deadline,
            'item': item.item,
            'delete_uri': '/to-do/delete/' + str(item.id) + '/',
        }
        rows.append(row)

    context = {'rows': rows, 'name': to_do_list.name, 'date': to_do_list.date, 'description': to_do_list.description,
               'id': to_do_list.id, 'share_uri': '/to-do/share/'
                                                 + str(to_do_list.id) + '?pwd='
                                                 + Fernet(key=to_do_list.key).encrypt(b'share').decode(),
               'userPreferences': set_default_preferences(request)}

    return render(request, 'to-do/list.html', context=context)


@login_required
@post_required
def create_to_do_list(request):
    """
    URI: ~/create
    Method: POST(csrf suppressed)

    This function creates a new to-do list. By default, only the user creating the list could
    """
    keywords = {'name', 'description'}
    for keyword in keywords:
        if keyword not in request.POST:
            return render(request, 'errors/400.html', status=400)
    user = request.user
    name = request.POST['name']
    if name == "":
        return render(request, 'errors/400.html', status=400, context={'message': 'Name cannot be empty'})
    date = timezone.now()
    description = request.POST['description']
    key = Fernet.generate_key()

    try:
        to_do_list = ToDoList()
        to_do_list.name = name
        to_do_list.date = date
        to_do_list.description = description
        to_do_list.key = key
        to_do_list.save()
        to_do_list.users.add(user)
    except IntegrityError as e:
        print('Unable to save ToDoList object:', e, sep='\n')

    return redirect(reverse('to-do'))


@login_required
@post_required
def add_to_do_item(request, id):
    """
    URI: ~/add/<to_do_list_id>
    Method: POST(csrf suppressed)

    This function creates a new to-do item.
    """

    try:
        to_do_list = ToDoList.objects.get(id=id)
    except ToDoList.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    keywords = {'deadline', 'item'}
    for keyword in keywords:
        if keyword not in request.POST:
            return render(request, 'errors/400.html', status=400)

    status = False
    deadline = request.POST['deadline']

    if deadline == "":
        return render(request, 'errors/400.html', status=400, context={"message": "deadline cannot be empty"})

    item = request.POST['item']
    if 'usernames' in request.POST:
        usernames = request.POST['usernames'].split(',')
    else:
        usernames = [request.user]
    users = [User.objects.get(username=username) for username in usernames]

    try:
        to_do_item = ToDoItem()
        to_do_item.status = status
        to_do_item.deadline = deadline
        to_do_item.item = item
        to_do_item.save()

        to_do_item.users.add(*users)

        to_do_list.items.add(to_do_item)
    except IntegrityError as e:
        print(e)

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@post_required
def drop_to_do_list(request, id):
    """
    URI: ~/drop/<to_do_list_id>
    Method: POST(csrf suppressed)

    This function drops an existing to-do list, and ignores non-existing to-do lists.
    """

    try:
        to_do_list = ToDoList.objects.get(id=id)
    except ToDoList.DoesNotExist:
        return redirect(reverse('to-do'))

    # Maybe only the creator can delete it?
    if not to_do_list.users.contains(request.user):
        return render(request, 'errors/403.html', status=403)

    to_do_list.delete()
    return redirect(reverse('to-do'))


@login_required
@post_required
def delete_to_do_item(request, id):
    """
    URI: ~/delete/<to_do_list_id>
    Method: POST(csrf suppressed)

    This function deletes an existing to-do item, and ignores non-existing to-do items.
    """

    try:
        to_do_item = ToDoItem.objects.get(id=id)
    except ToDoItem.DoesNotExist:
        return redirect(reverse('to-do'))

    # Maybe only the creator can delete it?
    if not to_do_item.users.contains(request.user):
        return render(request, 'errors/403.html', status=403)

    to_do_item.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@post_required
def edit_to_do_list(request, id):
    """
    URI: ~/edit/<to_do_list_id>
    Method: POST(csrf suppressed)
    """
    try:
        to_do_list = ToDoList.objects.get(id=id)
    except ToDoList.DoesNotExist:
        return redirect(request.META.get('HTTP_REFERER'))

    keywords = {'name', 'description'}
    for keyword in keywords:
        if keyword not in request.POST:
            return render(request, 'errors/400.html', status=400)

    name = request.POST['name']
    if name == "":
        return render(request, 'errors/400.html', status=400)
    description = request.POST['description']

    to_do_list.name = name
    to_do_list.date = timezone.now()
    to_do_list.description = description
    to_do_list.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@post_required
def update_to_do_item(request, id):
    """
    URI: ~/update/<to_do_item_id>
    Method: POST(csrf suppressed)
    """
    try:
        to_do_item = ToDoItem.objects.get(id=id)
    except ToDoItem.DoesNotExist:
        return redirect(request.META.get('HTTP_REFERER'))

    keywords = {'status', 'deadline', 'item'}
    for keyword in keywords:
        if keyword not in request.POST:
            return render(request, 'errors/400.html', status=400)

    status = request.POST['status']
    deadline = request.POST['deadline']
    item = request.POST['item']

    to_do_item.status = status == 'true'
    to_do_item.deadline = deadline
    to_do_item.item = item
    to_do_item.save()

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def share_to_do_list(request, id):
    """
    URI: ~/share/<to_do_list_id>?pwd=<password>
    Method: GET

    This method register the current user to the to-do list
    """
    try:
        to_do_list = ToDoList.objects.get(id=id)
    except ToDoList.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    user = request.user
    if 'pwd' not in request.GET:
        return render(request, 'errors/404.html', status=404)

    pwd = request.GET.get('pwd')
    key = to_do_list.key

    fernet = Fernet(key=key)
    try:
        plain = fernet.decrypt(bytes(pwd, 'utf-8')).decode()
    except InvalidToken:
        return render(request, 'errors/403.html', status=403)

    if plain != 'share':
        return render(request, 'errors/403.html', status=403)

    to_do_list.users.add(user)
    return redirect(reverse('to-do'))
