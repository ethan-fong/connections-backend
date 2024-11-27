from django.shortcuts import redirect

class RedirectLoggedInUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is trying to access the login page and is already authenticated
        if request.path == '/backend/admin/' and request.user.is_authenticated:
            return redirect('/backend/admin-tools/')  # Redirect to your specific URL
        response = self.get_response(request)
        return response