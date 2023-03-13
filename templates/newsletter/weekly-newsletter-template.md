Read this issue [online]({% verbatim %}{{ WebVersionURL }}{% endverbatim %})

## News and Updates


## Projects
{% for project in projects %}
  - [{{ project.title }}](https://builtwithdjango.com{{ project.get_absolute_url }})
  by [{{ project.maker.first_name }} {{ project.maker.last_name }}](https://builtwithdjango.com{{ project.maker.get_absolute_url }}):
  {{ project.short_description }}
{% endfor %}

## Jobs
{% for job in jobs %}
  - {% if job.paid %}⭐⭐⭐{% endif %}
  [{{ job.title }} at {{ job.company_name }}](https://builtwithdjango.com{{ job.get_absolute_url }})
  {% if job.paid %}⭐⭐⭐{% endif %}
{% endfor %}

## Podcast Episodes
{% for episode in podcast_episodes %}
  - [{{ episode.title }}](https://builtwithdjango.com{{ episode.get_absolute_url }})

  {{ episode.details }}
{% endfor %}

## End Note
If you stumble upon any cool Django projects please let me know.
If you enjoy this newsletter, it would mean a lot if you could spread the word around. People can subscribe to our newsletter at
[https://builtwithdjango.com/newsletter/](https://builtwithdjango.com/newsletter/)
Thanks a ton in advance and have a wonderful weekend.
