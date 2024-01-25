from allauth.socialaccount.signals import social_account_updated
from django.dispatch import receiver

@receiver(social_account_updated)
def social_account_updated_receiver(request, sociallogin, **kwargs):
    # Check if it's a Google account

    if sociallogin.account.provider == 'google' or 'Google':
        # Get the access and refresh tokens
        print(sociallogin)
        access_token = sociallogin.token.token
        refresh_token = sociallogin.token.token_secret

        # Store tokens in the user's session
        request.session['google_oauth_tokens'] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    else:
        print("Not google")



        