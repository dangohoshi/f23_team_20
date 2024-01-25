from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


def deprecated(func):
    """
    This notation marks the current function as deprecated.
    """
    def ret(*args, **kwargs):
        print('Warning: this function is deprecated')
        return func(*args, **kwargs)

    return ret


def post_required(func):
    """
    This notation marks the function as POST only.
    """
    def ret(*args, **kwargs):
        if len(args) == 0:
            print('Warning: this notation requires the function to take one argument')
            return func(*args, **kwargs)
        request = args[0]
        if not isinstance(request, WSGIRequest):
            print('Warning: the first argument must be request')
            return func(*args, **kwargs)
        if request.method != 'POST':
            return render(request, 'errors/405.html', status=405)
        return func(*args, **kwargs)

    return ret


@csrf_exempt
@deprecated
@post_required
def register(request):
    """
    URI: ~/register
    Method: POST(csrf suppressed)

    This is only for pre-developing, and should be deprecated as long as the OAuth is integrated into the web application.
    """

    username = request.POST['username']
    password = request.POST['password']
    try:
        user = User.objects.create_user(username=username, password=password)
        user.save()
    except IntegrityError:
        return render(request, 'errors/409.html', status=409)

    login(request, user)
    return redirect(reverse('to-do'))


@csrf_exempt
@deprecated
@post_required
def sign_in(request):
    """
    URI: ~/sign-in
    Method: POST(csrf suppressed)

    This is only for pre-developing, and should be deprecated as long as the OAuth is integrated into the web application.
    """

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(request, 'errors/errorpage.html', status=403)

    login(request=request, user=user)
    return redirect(reverse('to-do'))


@csrf_exempt
@deprecated
@login_required
def sign_out(request):
    logout(request.user)
    return redirect(reverse('to-do'))
