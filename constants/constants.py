MOVIES_BASE_URL = 'https://api.dev-cinescope.coconutqa.ru/'
AUTH_BASE_URL = 'https://auth.dev-cinescope.coconutqa.ru/'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

LOGIN_ENDPOINT = '/login'
REGISTER_ENDPOINT = '/register'

MOVIES_ENDPOINT = '/movies'

BROKEN_API_FILTERS = {'location', 'published'}