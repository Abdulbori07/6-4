import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'


def get_google_access_token(code):
    """Exchange an authorization code for a Google access token."""
    try:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                'code': code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code',
            },
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token') if isinstance(token_data, dict) else None
        if not access_token:
            raise AuthenticationFailed('Google не вернул access token.')
        return access_token
    except AuthenticationFailed:
        raise
    except (requests.RequestException, ValueError) as exc:
        raise AuthenticationFailed('Не удалось обменять код Google.') from exc


def get_google_user_info(access_token):
    """Fetch and validate the basic Google profile."""
    try:
        response = requests.get(
            GOOGLE_USER_INFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        response.raise_for_status()
        profile = response.json()
        if not isinstance(profile, dict):
            raise AuthenticationFailed('Google returned an invalid profile.')
        email = profile.get('email')
        if not email:
            raise AuthenticationFailed('Google профиль не содержит email.')
        return {'email': email, 'name': profile.get('name', '')}
    except AuthenticationFailed:
        raise
    except (requests.RequestException, ValueError) as exc:
        raise AuthenticationFailed('Не удалось получить профиль Google.') from exc

