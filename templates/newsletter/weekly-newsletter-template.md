## News and Updates
-

---

## Projects

{% for project in projects %}
- [{{ project.title }}](https://builtwithdjango.com{{ project.get_absolute_url }}) - {% if project.maker %}by [{{ project.maker.first_name }} {{ project.maker.last_name }}](https://builtwithdjango.com{{ project.maker.get_absolute_url }}):{% endif %} {{ project.short_description }}
{% endfor %}

---

## Jobs
{% for job in jobs %}
- {% if job.paid %}⭐⭐⭐{% endif %} [{{ job.title }} at {{ job.company_name }}](https://builtwithdjango.com{{ job.get_absolute_url }}){% if job.paid %}⭐⭐⭐{% endif %}
{% endfor %}

---

## Podcast Episodes
{% for episode in podcast_episodes %}
  - [{{ episode.title }}](https://builtwithdjango.com{{ episode.get_absolute_url }})

  {{ episode.details }}
{% endfor %}

---
