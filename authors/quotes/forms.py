from datetime import datetime
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, TextInput
from .models import Author, Quote, Tag

def validate_date_field(value):
    try:
        date_value = datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        raise ValidationError("Please enter a date in correct format: dd.mm.YYYY")
    
    if date_value > datetime.today().date():
        raise ValidationError("Born date can not to be in future")
    
    return date_value

class AuthorForm(ModelForm):
    fullname = CharField(min_length=3, max_length=25, required=True, widget=TextInput())
    born_date = CharField(min_length=3, max_length=25, required=True, widget=TextInput(), validators=[validate_date_field])
    born_location = CharField(min_length=3, max_length=25, required=True, widget=TextInput())
    description = CharField(min_length=3, max_length=25, required=True, widget=TextInput())

    class Meta:
        model = Author
        fields = ['born_date', 'born_location', 'description', 'fullname']

class QuoteForm(ModelForm):

    quote = TextInput()

    class Meta:
        model = Quote
        fields = ['quote']
        exclude = ['tags']

class TagForm(ModelForm):

    name = CharField(min_length=3, max_length=25, required=True, widget=TextInput())
    
    class Meta:
        model = Tag
        fields = ['name']
