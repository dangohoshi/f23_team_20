from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from lifesync.models import UserPreferences
from django.core.exceptions import ObjectDoesNotExist
from lifesync.utils import post_required


# Login redirects to placeholder page
def login_action(request):
    """
        URI: /
        Method: GET
        Load login page or homepage if logged in
    """
    context = {}
    if request.user.is_authenticated:
        context['userPreferences'] = set_default_preferences(request)
    return render(request, "homepage.html", context)


@login_required
def homepage(request):
    context = {'userPreferences': set_default_preferences(request)}
    return render(request, 'homepage.html', context)


@login_required
@post_required
def customize(request):
    """
        URI: /select-colors
        Method: POST
        Update the chosen user colors
    """
    if request.method == 'POST':

        # Handle missing input data
        if 'textColor' not in request.POST or 'navColor' not in request.POST:
            return render(request, 'errors/500.html', status=500)

        text_color = request.POST['textColor']
        navbar_color = request.POST['navColor']

        # Update or create user preferences
        UserPreferences.objects.update_or_create(
            user=request.user,
            defaults={'text_color': text_color, 'navbar_color': navbar_color}
        )
    return redirect('homepage')


@login_required
def select_colors(request):
    """
        URI: /select-colors
        Method: GET
        View color selection form
    """
    context = {'userPreferences': set_default_preferences(request)}
    return render(request, 'customize.html', context)


def set_default_preferences(request):
    """
        Method to update preferences on a page
    """
    try:
        # Check if preferences are updated
        user_preferences = UserPreferences.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Else, update to default values
        user_preferences = UserPreferences.objects.create(user=request.user)
    return user_preferences


def about(request):
    context = {}
    return render(request, 'about.html')
