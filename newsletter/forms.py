from django.forms import ModelForm
from .models import Emails

class NewsletterSignupForm(ModelForm):

    def __init__(self, *args, **kwargs):
            super(NewsletterSignupForm, self).__init__(*args, **kwargs)
            
            for fieldname in ['user_email']:
                self.fields[fieldname].help_text = None
                self.fields[fieldname].widget.attrs.update({'class':'block appearance-none w-full bg-white border border-grey-light hover:border-grey px-2 py-2 rounded shadow'})

    class Meta:
        model = Emails
        fields = '__all__'