import markdown
from cryptography.fernet import Fernet, InvalidToken
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from lifesync.notes.models import Category, Note
from lifesync.utils import post_required
from lifesync.views import set_default_preferences


EMAIL_ADDR = 'f23team20@gmail.com'


@login_required
def get_categories(request):
    """
    URI: ~/
    Method: GET
    """

    try:
        _ = Category.objects.get(users=request.user, name__exact='shared with me')
    except Category.DoesNotExist:
        category = Category()
        category.name = 'shared with me'
        category.description = 'Notes shared with me'
        category.created_time = timezone.now()
        category.save()
        category.users.add(request.user)

    rows = [
        {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'length': len(category.notes.all()),
        }
        for category in Category.objects.filter(users=request.user)
    ]
    return render(request, 'notes/home.html', context={'rows': rows, 'userPreferences': set_default_preferences(request)})


@post_required
@login_required
def add_category(request):
    """
    URI: ~/add
    Method: POST
    """
    keywords = {'name', 'description'}
    for keyword in keywords:
        if keyword not in request.POST:
            return render(request, 'errors/400.html', status=400)
    user = request.user
    name = request.POST['name']
    if name == "":
        return render(request, 'errors/400.html', status=400, context={'message': 'name cannot be empty'})
    time = timezone.now()
    description = request.POST['description']

    try:
        category = Category()
        category.name = name
        category.description = description
        category.created_time = time
        category.save()
        category.users.add(user)
    except IntegrityError as e:
        print('Unable to save NoteCategory:', e, sep='\n')

    return redirect(reverse('notes'))


@login_required
def view_category(request, id):
    """
    URI: ~/category/<int:id>
    Method: GET
    """
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    if request.user not in category.users.all():
        return render(request, 'errors/403.html', status=403)

    rows = [
        {
            'id': note.id,
            'name': note.name,
            'description': note.created_time,
        }
        for note in category.notes.all()
    ]
    return render(request, 'notes/category.html', context={'rows': rows, 'userPreferences': set_default_preferences(request)})


@post_required
@login_required
def create_note(request, id):
    """
    URI: ~/create/<int:id>
    Method: POST
    """
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    if request.user not in category.users.all():
        return render(request, 'errors/403.html', status=403)

    timestamp = timezone.now()

    keywords = {'name', 'description'}
    for keyword in keywords:
        if keyword not in request.POST:
            return render(request, 'errors/400.html', status=400)

    try:
        note = Note()
        note.name = request.POST['name']
        note.description = request.POST['description']
        note.created_time = timestamp
        note.latest_update_time = timestamp
        note.key = Fernet.generate_key()
        note.save()
        note.users.add(request.user)
        category.notes.add(note)
    except IntegrityError as e:
        print(e)
        return render(request, 'errors/500.html', status=500)

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def view_note(request, id):
    """
    URI: ~/view/<int:id>
    Method: POST
    """
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    if request.user not in note.users.all():
        return render(request, 'errors/403.html', status=403)

    context = {'id': id, 'parsed': markdown.markdown(note.content, extensions=['markdown.extensions.tables']),
               'content': note.content, 'share_uri': '/notes/share/'
                                                     + str(note.id) + '?pwd='
                                                     + Fernet(key=note.key).encrypt(b'share').decode(),
               'userPreferences': set_default_preferences(request)}

    return render(request, 'notes/note.html', context=context)


@login_required
def edit_note(request, id):
    """
    URI: ~/edit/<int:id>
    Method: POST
    """
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    if request.user not in note.users.all():
        return render(request, 'errors/403.html', status=403)

    if 'content' not in request.POST:
        return render(request, 'errors/400.html', status=400)

    try:
        note.content = request.POST['content']
        note.save()
    except IntegrityError as e:
        return render(request, 'errors/500.html', status=500)

    return redirect(request.META.get('HTTP_REFERER'))


@post_required
@login_required
def email(request):
    """
    URI: ~/email
    Method: POST
    """
    subject = f'[LifeSync] {request.user.username} sent you an invitation'
    message = (f'[LifeSync] {request.user.username} sent you an invitation, click the following link to view.\n'
               f'{request.scheme}://{request.get_host()}{request.POST["share_uri"]}')
    if 'email' not in request.POST:
        return render(request, 'errors/403.html', status=403)
    destination = [request.POST['email']]
    send_mail(subject, message, EMAIL_ADDR, destination)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def share(request, id):
    """
    URI: ~/share/<int:id>?pwd=<password>
    Method: GET
    """
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    user = request.user
    if 'pwd' not in request.GET:
        return render(request, 'errors/404.html', status=404)

    pwd = request.GET.get('pwd')
    key = note.key

    fernet = Fernet(key=key)
    try:
        plain = fernet.decrypt(bytes(pwd, 'utf-8')).decode()
    except InvalidToken:
        return render(request, 'errors/403.html', status=403)

    if plain != 'share':
        return render(request, 'errors/403.html', status=403)

    try:
        category = Category.objects.get(users=request.user, name__exact='shared with me')
    except Category.DoesNotExist:
        try:
            category = Category()
            category.name = 'shared with me'
            category.description = 'Notes shared with me'
            category.created_time = timezone.now()
            category.save()
            category.users.add(request.user)
        except IntegrityError:
            return render(request, 'errors/500.html', status=500)

    note.users.add(user)
    category.notes.add(note)

    return redirect(reverse('notes'))
