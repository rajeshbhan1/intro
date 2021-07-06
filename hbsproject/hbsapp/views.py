from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count, Q, F, Avg
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import date
from .utils import *
from .forms import *
import requests


class ClientMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.context = {
            "roomtypes": ROOM_TYPE
        }
        return super(ClientMixin, self).dispatch(request, *args, **kwargs)


class ClientHomeView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["all_hotels"] = Hotel.objects.order_by("-id")
        context["popular_rooms"] = HotelRoom.objects.order_by("-view_count")
        return render(request, "clienttemplates/clienthome.html", context)


class ClientContactView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["contact_form"] = ContactForm
        return render(request, "clienttemplates/clientcontact.html", context)

    def post(self, request, *args, **kwargs):
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(
                request, "Thanks for contacting us. We will get back to you shortly.")
        else:
            messages.error(request, "Something went wrong...")
        return redirect("hbsapp:clienthome")


class ClientSearchView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        keyword = request.GET.get("keyword")
        context["searched_hotels"] = Hotel.objects.filter(
            Q(name__icontains=keyword) | Q(address__icontains=keyword))

        query_string = Q(hotel__name__icontains=keyword) | Q(hotel__address__icontains=keyword) | Q(room_type__icontains=keyword) | Q(
            room_type__icontains=keyword) | Q(room_code__icontains=keyword) | Q(description__icontains=keyword)

        context["searched_rooms"] = HotelRoom.objects.filter(query_string)

        return render(request, "clienttemplates/clientsearch.html", context)


class ClientHotelDetailView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            hotel = Hotel.objects.get(id=self.kwargs.get("pk"))
            context["hotel"] = hotel
            context["total_bookings"] = RoomBooking.objects.filter(
                hotel_room__hotel=hotel, booking_status="Confirmed")
        except Exception as e:
            print(e)
            messages.error(request, "Hotel not found..")
            return redirect("hbsapp:clienthome")
        return render(request, "clienttemplates/clienthoteldetail.html", context)


class ClientRoomDetailView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
            context["room"] = room
            context["options"] = [i+1 for i in range(room.maximum_capacity)]
            context["roombookingform"] = RoomBookingForm
            context["all_ratings"] = RoomBooking.objects.filter(hotel_room=room, rating__isnull=False)
            context["most_rated_rooms"] = HotelRoom.objects.annotate(rating=Avg("roombooking__rating")).order_by("-rating")[:2]
            room.view_count += 1
            room.save()
            return render(request, "clienttemplates/clientroomdetail.html", context)
        except Exception as e:
            print(e)
            messages.error(request, "Hotel not found.")
            return redirect("hbsapp:clienthome")


class ForgotPasswordView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        return render(request, "clienttemplates/forgotpassword.html", context)

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
            url = self.request.META['HTTP_HOST']
            text_content = 'Please Click the link below to reset your password. '
            html_content = url + "/reset-password/" + email + \
                "/" + password_reset_token.make_token(user) + "/"
            send_mail(
                'Please click this Password Reset Link to reset your password.',
              #  text_content + html_content,
             #   settings.EMAIL_HOST_USER,
             #   [email],
                fail_silently=False,
            )

            status = "success"
            message = "Reset link sent successfully"
            messages.success(
                request, "Password reset link has been sent to your email. Please check your email soon.")
        else:
            status = "failure"
            message = "The user with this email doesnot exists.."
        resp = {
            "status": status,
            "message": message
        }
        return JsonResponse(resp)


class ResetPasswordView(ClientMixin, View):

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(username=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            messages.email(request, "Something went wrong. Please try again.")
            return redirect(reverse("hbsapp:forgotpassword"))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.context
        return render(request, "clienttemplates/resetpassword.html", context)

    def post(self, request, *args, **kwargs):
        password = request.POST.get("password")
        email = self.kwargs.get("email")
        user = User.objects.get(username=email)
        user.set_password(password)
        user.save()
        messages.success(request, "Your password has been reset successfully. Please login to continue.")
        try:
            user.customer
            return redirect("hbsapp:customerlogin")
        except Exception as e:
            print(e)
            return redirect("hbsapp:adminlogin")


# customer views
class CustomerRegisterView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["registrationform"] = CustomerRegistrationForm
        return render(request, "clienttemplates/customerregister.html", context)

    def post(self, request, *args, **kwargs):
        context = self.context
        registrationform = CustomerRegistrationForm(request.POST)
        if registrationform.is_valid():
            email = registrationform.cleaned_data.get("email")
            password = registrationform.cleaned_data.get("password")
            mobile = registrationform.cleaned_data.get("mobile")
            first_name = registrationform.cleaned_data.get("first_name")
            last_name = registrationform.cleaned_data.get("last_name")
            address = registrationform.cleaned_data.get("address")
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(
                    email, email, password, first_name=first_name, last_name=last_name)
                Customer.objects.create(
                    user=user, mobile=mobile, address=address)
                login(request, user)
                messages.success(request, "You are registered successfully.")
                if "next" in request.GET:
                    next_url = request.GET.get("next")
                    return redirect(next_url)
                else:
                    return redirect("hbsapp:clienthome")
            else:
                context["registrationform"] = CustomerRegistrationForm
                context["error"] = "Invalid attempts"
                messages.error(request, "Invalid attempts to register...")
                return render(request, "clienttemplates/customerregister.html", context)
        else:

            context["registrationform"] = CustomerRegistrationForm
            context["error"] = "Invalid attempts"
            messages.error(request, "Invalid attempts to register.")
            return render(request, "clienttemplates/customerregister.html", context)


class CustomerLoginView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["loginform"] = LoginForm
        return render(request, "clienttemplates/customerlogin.html", context)

    def post(self, request, *args, **kwargs):
        loginform = LoginForm(request.POST, None)
        if loginform.is_valid():

            email = loginform.cleaned_data.get("email")
            password = loginform.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            try:
                customer = user.customer
                login(request, user)
                messages.success(request, "Successfully logged in.")
                if "next" in request.GET:
                    next_url = request.GET.get("next")
                    return redirect(next_url)
                else:
                    return redirect(reverse("hbsapp:clienthome"))
            except Exception as e:
                print(e)
                messages.error(request, "Invalid username or password..")
                context = {
                    "loginform": LoginForm,
                    "error": "Invalid username or password."
                }
                return render(request, "clienttemplates/customerlogin.html", context)
        else:
            context = {
                "loginform": LoginForm,
                "error": "Invalid username or password."
            }
            return render(request, "clienttemplates/customerlogin.html", context)


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Successfully logged out")
        return redirect("hbsapp:clienthome")


class CustomerRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.customer = request.user.customer
        except Exception as e:
            print(e)
            return redirect(reverse("hbsapp:customerlogin") + "?next=" + request.path)
        return super(CustomerRequiredMixin, self).dispatch(request, *args, **kwargs)


class CustomerRoomCheckView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
        booking_starts = request.GET.get("date")
        booking_for = date.fromisoformat(booking_starts)
        if booking_for >= timezone.now().date():
            rb = RoomBooking.objects.filter(
                hotel_room=room, booking_starts__lte=booking_starts, booking_ends__gte=booking_starts)
            if rb.exists():
                room_status = "unavailable"
            else:
                room_status = "available"
        else:
            room_status = "error"
        resp = {
            "status": room_status
        }
        return JsonResponse(resp)


class CustomerRoomBookingView(CustomerRequiredMixin, ClientMixin, View):
    def post(self, request, *args, **kwargs):
        try:

            room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
            context = self.context
            booking_form = RoomBookingForm(request.POST)
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.hotel_room = room
                booking.customer = request.user.customer
                booking.booking_status = "Pending"
                stay_days = booking_form.cleaned_data.get(
                    "booking_ends") - booking_form.cleaned_data.get("booking_starts")
                stay_days = 1 if stay_days.days == 0 else stay_days.days
                booking.amount = room.price * stay_days
                booking.save()
                if booking.payment_method.name in ["Khalti", "khalti"]:
                    request.session["booking_id"] = booking.id
                    return redirect(booking.payment_method.payment_url)
                else:
                    messages.success(request, "Room booking successful...")
                    return redirect(reverse("hbsapp:customerbookingdetail", kwargs={"pk": booking.id}) + "?b=s")
            else:
                messages.error(request, "Something went wrong..")
                return redirect("hbsapp:clientroomdetail", room_code=room.room_code, pk=room.id)
        except Exception as e:
            messages.error(request, "Room not found..")
            print(e)
            return redirect("hbsapp:clienthome")


class KhaltiRequestView(CustomerRequiredMixin, ClientMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            booking = RoomBooking.objects.get(
                id=request.session.get("booking_id"))
            context = self.context
            context["booking"] = booking
            return render(request, "clienttemplates/khaltirequest.html", context)
        except Exception as e:
            messages.error(request, "Invalid Request...")
            print(e)
            return redirect("hbsapp:clienthome")


class KhaltiVerifyView(CustomerRequiredMixin, ClientMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            booking = RoomBooking.objects.get(
                id=request.session.get("booking_id"))
            payment_method = booking.payment_method
            url = payment_method.payment_verify_url
            payload = {
                "token": request.POST.get("token"),
                "amount": request.POST.get("amount")
            }
            headers = {
                "Authorization": f"Key {payment_method.test_secret_key}"
            }

            response = requests.post(url, payload, headers=headers)
            resp_dict = response.json()
            if resp_dict.get("idx"):
                booking.payment_status = True
                booking.paid_date = timezone.localtime(timezone.now())
                booking.save()
                del request.session["booking_id"]
                messages.success(
                    request, "Booking success. Thanks for booking our room.")
                return JsonResponse({"status": "success", "return_url": booking.get_absolute_url + "?b=s"})
            else:
                return JsonResponse({"status": "error", "return_url": payment_method.khalti_verify})

        except Exception as e:
            messages.error(request, "Invalid Reqeust...")
            print(e)
            return redirect("hbsapp:clienthome")


class CustomerProfileView(CustomerRequiredMixin, ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        customer = request.user.customer
        context["customer"] = customer
        context["allbookings"] = RoomBooking.objects.filter(
            customer=customer).order_by("-id")
        return render(request, "clienttemplates/customerprofile.html", context)


class CustomerPasswordChangeView(CustomerRequiredMixin, ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["password_change_form"] = PasswordChangeForm
        return render(request, "clienttemplates/customerpasswordchange.html", context)

    def post(self, request, *args, **kwargs):
        pcf = PasswordChangeForm(request.POST)
        if pcf.is_valid():
            password = pcf.cleaned_data.get("password")
            confirm_password = pcf.cleaned_data.get("confirm_password")
            if password == confirm_password:
                user = request.user
               # user.set_password(password)
                #user.save()
                #messages.success(request, "Password changed successfully. Please login again.")
            else:
                messages.error(request, "Your passwords did not match.")
        else:
            messages.error(request, "Something went wrong..")
        return redirect("hbsapp:customerprofile")

class CustomerProfileUpdateView(CustomerRequiredMixin, ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        customer = request.user.customer
        context["customer"] = customer
        initial = {
            "first_name": customer.user.first_name,
            "last_name": customer.user.last_name,
        }
        context["customer_form"] = CustomerProfileForm(
            instance=customer, initial=initial)
        return render(request, "clienttemplates/customerprofileupdate.html", context)

    def post(self, request, *args, **kwargs):
        customer = request.user.customer
        customer_form = CustomerProfileForm(
            request.POST, request.FILES, instance=customer)
        if customer_form.is_valid():
            customer = customer_form.save()
            user = request.user
            user.first_name = customer_form.cleaned_data.get("first_name")
            user.last_name = customer_form.cleaned_data.get("last_name")
            user.last_name = customer_form.cleaned_data.get("last_name")
            user.save()
            messages.success(request, "Customer profile updated successfully.")
        else:
            messages.errors(request, "Something went wrong.")
        return redirect("hbsapp:customerprofile")




class CustomerBookingDetailView(CustomerRequiredMixin, ClientMixin, View):

    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            room_booking = RoomBooking.objects.get(
                id=self.kwargs.get("pk"), customer=request.user.customer)
            context["booking"] = room_booking
            context["ratings"] = RATING
            context["all_ratings"] = RoomBooking.objects.filter(hotel_room=room_booking.hotel_room, rating__isnull=False)
            return render(request, "clienttemplates/customerbookingdetail.html", context)
        except Exception as e:
            print(e)
            messages.error(request, "You are not allowed to view this page.")
            return redirect("hbsapp:clienthome")

    def post(self, request, *args, **kwargs):
        try:
            if request.POST.get("action") == "cancel":
                booking = RoomBooking.objects.get(
                    id=self.kwargs.get("pk"), customer=request.user.customer)
                booking.booking_status = "Rejected"
                booking.status_remarks = "Canceled by customer on " + \
                    timezone.localtime(timezone.now()).strftime(
                        "%m/%d/%Y, %H:%M:%S")
                booking.save()
                status = "success"
                messages.success(request, "Your booking was canceled...")
            else:
                status = "failure"
                messages.error(request, "Something went wrong...")
        except Exception as e:
            print(e)
            status = "failure"
            messages.error(request, "Something went wrong...")
        return JsonResponse({"status": status})



class CustomerRatingView(CustomerRequiredMixin, ClientMixin, View):
    def post(self, request, *args, **kwargs):
        booking = RoomBooking.objects.get(id=self.kwargs.get("pk"))
        rating = request.POST.get("c_rating")
        booking.rating = rating
        booking.save()
        messages.success(request, "Thanks for providing your reviews to our room.")
        return redirect("hbsapp:customerbookingdetail", booking.id)

# admin views


class AdminLoginView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "loginform": LoginForm
        }
        return render(request, "admintemplates/adminlogin.html", context)

    def post(self, request, *args, **kwargs):
        loginform = LoginForm(request.POST, None)
        if loginform.is_valid():

            email = loginform.cleaned_data.get("email")
            password = loginform.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            try:
                admin = user.admin
                login(request, user)
                return redirect(reverse("hbsapp:adminhome"))
            except Exception as e:
                print(e)
                context = {
                    "loginform": LoginForm,
                    "error": "Invalid username or password."
                }
                return render(request, "admintemplates/adminlogin.html", context)
        else:
            context = {
                "loginform": LoginForm,
                "error": "Invalid username or password."
            }
            return render(request, "admintemplates/adminlogin.html", context)


class AdminLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Successfully logged out")
        return redirect("hbsapp:adminlogin")


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.admin = request.user.admin
            self.context = {
                "admin": self.admin
            }
        except Exception as e:
            print(e)
            return redirect(reverse("hbsapp:adminlogin") + "?next=" + request.path)
        return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["hotels"] = Hotel.objects.all()
        context["rooms"] = HotelRoom.objects.all()
        all_bookings = RoomBooking.objects.all()

        context["all_bookings"] = all_bookings
        context["confirmed_bookings"] = all_bookings.filter(
            booking_status="Confirmed")
        context["booking_requests"] = all_bookings.filter(
            booking_status="Pending")
        context["served_peoples"] = all_bookings.aggregate(
            total=Sum("total_persons")).get("total") or 0
        context["registered_customers"] = Customer.objects.all().count()

        context["rejected_amount"] = all_bookings.filter(
            booking_status="Rejected").aggregate(total=Sum("amount")).get("total") or 0
        context["confirmed_amount"] = all_bookings.filter(
            booking_status="Confirmed").aggregate(total=Sum("amount")).get("total") or 0
        context["collected_amount"] = all_bookings.filter(
            booking_status="Confirmed", payment_status=True).aggregate(total=Sum("amount")).get("total") or 0
        context["pending_amount"] = all_bookings.filter(booking_status__in=[
                                                        "Confirmed", "Pending"], payment_status=False).aggregate(total=Sum("amount")).get("total") or 0
        context["epayment"] = all_bookings.exclude(payment_method__name="Pay at Hotel").filter(booking_status__in=[
            "Confirmed", "Pending"], payment_status=True).aggregate(total=Sum("amount")).get("total") or 0
        return render(request, "admintemplates/adminhome.html", context)


class AdminHotelListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["hotellist"] = Hotel.objects.all()
        return render(request, "admintemplates/adminhotellist.html", context)


class AdminHotelCreateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["hotelform"] = HotelForm
        return render(request, "admintemplates/adminhotelcreate.html", context)

    def post(self, request, *args, **kwargs):
        hotelform = HotelForm(request.POST, request.FILES)
        if hotelform.is_valid():
            hotelform.save()
            messages.success(request, "New hotel added successfully.")
        else:
            context = {}
            messages.error(request, "Error creating new hotel.")
            return render(request, "admintemplates/adminhotelcreate.html", context)
        return redirect("hbsapp:adminhotellist")


class AdminHotelUpdateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            hotel = Hotel.objects.get(id=self.kwargs.get("pk"))
            context["hotelform"] = HotelForm(instance=hotel)
            return render(request, "admintemplates/adminhotelcreate.html", context)
        except Exception as e:
            print(e)
            messages.error(request, "Hotel not found.")
            return redirect("hbsapp:adminhotellist")

    def post(self, request, *args, **kwargs):
        try:
            hotel = Hotel.objects.get(id=self.kwargs.get("pk"))
            hotel.name = request.POST.get("name")
            hotel.address = request.POST.get("address")
            hotel.image = request.FILES.get("image")
            hotel.email = request.POST.get("email")
            hotel.contact = request.POST.get("contact")
            hotel.save()
            messages.success(request, "Data updated successfully.")
        except Exception as e:
            print(e)
            messages.error(request, "Can not save the data.")
        return redirect("hbsapp:adminhotellist")


class AdminRoomListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["roomlist"] = HotelRoom.objects.order_by("-id")
        return render(request, "admintemplates/adminroomlist.html", context)


class AdminRoomCreateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["roomform"] = HotelRoomForm
        return render(request, "admintemplates/adminroomcreate.html", context)

    def post(self, request, *args, **kwargs):
        room_form = HotelRoomForm(request.POST, request.FILES)
        if room_form.is_valid():
            room = room_form.save()
            messages.success(request, "New hotel added successfully.")
        else:
            messages.error(request, "Something went wrong")
        return redirect("hbsapp:adminroomlist")


class AdminRoomUpdateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
        context["room"] = room
        context["roomform"] = HotelRoomUpdateForm(instance=room)
        return render(request, "admintemplates/adminroomupdate.html", context)

    def post(self, request, *args, **kwargs):
        hotel_room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
        room_form = HotelRoomUpdateForm(
            request.POST, request.FILES, instance=hotel_room)
        if room_form.is_valid():
            room_form.save()
            messages.success(request, "Data updated successfully.")
        else:
            print(room_form.errors)
            messages.error(request, "Something went wrong")
        return redirect("hbsapp:adminroomlist")


class AdminBookingListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        allbookings = RoomBooking.objects.all()
        context["pending_bookings"] = allbookings.filter(
            booking_status="Pending").count()
        context["allbookings"] = allbookings
        return render(request, "admintemplates/adminbookinglist.html", context)


class AdminBookingDetailView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["booking"] = RoomBooking.objects.get(id=self.kwargs.get("pk"))
        return render(request, "admintemplates/adminbookingdetail.html", context)

    def post(self, request, *args, **kwargs):
        rb = RoomBooking.objects.get(id=self.kwargs.get("pk"))
        action = request.POST.get("action")
        if action == "bc":
            rb.booking_status = "Confirmed"
            rb.save()
            status = "success"
        elif action == "br":
            rb.booking_status = "Rejected"
            rb.status_remarks = request.POST.get("remarks")
            rb.save()
            status = "success"
        elif action == "ci":
            rb.customer_checked_in = True
            rb.checkin_time = timezone.localtime(timezone.now())
            rb.save()
            status = "success"
        elif action == "co":
            rb.customer_checked_out = True
            rb.checkout_time = timezone.localtime(timezone.now())
            rb.save()
            status = "success"
        elif action == "mp":
            rb.payment_status = True
            rb.paid_date = timezone.localtime(timezone.now())
            rb.save()
            status = "success"
        else:
            status = "error"
        resp = {
            "action": request.POST.get("action"),#new dictionery name action and status created
            "status": status
        }
        if status == "error":
            messages.error(request, "Something went wrong..")
        else:
            messages.success(
                request, "Booking Information updated successfully...")
        return JsonResponse(resp)# return json response status and action sucess


class AdminMessageListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["all_messages"] = Message.objects.order_by("-id")
        return render(request, "admintemplates/adminmessagelist.html", context)


class AdminCustomerListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["all_customers"] = Customer.objects.order_by("-id")
        return render(request, "admintemplates/admincustomerlist.html", context)


class AdminCustomerDetailView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            customer = Customer.objects.get(id=self.kwargs.get("pk"))
            context["customer"] = customer
            context["allbookings"] = RoomBooking.objects.filter(
                customer=customer)
        except Exception as e:
            print(e)
            messages.error(request, "Customer not found...")
            return redirect("hbsapp:adminhome")
        return render(request, "admintemplates/admincustomerdetail.html", context)
