from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from django.urls import reverse_lazy
from .forms import LoginForm


class UserLoginView(LoginView):
    """
    Handles user login using the custom styled LoginForm.
    """
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return reverse_lazy('dashboard:index')


class UserLogoutView(View):
    """
    Handles logging out the user and redirecting to the login screen.
    Supports GET request logout for developer/operator convenience.
    """
    def get(self, request):
        logout(request)
        return redirect('accounts:login')

    def post(self, request):
        logout(request)
        return redirect('accounts:login')
