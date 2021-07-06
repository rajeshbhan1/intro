from django import forms
from .models import *


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["full_name", "mobile", "email", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "mobile": forms.NumberInput(attrs={
                "class": "form-control",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "pattern": '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            })
        }

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "Enter your email...",
        "class": "form-control",
        "pattern": '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter your password...",
        "class": "form-control"
    }))

# customer forms
class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your first name..."
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your last name..."
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your address..."
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "Enter your email...",
        "class": "form-control",
        "pattern": '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter your password...",
        "class": "form-control"
    }))
    mobile = forms.CharField(widget=forms.NumberInput(attrs={
        "placeholder": "Enter your phone number...",
        "class": "form-control",
    }))


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Your first name..."
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Your last name..."
    }))
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "mobile", "address", "profile_image"]
        widgets = {
            "mobile": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Your Mobile number..."
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "your address..."
            }),
            "profile_image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            })
        }


class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
  #      "class": "form-control",
   #     "placeholder": "Enter new passowrd...",
    #    "onkeyup": "checkPasswords()"
    }))
    #confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
     #   "class": "form-control",
      #  "placeholder": "Confirm new passowrd...",
       # "onkeyup": "checkPasswords()"
    #}))


class RoomBookingForm(forms.ModelForm):

    class Meta:
        model = RoomBooking
        fields = ["total_persons", "booking_starts", "booking_ends", "message", "payment_method"]
        widgets = {
            "total_persons": forms.Select(attrs={
                "class": "form-control"
            }),
            "booking_starts": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "date",
                "onchange": "compareDates()"
            }),
            "booking_ends": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "date",
                "onchange": "compareDates()"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "payment_method": forms.Select(attrs={
                "class": "form-control",
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].empty_label = "Select payment method"
    


# admin forms

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ["name", "image", "address", "contact", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
    



class HotelRoomForm(forms.ModelForm):
    class Meta:
        model = HotelRoom
        fields = ["hotel", "room_type", "room_code", "image", "description", "marked_price", "price", "maximum_capacity"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class HotelRoomUpdateForm(forms.ModelForm):
    class Meta:
        model = HotelRoom
        fields = ["hotel", "room_type", "room_code", "image", "description", "marked_price", "price", "maximum_capacity"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"