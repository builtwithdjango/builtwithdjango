from django.forms import ModelForm
from .models import Project

class AddProject(ModelForm):

    def __init__(self, *args, **kwargs):
            super(AddProject, self).__init__(*args, **kwargs)
            
            for fieldname in ['website_title', 'user_email', 'website_short_description', 'website_url']:
                self.fields[fieldname].help_text = None
                self.fields[fieldname].widget.attrs.update({'class':'block appearance-none w-full bg-white border border-grey-light hover:border-grey px-2 py-2 rounded shadow'})

    class Meta:
        model = Project
        fields = '__all__'