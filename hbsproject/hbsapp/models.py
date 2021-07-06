from django.contrib.auth.models import User
from django.db.models import Avg
from django.urls import reverse
from django.db import models


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Admin(TimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.ImageField(upload_to="customers", null=True, blank=True)

    def __str__(self):
        return self.user.username


class Hotel(TimeStamp):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="hotels", null=True, blank=True)
    address = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name



ROOM_TYPE = (
    ("Single", "Single"),
    ("Double", "Double"),
    ("Triple", "Triple"),
    ("Quad", "Quad"),
    ("Queen", "Queen"),
    ("King", "King"),
)

CAPACITY = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)


class HotelRoom(TimeStamp):
    hotel = models.ForeignKey(Hotel, on_delete=models.RESTRICT)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE)
    room_code = models.CharField(max_length=50)
    image = models.ImageField(upload_to="rooms")
    description = models.TextField()
    marked_price = models.PositiveIntegerField(null=True, blank=True)
    price = models.PositiveIntegerField()
    view_count = models.BigIntegerField(default=0)
    maximum_capacity = models.PositiveIntegerField(default=2, choices=CAPACITY)

    def __str__(self):
        return self.room_code

    @property
    def get_absolute_url(self):
        return reverse("hbsapp:clientroomdetail",kwargs={"room_code": self.room_code, "pk": self.id})

    @property
    def get_rating(self):
        bookings = self.roombooking_set.filter(rating__isnull=False)
        if bookings.exists():
            rating = bookings.aggregate(avg=Avg("rating"))["avg"]
            return rating, bookings.count()
        else:
            return None


class Customer(TimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    address = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.ImageField(upload_to="customers", null=True, blank=True)

    def __str__(self):
        return self.user.username


class PaymentMethod(TimeStamp):
    name = models.CharField(max_length=200)
    #image = models.ImageField(upload_to="payment_methods")
    test_public_key = models.CharField(max_length=100, null=True, blank=True)
    live_public_key = models.CharField(max_length=100, null=True, blank=True)
    test_secret_key = models.CharField(max_length=100, null=True, blank=True)
    live_secret_key = models.CharField(max_length=100, null=True, blank=True)
    payment_url = models.CharField(max_length=50, null=True, blank=True)
    return_url = models.CharField(max_length=50, null=True, blank=True)
    payment_request_url = models.CharField(max_length=50, null=True, blank=True)
    payment_verify_url = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


BOOKING_STATUS = (
    ("Pending", "Pending"),
    ("Confirmed", "Confirmed"),
    ("Rejected", "Rejected"),
)

RATING = (
    (5, "One of the best room, I highly recommend to stay here"),
    (4, "Very Good Room, I recommend to stay here"),
    (3, "Good Room and nice service"),
    (2, "Its ok, no comment"),
    (1, "I do not recommend this room"),
)
class RoomBooking(TimeStamp):
    hotel_room = models.ForeignKey(HotelRoom, on_delete=models.RESTRICT)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)

    total_persons = models.PositiveIntegerField(default=1, choices=CAPACITY)
    booking_starts = models.DateField()
    booking_ends = models.DateField()
    message = models.TextField(null=True, blank=True)

    booking_status = models.CharField(max_length=50, choices=BOOKING_STATUS)
    status_remarks = models.CharField(max_length=500, null=True, blank=True)
    # after acceptance
    customer_checked_in = models.BooleanField(default=False)
    checkin_time = models.DateTimeField(null=True, blank=True)
    checkout_time = models.DateTimeField(null=True, blank=True)
    rating = models.PositiveIntegerField(choices=RATING, null=True, blank=True)
    # payment information
    amount = models.PositiveIntegerField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.RESTRICT)
    payment_status = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.hotel_room.room_code

    @property
    def get_review(self):
        if self.rating:
            return dict(RATING)[self.rating]
        else:
            return None

    @property
    def booking_duration(self):
        stay_days = self.booking_ends - self.booking_starts
        stay_days = 1 if stay_days.days == 0 else stay_days.days
        return stay_days

    @property
    def get_absolute_url(self):
        return reverse("hbsapp:customerbookingdetail",kwargs={"pk": self.id})



class Message(TimeStamp):
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField()

    def __str__(self):
        return self.full_name