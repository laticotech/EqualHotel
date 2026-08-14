from django import forms
from .models import TeamMember, Event, EventRegistration


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            'name', 'position', 'bio', 'photo', 'email',
            'phone', 'display_order', 'is_active'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'max_attendees', 'price', 'image', 'status', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date")

        return cleaned_data


class EventRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)  # Get event from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = EventRegistration
        fields = ['full_name', 'email', 'phone', 'company', 'special_requirements', 'number_of_guests']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'company': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter your company name (optional)'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                          'placeholder': 'Any special requirements or dietary restrictions?'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
        labels = {
            'number_of_guests': 'Number of attendees (including yourself)',
        }

    def clean_number_of_guests(self):
        number_of_guests = self.cleaned_data['number_of_guests']

        if self.event and self.event.max_attendees > 0:
            available_spots = self.event.available_spots
            if number_of_guests > available_spots:
                raise forms.ValidationError(
                    f"Only {available_spots} spots available. Please reduce the number of guests."
                )
        return number_of_guests

    def clean_email(self):
        email = self.cleaned_data['email']

        if self.event and EventRegistration.objects.filter(event=self.event, email=email).exists():
            raise forms.ValidationError("This email is already registered for this event.")

        return email