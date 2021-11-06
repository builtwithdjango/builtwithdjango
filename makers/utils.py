from django.utils.text import slugify

from makers.models import Maker


def retroactively_assign_slug():
    makers = Maker.objects.all()

    for maker in makers:
        if maker.slug is None:
            print(f"Updating slug for {maker.first_name} {maker.last_name}")
            maker.slug = slugify(f"{maker.first_name} {maker.last_name}")
            maker.save()
            print(f"New slug {maker.slug} is saved.")
        continue


retroactively_assign_slug()

# run with `poetry run python manage.py shell < makers/utils.py`
