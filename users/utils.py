from django.forms.utils import ErrorList
from django.utils.text import slugify

from users.models import CustomUser


def retroactively_assign_slug():
    users = CustomUser.objects.all()

    for user in users:
        if user.slug is None or 1:
            print(f"Updating slug for {user.username}")
            user.slug = slugify(user.username)
            user.save()
            print(f"New slug {user.slug} is saved.")
        continue


retroactively_assign_slug()

# run with `poetry run python manage.py shell < users/utils.py`


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ""
        return f"""
            <div class="p-4 my-4 border border-red-600 border-solid rounded-md bg-red-50">
              <div class="flex">
                <div class="flex-shrink-0">
                  <!-- Heroicon name: solid/x-circle -->
                  <svg class="w-5 h-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3 text-sm text-red-700">
                      {''.join(['<div>%s</div>' % e for e in self])}
                </div>
              </div>
            </div>
         """
