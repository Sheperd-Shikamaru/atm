from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect, render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .forms import UserRegistrationForm, UserAddressForm, CustomLoginForm

from pyfingerprint.pyfingerprint import PyFingerprint
import adafruit_fingerprint
import time
import serial

User = get_user_model()


class UserRegistrationView(TemplateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse_lazy('transactions:transaction_report')
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(self.request.POST)
        address_form = UserAddressForm(self.request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            login(self.request, user)
            messages.success(
                self.request,
                (
                    f'Thank You For Creating A Bank Account. '
                    f'Your Account Number is {user.account.account_no}. '
                )
            )
            return HttpResponseRedirect(
                reverse_lazy('transactions:fingerprint_register')
            )

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs):
        if 'registration_form' not in kwargs:
            kwargs['registration_form'] = UserRegistrationForm()
        if 'address_form' not in kwargs:
            kwargs['address_form'] = UserAddressForm()

        return super().get_context_data(**kwargs)
    
def get_fingerprint(finger):

    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

    
def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        print(f"form = {form}")
        uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
        print(f"uart = {uart}")
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        print(f"finger = {finger}")
        
        if form.is_valid():
            email = form.cleaned_data['username']  # 'username' field is used for email
            password = form.cleaned_data['password']
            
            
            if get_fingerprint(finger):
                user_id=finger.finger_id
                print("Detected #", finger.finger_id, "with confidence", finger.confidence)
                user_obj = User.objects.filter(id=user_id).first()
                email = user_obj.email
                print("email = ",email)
                user = authenticate(request, email=email, password=password)
            else:
                user = None

            if user is not None:
                login(request, user)
                return redirect('transactions:transaction_report')  # Redirect using app namespace
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/user_login.html', {'form': form})


class UserLoginView(LoginView):
    # template_name='accounts/fingerprint.html'
    template_name='accounts/user_login.html'
    redirect_authenticated_user = False


class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)
