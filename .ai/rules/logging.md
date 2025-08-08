# Logging Guidelines for Built with Django

## Import Pattern
```python
from builtwithdjango.utils import get_builtwithdjango_logger

logger = get_builtwithdjango_logger(__name__)
```

## General
- Don't add logs unless specifically asked to.

## Message Formatting
- Message should be simple and to the point and describe an action: `logger.info("Project Added")`
- Include any context as kwargs: `logger.info("{message}", project_id = 1)`
- Prefix should be added to suggest where the opration is happening: `logger.info("[Task - Add new project] Project Added")`


## Contextual Information
- Try to inlude all data that is available
- Must include: project_id, user_email, to help with debugging
