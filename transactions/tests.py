from django.test import TestCase

# Create your tests here.

def fingerprint_register(request):
    # pylint: disable=too-many-statements

    if request.method == 'POST':
        location = request.POST.get('location')
        location = int(location)
        
        uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

        """Take 2 finger images and template it, then store in 'location'"""
        user_id = request.user.id
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Place finger on sensor..."})
                
            else:
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Place same finger again..."})
                

            while True:
                i = finger.get_image()

                if i == adafruit_fingerprint.OK:
                    Status.objects.update_or_create(user_id=user_id,
                                    defaults={'status':"Image taken"})
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    print('.', end="")
                    
                else:
                    response_data['status'] = "An error occurred"
                    # Status.objects.update_or_create(user_id=user_id,
                    #                 defaults={'status':"An error occurred"})
                    return False
                
            Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Templating..."})
            
            i = finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                Status.objects.update_or_create(user_id=user_id,
                                                defaults={'status':"Templated"})
                
                print("Templated")
            else:
                Status.objects.update_or_create(user_id=user_id,
                                                defaults={'status':"An error occurred"})
                
                return JsonResponse(response_data, safe=False)

            if fingerimg == 1:
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Remove finger"})
                
                while i != adafruit_fingerprint.NOFINGER:
                    i = finger.get_image()

            Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Creating model..."})
            
        i = finger.create_model()
        if i == adafruit_fingerprint.OK:
            Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"Created"})
            
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"Prints did not match"})
                
            else:
                Status.objects.update_or_create(user_id=user_id,
                            defaults={'status':"An error occurred"})
                    

            print("Storing model #%d..." % location, end="")
            Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Storing model"})
            
            i = finger.store_model(location)
            if i == adafruit_fingerprint.OK:
                Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Stored"})
            else:
                if i == adafruit_fingerprint.BADLOCATION:
                    Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Bad storage location"})
                elif i == adafruit_fingerprint.FLASHERR:
                    Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Flash storage error"})
                else:
                    Status.objects.update_or_create(user_id=user_id,
                                defaults={'status':"Other error"})

        response_data['location'] = user_id
        response_data['status'] = Status.objects.get(user_id=user_id).status
        return JsonResponse(response_data, safe=False)