from django.urls import path
from .views import *

app_name = "hbsapp"
urlpatterns = [
    # client urls
    path("", ClientHomeView.as_view(), name="clienthome"),
    path("contact/", ClientContactView.as_view(), name="clientcontact"),
    path("search/", ClientSearchView.as_view(), name="clientsearch"),
    path("hotel-<int:pk>-rooms/",
         ClientHotelDetailView.as_view(), name="clienthoteldetail"),
    path("room-<room_code>-<int:pk>/",
         ClientRoomDetailView.as_view(), name="clientroomdetail"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgotpassword"),
    path("reset-password/<email>/<token>/",
         ResetPasswordView.as_view(), name="resetpassword"),
    # customer urls
    path("register/", CustomerRegisterView.as_view(), name="customerregister"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),

    path("room-<int:pk>-check/",
         CustomerRoomCheckView.as_view(), name="customerroomcheck"),
    path("room-<int:pk>-book/",
         CustomerRoomBookingView.as_view(), name="customerroombooking"),

    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),

    path("customer-profile/",
         CustomerProfileView.as_view(), name="customerprofile"),
    path("customer-profile/password-change/",
         CustomerPasswordChangeView.as_view(), name="customerpasswordchange"),
    path("customer-profile-update/",
         CustomerProfileUpdateView.as_view(), name="customerprofileupdate"),
    path("customer-profile/booking-<int:pk>/",
         CustomerBookingDetailView.as_view(), name="customerbookingdetail"),
    path("customer-profile/booking-<int:pk>-rate/",
         CustomerRatingView.as_view(), name="customerrating"),

    # admin urls
    path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),
    path("admin-logout/", AdminLogoutView.as_view(), name="adminlogout"),

    path("system-admin/", AdminHomeView.as_view(), name="adminhome"),
    path("system-admin/hotel-list/",
         AdminHotelListView.as_view(), name="adminhotellist"),
    path("system-admin/hotel-create/",
         AdminHotelCreateView.as_view(), name="adminhotelcreate"),
    path("system-admin/hotel-<int:pk>-update/",
         AdminHotelUpdateView.as_view(), name="adminhotelupdate"),

    path("system-admin/room-list/",
         AdminRoomListView.as_view(), name="adminroomlist"),
    path("system-admin/room-create/",
         AdminRoomCreateView.as_view(), name="adminroomcreate"),
    path("system-admin/room-<int:pk>-update/",
         AdminRoomUpdateView.as_view(), name="adminroomupdate"),

    path("system-admin/room-booking/",
         AdminBookingListView.as_view(), name="adminbookinglist"),
    path("system-admin/room-booking-<int:pk>/",
         AdminBookingDetailView.as_view(), name="adminbookingdetail"),


    path("system-admin/received-messages/",
         AdminMessageListView.as_view(), name="adminmessagelist"),

    path("system-admin/customers-list/",
         AdminCustomerListView.as_view(), name="admincustomerlist"),
    path("system-admin/customers-<int:pk>-detail/",
         AdminCustomerDetailView.as_view(), name="admincustomerdetail"),
]
