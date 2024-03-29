from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView

from transactions.constants import *
from transactions.forms import (
    DepositForm,
    TransactionDateRangeForm,
    WithdrawForm,
)

from django.shortcuts import redirect
from pyfingerprint.pyfingerprint import PyFingerprint

from transactions.models import Status, Transaction


################
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import serial

import adafruit_fingerprint
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# import board
# uart = busio.UART(board.TX, board.RX, baudrate=57600)


##################################################


def get_fingerprint():
    # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi and hardware UART:
    # uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi 3 with pi3-disable-bt
    # uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
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


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi and hardware UART:
    # uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi 3 with pi3-disable-bt
    # uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
        # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi and hardware UART:
    # uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi 3 with pi3-disable-bt
    # uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


def save_fingerprint_image(filename):
    # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi and hardware UART:
    # uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi 3 with pi3-disable-bt
    # uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
    """Scan fingerprint then save image to filename."""
    while finger.get_image():
        pass

    # let PIL take care of the image headers and file structure
    from PIL import Image  # pylint: disable=import-outside-toplevel

    img = Image.new("L", (256, 288), "white")
    pixeldata = img.load()
    mask = 0b00001111
    result = finger.get_fpdata(sensorbuffer="image")

    # this block "unpacks" the data received from the fingerprint
    #   module then copies the image data to the image placeholder "img"
    #   pixel by pixel.  please refer to section 4.2.1 of the manual for
    #   more details.  thanks to Bastian Raschke and Danylo Esterman.
    # pylint: disable=invalid-name
    x = 0
    # pylint: disable=invalid-name
    y = 0
    # pylint: disable=consider-using-enumerate
    for i in range(len(result)):
        pixeldata[x, y] = (int(result[i]) >> 4) * 17
        x += 1
        pixeldata[x, y] = (int(result[i]) & mask) * 17
        if x == 255:
            x = 0
            y += 1
        else:
            x += 1

    if not img.save(filename):
        return True
    return False


##################################################


def get_num(max_number):
    """Use input() to get a valid number from 0 to the maximum size
    of the library. Retry till success!"""
    i = -1
    while (i > max_number - 1) or (i < 0):
        try:
            i = int(input("Enter ID # from 0-{}: ".format(max_number - 1)))
        except ValueError:
            pass
    return i


class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None)
        })

        return context

#login
def fingerprint_auth(request):
    try:
        # Connect to the fingerprint sensor
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        # Search for a finger
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        return redirect('user_login')

    try:
        print('Waiting for finger...')

        # Wait that finger is read
        while ( f.readImage() == False ):
            pass

        # Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        # Searchs template
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if ( positionNumber == -1 ):
            print('No match found!')
            return redirect('user_login')
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            # Authenticate the user and allow access to protected resource
            request.session['authenticated'] = True
            return redirect('home')

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        return redirect('user_login')

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Money to Your Account'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        if not account.initial_deposit_date:
            now = timezone.now()
            next_interest_month = int(
                12 / account.account_type.interest_calculation_per_year
            )
            account.initial_deposit_date = now
            account.interest_start_date = (
                now + relativedelta(
                    months=+next_interest_month
                )
            )

        account.balance += amount
        account.save(
            update_fields=[
                'initial_deposit_date',
                'balance',
                'interest_start_date'
            ]
        )

        messages.success(
            self.request,
            f'R{amount} was deposited to your account successfully'
        )
        
        for i in range(5):
            GPIO.output(LED_PIN,True)
            GPIO.output(BUZZER_PIN,True)
            time.sleep(TIMER)
            
            GPIO.output(LED_PIN,False)
            GPIO.output(BUZZER_PIN,False)
            time.sleep(TIMER)

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money from Your Account'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn R{amount} from your account'
        )

        # loop through 5 times, on/off for .55 second
        for i in range(5):
            GPIO.output(LED_PIN,True)
            GPIO.output(BUZZER_PIN,True)
            time.sleep(TIMER)
            
            GPIO.output(LED_PIN,False)
            GPIO.output(BUZZER_PIN,False)
            time.sleep(TIMER)

        return super().form_valid(form)



def fingerprint_register(request):
    # pylint: disable=too-many-statements

    if request.method == 'POST':
        
        response_data = {}
        uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

        """Take 2 finger images and template it, then store in 'location'"""
        user_id = request.user.id
        location = int(user_id)
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                response_data['status'] = "Place finger on sensor..."
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Place finger on sensor..."})
                time.sleep(2)
                
                print("Place finger on sensor...", end="")
            else:
                response_data['status'] = "Place same finger again..."
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Place same finger again..."})
                time.sleep(2)
                
                print("Place same finger again...", end="")

            while True:
                i = finger.get_image()
                time.sleep(2)

                if i == adafruit_fingerprint.OK:
                    print("Image taken")
                    Status.objects.update_or_create(user_id=user_id,
                                    defaults={'status':"Image taken"})
                    time.sleep(1)
                    break
                
                if i == adafruit_fingerprint.NOFINGER:
                    print('.', end="")

                else:
                    response_data['status'] = "An error occurred"
                    # Status.objects.update_or_create(user_id=user_id,
                    #                 defaults={'status':"An error occurred"})
                    time.sleep(1)
                    return False
                
            print("Templating...", end="")
            Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Templating..."})
            time.sleep(1)
            
            i = finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                Status.objects.update_or_create(user_id=user_id,
                                                defaults={'status':"Templated"})
                time.sleep(1)
                
                print("Templated")
            else:
                response_data['status'] = "An error occurred"
                Status.objects.update_or_create(user_id=user_id,
                                                defaults={'status':"An error occurred"})
                time.sleep(2)
                
                return JsonResponse(response_data, safe=False)

            if fingerimg == 1:
                response_data['status'] = "Remove finger"
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Remove finger"})
                
                print("Remove finger")
                time.sleep(2)
                while i != adafruit_fingerprint.NOFINGER:
                    i = finger.get_image()

            response_data['status'] = "Creating model..."
            Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Creating model..."})
            time.sleep(1)
            
        print("Creating model...", end="")
        i = finger.create_model()
        if i == adafruit_fingerprint.OK:
            response_data['status'] = "Created"
            Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"Created"})
            
            print("Created")
            time.sleep(1)
            print("Storing model #%d..." % location, end="")
            Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Storing model"})
            time.sleep(2)
            
            i = finger.store_model(location)
            if i == adafruit_fingerprint.OK:
                print("Stored")
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Stored"})
                time.sleep(2)
            else:
                if i == adafruit_fingerprint.BADLOCATION:
                    print("Bad storage location")
                    Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Bad storage location"})
                    time.sleep(1)
                elif i == adafruit_fingerprint.FLASHERR:
                    print("Flash storage error")
                    Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Flash storage error"})
                    time.sleep(1)
                else:
                    print("Other error")
                    Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Other error"})
                    time.sleep(1)
            
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                response_data['status'] = "Prints did not match"
                Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"Prints did not match"})
                time.sleep(2)
                
                print("Prints did not match")
            else:
                response_data['status'] = "An error occurred"
                Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"An error occurred"})
                time.sleep(1)
                
        print("Storing model #%d..." % location, end="")
        Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"Storing model"})
        time.sleep(2)
        
        
        response_data['location'] = user_id
        response_data['status'] = Status.objects.get(user_id=user_id).status
        return JsonResponse(response_data, safe=False)
    
    return render(request, 'accounts/fingerprint.html')

def get_status(request):
    user_id = request.user.id
    try:
        status = Status.objects.get(user_id=user_id).status
    except Status.DoesNotExist:
        status = "No status"
    return JsonResponse({'status': status}, safe=False)
