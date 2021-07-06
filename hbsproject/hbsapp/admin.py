from django.contrib import admin

from .models import *

admin.site.register([Admin, Hotel, HotelRoom, Customer, PaymentMethod, RoomBooking, Message])