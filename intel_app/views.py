import hashlib
import hmac
import json
from datetime import datetime

from decouple import config
from django.contrib.auth.forms import PasswordResetForm
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import requests
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt

from . import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import helper, models
from .forms import UploadFileForm
from .models import CustomUser


# Create your views here.
def home(request):
    if models.Announcement.objects.filter(active=True).exists():
        announcement = models.Announcement.objects.filter(active=True).first()
        messages.info(request, announcement.message)
        return render(request, "layouts/index.html")
    return render(request, "layouts/index.html")


def services(request):
    return render(request, "layouts/services.html")


@login_required
def pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone_number")
        amount = request.POST.get("offers")
        reference = request.POST.get("reference")
        network = 'at'


        print(reference)

        # Validate the form data
        form = forms.IShareBundleForm(data=request.POST, status=user.status)
        if not form.is_valid():
            messages.error(request, 'Invalid form submission. Please correct the errors and try again.')
            return redirect('airtel-tigo')

        # Check if the user has sufficient wallet balance
        if user.wallet is None or user.wallet <= 0 or user.wallet < float(amount):
            messages.error(request, 'Your wallet balance is low. Contact the admin to recharge.')
            return redirect('airtel-tigo')

        # Determine bundle volume based on user status and amount
        try:
            if user.status == "User":
                bundle_obj = models.IshareBundlePrice.objects.get(price=float(amount))
            elif user.status == "Agent":
                bundle_obj = models.AgentIshareBundlePrice.objects.get(price=float(amount))
            elif user.status == "Super Agent":
                bundle_obj = models.SuperAgentIshareBundlePrice.objects.get(price=float(amount))
            else:
                bundle_obj = models.IshareBundlePrice.objects.get(price=float(amount))
            bundle_volume = bundle_obj.bundle_volume
        except models.IshareBundlePrice.DoesNotExist:
            messages.error(request, 'Invalid bundle amount selected.')
            return redirect('airtel-tigo')

        # Start atomic transaction
        with transaction.atomic():
            # Call the send_bundle function
            send_bundle_response = helper.send_bundle(user, network, bundle_volume, reference, phone_number)
            try:
                data = send_bundle_response.json()
            except ValueError:
                messages.error(request, 'Invalid response from the bundle service.')
                return redirect('airtel-tigo')

            # Check if the transaction was successful
            if send_bundle_response.status_code == 200 and data.get("status") == True:
                # Deduct amount from user's wallet
                user.wallet -= float(amount)
                user.save()

                # Create a new transaction record
                models.IShareBundleTransaction.objects.create(
                    user=user,
                    bundle_number=phone_number,
                    amount=amount,
                    offer=f"{bundle_volume}MB",
                    reference=reference,
                    transaction_status="Completed",
                    transaction_date=datetime.now()
                )

                models.WalletTransaction.objects.create(
                    user=user,
                    transaction_type='Debit',
                    transaction_amount=amount,
                    transaction_use='AT Bundle Purchase',
                    new_balance=user.wallet,
                )

                # Send SMS notifications (optional)
                # You can uncomment and configure the SMS sending code here

                messages.success(request, 'Transaction completed successfully.')
                return redirect('airtel-tigo')  # Redirect to a success page
            else:
                # Transaction failed, do not deduct wallet
                models.IShareBundleTransaction.objects.create(
                    user=user,
                    bundle_number=phone_number,
                    offer=f"{bundle_volume}MB",
                    amount=amount,
                    reference=reference,
                    transaction_status="Failed",
                    description=data.get("message", "Transaction failed"),
                    transaction_date=datetime.now()
                )
                messages.error(request, 'Transaction failed. Please try again later.')
                return redirect('airtel-tigo')
    else:
        return redirect('airtel-tigo')


@login_required(login_url='login')
def airtel_tigo(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    status = user.status
    form = forms.IShareBundleForm(status=status)
    reference = helper.ref_generator()
    wallet_balance = user.wallet or 0.0

    context = {
        "form": form,
        "ref": reference,
        "email": user.email,
        "wallet": wallet_balance,
    }
    return render(request, "layouts/services/at.html", context=context)


@login_required
def mtn_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone_number")
        amount = request.POST.get("offers")
        reference = request.POST.get("reference")
        network = 'mtn'

        # Validate the form data
        form = forms.MTNForm(data=request.POST, status=user.status)
        if not form.is_valid():
            messages.error(request, 'Invalid form submission. Please correct the errors and try again.')
            return redirect('mtn')

        # Check if the user has sufficient wallet balance
        if user.wallet is None or user.wallet <= 0 or user.wallet < float(amount):
            messages.error(request, 'Your wallet balance is low. Contact the admin to recharge.')
            return redirect('mtn')

        # Determine bundle volume based on user status and amount
        try:
            if user.status == "User":
                bundle_obj = models.MTNBundlePrice.objects.get(price=float(amount))
            elif user.status == "Agent":
                bundle_obj = models.AgentMTNBundlePrice.objects.get(price=float(amount))
            elif user.status == "Super Agent":
                bundle_obj = models.SuperAgentMTNBundlePrice.objects.get(price=float(amount))
            else:
                bundle_obj = models.MTNBundlePrice.objects.get(price=float(amount))
            bundle_volume = bundle_obj.bundle_volume
        except models.MTNBundlePrice.DoesNotExist:
            messages.error(request, 'Invalid bundle amount selected.')
            return redirect('mtn')

        # Start atomic transaction
        with transaction.atomic():
            # Call the send_bundle function
            send_bundle_response = helper.send_bundle(user, network, bundle_volume, reference, phone_number)
            try:
                data = send_bundle_response.json()
            except ValueError:
                messages.error(request, 'Invalid response from the bundle service.')
                return redirect('mtn')

            # Check if the transaction was successful
            if send_bundle_response.status_code == 200 and data['data']['status'] is True:
                # Deduct amount from user's wallet
                user.wallet -= float(amount)
                user.save()

                # Create a new transaction record
                models.MTNTransaction.objects.create(
                    user=user,
                    bundle_number=phone_number,
                    offer=f"{bundle_volume}MB",
                    reference=reference,
                    amount=amount,
                    transaction_status="Completed",
                    transaction_date=datetime.now()
                )

                models.WalletTransaction.objects.create(
                    user=user,
                    transaction_type='Debit',
                    transaction_amount=amount,
                    transaction_use='MTN Bundle Purchase',
                    new_balance=user.wallet,
                )

                # Send SMS notifications (optional)
                # You can uncomment and configure the SMS sending code here

                messages.success(request, 'Transaction completed successfully.')
                return redirect('mtn')  # Redirect to a success page
            else:
                # Transaction failed, do not deduct wallet
                models.MTNTransaction.objects.create(
                    user=user,
                    bundle_number=phone_number,
                    offer=f"{bundle_volume}MB",
                    reference=reference,
                    amount=amount,
                    transaction_status="Failed",
                    description=data.get("message", "Transaction failed"),
                    transaction_date=datetime.now()
                )
                messages.error(request, 'Transaction failed. Please try again later.')
                return redirect('mtn')
    else:
        return redirect('mtn')


def telecel_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        print(phone_number)
        print(amount)
        print(reference)


        if user.wallet is None:
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse({'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        if user.status == "User":
            bundle = models.TelecelBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentTelecelBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentTelecelBundlePrice.objects.get(price=float(amount)).bundle_volume
        else:
            bundle = models.TelecelBundlePrice.objects.get(price=float(amount)).bundle_volume

        print(bundle)
        sms_message = f"An order has been placed. {bundle}MB for {phone_number}"

        with transaction.atomic():
            new_telecel_transaction = models.TelecelTransaction.objects.create(
                user=request.user,
                amount=amount,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=reference,
            )
            new_telecel_transaction.save()
            user.wallet -= float(amount)
            user.save()

            models.WalletTransaction.objects.create(
                user=user,
                transaction_type='Debit',
                transaction_amount=amount,
                transaction_use='Telecel Bundle Purchase',
                new_balance=user.wallet,
            )

        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('telecel')


@login_required(login_url='login')
def big_time_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        print(phone_number)
        print(amount)
        print(reference)
        if user.wallet is None:
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        if user.status == "User":
            bundle = models.BigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Agent":
            bundle = models.AgentBigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        elif user.status == "Super Agent":
            bundle = models.SuperAgentBigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        else:
            bundle = models.BigTimeBundlePrice.objects.get(price=float(amount)).bundle_volume
        print(bundle)
        with transaction.atomic():
            new_mtn_transaction = models.BigTimeTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                amount=amount,
                offer=f"{bundle}MB",
                reference=reference,
            )
            new_mtn_transaction.save()
            user.wallet -= float(amount)
            user.save()

            models.WalletTransaction.objects.create(
                user=user,
                transaction_type='Debit',
                transaction_amount=amount,
                transaction_use='Big Time Bundle Purchase',
                new_balance=user.wallet,
            )
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('big_time')


@login_required(login_url='login')
def mtn(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    status = user.status
    form = forms.MTNForm(status=status)
    reference = helper.ref_generator()
    wallet_balance = user.wallet or 0.0

    context = {
        "form": form,
        "ref": reference,
        "email": user.email,
        "wallet": wallet_balance,
    }
    return render(request, "layouts/services/mtn.html", context=context)


@login_required(login_url='login')
def telecel(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    status = user.status
    form = forms.TelecelForm(status=status)
    reference = helper.ref_generator()
    user_email = request.user.email

    user = models.CustomUser.objects.get(id=request.user.id)
    phone_num = user.phone

    context = {'form': form, 'phone_num': phone_num,
               "ref": reference, "email": user_email, "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/voda.html", context=context)


@login_required(login_url='login')
def afa_registration(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    reference = helper.ref_generator()
    db_user_id = request.user.id
    price = models.AdminInfo.objects.filter().first().afa_price
    user_email = request.user.email
    print(price)

    form = forms.AFARegistrationForm()
    context = {'form': form, 'ref': reference, 'price': price, 'id': db_user_id, "email": user_email,
               "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/afa.html", context=context)


def afa_registration_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        name = request.POST.get("name")
        card_number = request.POST.get("card")
        occupation = request.POST.get("occupation")
        date_of_birth = request.POST.get("birth")
        price = models.AdminInfo.objects.filter().first().afa_price

        if user.wallet is None:
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})


        with transaction.atomic():
            new_registration = models.AFARegistration.objects.create(
                user=user,
                reference=reference,
                amount=float(price),
                name=name,
                phone_number=phone_number,
                gh_card_number=card_number,
                occupation=occupation,
                date_of_birth=date_of_birth
            )
            new_registration.save()
            user.wallet -= float(price)
            user.save()

            models.WalletTransaction.objects.create(
                user=user,
                transaction_type='Debit',
                transaction_amount=price,
                transaction_use='AT Bundle Purchase',
                new_balance=user.wallet,
            )
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('home')


@login_required(login_url='login')
def big_time(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    status = user.status
    form = forms.BigTimeBundleForm(status)
    reference = helper.ref_generator()
    db_user_id = request.user.id
    user_email = request.user.email


    user = models.CustomUser.objects.get(id=request.user.id)

    context = {'form': form,
               "ref": reference, "email": user_email, 'id': db_user_id,
               "wallet": 0 if user.wallet is None else user.wallet}
    return render(request, "layouts/services/big_time.html", context=context)


@login_required(login_url='login')
def history(request):
    user_transactions = models.IShareBundleTransaction.objects.filter(user=request.user).order_by('transaction_date').reverse()[:200]
    header = "AirtelTigo Transactions"
    net = "tigo"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def mtn_history(request):
    user_transactions = models.MTNTransaction.objects.filter(user=request.user).order_by('transaction_date').reverse()[:300]
    header = "MTN Transactions"
    net = "mtn"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def telecel_history(request):
    user_transactions = models.TelecelTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()[:300]
    header = "Telecel Transactions"
    net = "telecel"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def big_time_history(request):
    user_transactions = models.BigTimeTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()[:300]
    header = "Big Time Transactions"
    net = "bt"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def afa_history(request):
    user_transactions = models.AFARegistration.objects.filter(user=request.user).order_by('transaction_date').reverse()[:200]
    header = "AFA Registrations"
    net = "afa"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/afa_history.html", context=context)


@login_required(login_url='login')
def topup_info(request):
    admin_info = models.AdminInfo.objects.first()
    paystack_active = admin_info.paystack_active if admin_info else False

    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        reference = helper.top_up_ref_generator()
        amount_in_pesewas = int(float(amount) * 100)  # Convert amount to pesewas (assuming GHS)

        if paystack_active:
            # Proceed with Paystack payment
            paystack_secret_key = config("PAYSTACK_SECRET_KEY")
            # paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
            headers = {
                'Authorization': f'Bearer {paystack_secret_key}',
                'Content-Type': 'application/json',
            }
            data = {
                'email': user.email,
                'amount': amount_in_pesewas,
                'reference': reference,
                'metadata': {
                    'user_id': user.id,
                    'reference': reference,
                    'real_amount': amount,
                    'channel': 'topup',
                },
                'callback_url': request.build_absolute_uri(reverse('home')),  # Adjust callback URL as needed
            }
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=data)
            res_data = response.json()
            if res_data.get('status'):
                authorization_url = res_data['data']['authorization_url']
                # Create a TopUpRequest with status Pending
                models.TopUpRequest.objects.create(
                    user=user,
                    amount=amount,
                    reference=reference,
                    status='Pending',
                    payment_channel='Paystack',
                )
                return redirect(authorization_url)
            else:
                messages.error(request, 'An error occurred while initializing payment. Please try again.')
                return redirect('topup_info')
        else:
            # Proceed as before
            admin_phone = admin_info.phone_number if admin_info else 'ADMIN_PHONE_NUMBER'
            new_topup_request = models.TopUpRequest.objects.create(
                user=user,
                amount=amount,
                reference=reference,
                status='Pending',
                payment_channel='Paystack',
            )
            messages.success(request,
                             f"Your Request has been sent successfully.")
            return redirect("request_successful", reference)
    else:
        return render(request, "layouts/topup-info.html")


@login_required(login_url='login')
def request_successful(request, reference):
    admin = models.AdminInfo.objects.filter().first()
    context = {
        "name": admin.name,
        "number": f"0{admin.momo_number}",
        "channel": admin.payment_channel,
        "reference": reference
    }
    return render(request, "layouts/services/request_successful.html", context=context)


@csrf_exempt
def paystack_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)  # Method Not Allowed

    # Verify Paystack signature
    paystack_secret_key = config("PAYSTACK_SECRET_KEY")
    paystack_signature = request.headers.get('X-Paystack-Signature', '')
    computed_signature = hmac.new(
        key=paystack_secret_key.encode('utf-8'),
        msg=request.body,
        digestmod=hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, paystack_signature):
        return HttpResponse(status=400)  # Bad Request

    # Parse the request body
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)  # Bad Request

    event = payload.get('event')
    data = payload.get('data', {})

    if event == 'charge.success':
        metadata = data.get('metadata', {})
        user_id = metadata.get('user_id')
        reference = data.get('reference')
        channel = metadata.get('channel')
        real_amount = metadata.get('real_amount')

        if channel != 'topup':
            return HttpResponse(status=200)  # Not a top-up transaction

        # Get the user
        try:
            user = models.CustomUser.objects.get(id=int(user_id))
        except (models.CustomUser.DoesNotExist, ValueError):
            return HttpResponse(status=200)  # User not found

        # Get payment details
        paid_amount_kobo = data.get('amount')
        if not paid_amount_kobo or not reference:
            return HttpResponse(status=400)  # Bad Request

        # Convert amounts
        paid_amount = float(paid_amount_kobo) / 100  # Convert from kobo/pesewas to GHS
        real_amount = float(real_amount)

        # Validate the amount
        amount_difference = abs(paid_amount - real_amount)
        if amount_difference > 1.0:
            # Possible tampering detected
            return HttpResponse(status=200)

        # Check if this transaction has already been processed
        if models.TopUpRequest.objects.filter(reference=reference, status='Completed').exists():
            return HttpResponse(status=200)

        with transaction.atomic():
            # Update user's wallet
            user.wallet = (user.wallet or 0) + real_amount
            user.save()

            # Update TopUpRequest
            try:
                topup_request = models.TopUpRequest.objects.get(reference=reference)
                topup_request.amount = real_amount
                topup_request.status = 'Completed'
                topup_request.payment_status = 'Success'
                topup_request.new_balance = user.wallet
                topup_request.time_credited = datetime.now()
                topup_request.save()
            except models.TopUpRequest.DoesNotExist:
                # Create a new TopUpRequest if it doesn't exist
                models.TopUpRequest.objects.create(
                    user=user,
                    reference=reference,
                    amount=real_amount,
                    status='Completed',
                    payment_channel='Paystack',
                    payment_status='Success',
                    new_balance=user.wallet,
                    time_credited=datetime.now(),
                )

            # Create WalletTransaction
            models.WalletTransaction.objects.create(
                user=user,
                transaction_type='Credit',
                transaction_amount=real_amount,
                transaction_use='Wallet Topup (Paystack)',
                new_balance=user.wallet,
            )

            # Optionally, send SMS notification
            sms_message = f"Your wallet has been credited with GHS{real_amount}.\nReference: {reference}"
            # Send SMS logic here (uncomment and configure as needed)
            # sms_headers = {
            #     'Authorization': 'Bearer YOUR_SMS_API_KEY',
            #     'Content-Type': 'application/json'
            # }
            # sms_url = 'https://sms.api.url/send'
            # sms_body = {
            #     'recipient': f"233{user.phone}",
            #     'sender_id': 'YOUR_SENDER_ID',
            #     'message': sms_message
            # }
            # response = requests.post(sms_url, headers=sms_headers, json=sms_body)

        return HttpResponse(status=200)
    else:
        # For other events, return 200 OK
        return HttpResponse(status=200)


def topup_list(request):
    if request.user.is_superuser:
        topup_requests = models.TopUpRequest.objects.all().order_by('date').reverse()[:500]
        context = {
            'requests': topup_requests,
        }
        return render(request, "layouts/services/topup_list.html", context=context)
    else:
        messages.error(request, "Access Denied")
        return redirect('home')




# def populate_custom_users_from_excel(request):
#     # Read the Excel file using pandas
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             excel_file = request.FILES['file']
#
#             # Process the uploaded Excel file
#             df = pd.read_excel(excel_file)
#             counter = 0
#             # Iterate through rows to create CustomUser instances
#             for index, row in df.iterrows():
#                 print(counter)
#                 # Create a CustomUser instance for each row
#                 custom_user = CustomUser.objects.create(
#                     first_name=row['first_name'],
#                     last_name=row['last_name'],
#                     username=str(row['username']),
#                     email=row['email'],
#                     phone=row['phone'],
#                     wallet=float(row['wallet']),
#                     status=str(row['status']),
#                     password1=row['password1'],
#                     password2=row['password2'],
#                     is_superuser=row['is_superuser'],
#                     is_staff=row['is_staff'],
#                     is_active=row['is_active'],
#                     password=row['password']
#                 )
#
#                 custom_user.save()
#
#                 # group_names = row['groups'].split(',')  # Assuming groups are comma-separated
#                 # groups = Group.objects.filter(name__in=group_names)
#                 # custom_user.groups.set(groups)
#                 #
#                 # if row['user_permissions']:
#                 #     permission_ids = [int(pid) for pid in row['user_permissions'].split(',')]
#                 #     permissions = Permission.objects.filter(id__in=permission_ids)
#                 #     custom_user.user_permissions.set(permissions)
#                 print("killed")
#                 counter = counter + 1
#             messages.success(request, 'All done')
#     else:
#         form = UploadFileForm()
#     return render(request, 'layouts/import_users.html', {'form': form})
#
#
# def delete_custom_users(request):
#     CustomUser.objects.all().delete()
#     return HttpResponseRedirect('Done')


from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            user = models.CustomUser.objects.filter(email=data).first()
            current_user = user
            if user:
                subject = "Password Reset Requested"
                email_template_name = "password/password_reset_message.txt"
                c = {
                    "name": user.first_name,
                    "email": user.email,
                    'domain': 'www.danwelstoregh.com',
                    'site_name': 'DanWel Store GH',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https',
                }
                email = render_to_string(email_template_name, c)

                sms_headers = {
                    'Authorization': 'Bearer 1320|DMvAzhkgqCGgsuDs6DHcTKnt8xcrFnD48HEiRbvr',
                    'Content-Type': 'application/json'
                }

                sms_url = 'https://webapp.usmsgh.com/api/sms/send'

                sms_body = {
                    'recipient': f"233{user.phone}",
                    'sender_id': 'DANWELSTORE',
                    'message': email
                }
                response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                print(response.text)
                # requests.get(
                #     f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=UnBzemdvanJyUGxhTlJzaVVQaHk&to=0{current_user.phone}&from=GEO_AT&sms={email}")

                return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})

@login_required
def wallet_transactions(request):
    user = request.user
    transactions = models.WalletTransaction.objects.filter(user=user).order_by('-transaction_date')[:300]
    wallet_balance = user.wallet
    context = {
        'transactions': transactions,
        'wallet_balance': wallet_balance,
    }
    return render(request, 'layouts/services/wallet_transactions.html', context)