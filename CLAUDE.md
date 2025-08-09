# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python/Django Development
- **Install dependencies**: `poetry install`
- **Activate shell**: `poetry shell` or `poetry run python manage.py shell_plus --ipython`
- **Django shell**: `make shell` (uses shell_plus with IPython)
- **Run server**: `poetry run python manage.py runserver`
- **Database migrations**: `poetry run python manage.py makemigrations` then `poetry run python manage.py migrate`
- **Redis server**: `make redis` (runs on port 6390)
- **Production shell**: `make prod-shell`

### Frontend Development (Webpack/Node.js)
- **Install frontend dependencies**: `npm install` or `pnpm install`
- **Development build with hot reload**: `npm run start`
- **Production build**: `npm run build`
- **Watch mode**: `npm run watch`
- **Basic webpack**: `npm run webpack`

### Code Quality
- **Black formatting**: `poetry run black .` (line length: 120)
- **isort imports**: `poetry run isort .` (Django profile)
- **Template linting**: `poetry run djlint .` (Django profile)

## Architecture Overview

### Core Django Project Structure
Built with Django, this is a community showcase platform for Django projects. The main application is `builtwithdjango` with multiple Django apps:

**Main Apps:**
- `projects/` - Core functionality for showcasing Django projects
- `jobs/` - Job board for Django developers
- `makers/` - Developer profiles and community features
- `blog/` - Content management for articles
- `podcast/` - Podcast episode management
- `newsletter/` - Email newsletter functionality
- `developers/` - Developer account management
- `users/` - Custom user model and authentication
- `pages/` - Static pages and landing pages
- `tools/` - Utility tools (HTML formatter, Django secret generator)
- `api/` - REST API endpoints

### Key Technologies & Patterns
- **Django 5.0+** with Poetry for dependency management
- **Frontend**: Webpack + Stimulus (Hotwire) + Tailwind CSS
- **Database**: PostgreSQL (production), SQLite (development)
- **File Storage**: Cloudinary for media files
- **Background Tasks**: django-q2 with Redis
- **Monitoring**: Sentry, PostHog, OpenTelemetry integration
- **Authentication**: django-allauth with custom user model
- **Payments**: Stripe integration via dj-stripe

### Database Models
Key models include:
- `Project` - Main showcase projects with metadata, screenshots, tech stack
- `Job` - Job listings with company information
- `Maker` - Developer profiles linked to projects
- `Technology` - Tech stack tagging system
- `CustomUser` - Extended user model with profile features

### Logging
- @.ai/rules/logging.md for logging instructions

### Frontend Architecture
- **Webpack configuration** in `frontend/webpack/` with dev/prod/watch configs
- **Stimulus controllers** in `frontend/src/controllers/` for interactive components
- **Tailwind CSS** with custom styling in `frontend/src/styles/`
- **Static files** served from `static/` with manifest-based asset management

### Task Management Integration
This project uses Task Master for development workflow management:
- Configuration in `.taskmaster/config.json` and `.cursor/mcp.json`
- Follow the workflow patterns defined in `.cursor/rules/dev_workflow.mdc`
- Use MCP server integration for task management within development tools
- AI-powered task breakdown and complexity analysis available

### Environment Configuration
- Environment variables managed via django-environ
- Settings loaded from `.env` file (not committed)
- Separate configuration for development/production environments
- Makefile includes environment variable exports for consistency

### Background Jobs & Content Generation
- Uses Celery-style background tasks via django-q2
- Content generation features using AI tools (pydantic-ai, twikit for Twitter integration)
- Automated project metadata extraction and analysis

### Deployment
- Docker configuration in `deployment/` directory
- Separate Dockerfiles for server and worker processes
- Gunicorn configuration for production serving
- Environment-specific deployment scripts

## Common Workflows

### Adding New Projects
Projects are submitted via `/projects/new/` and processed through:
1. Form validation in `projects/forms.py`
2. Model creation with automated slug generation
3. Optional screenshot capture and metadata extraction
4. Technology tagging and categorization

### Content Management
- Blog posts support Markdown with syntax highlighting (Pygments)
- Template tags for Markdown rendering in `templatetags/markdown_extras.py`
- RSS feeds implemented for blog and podcast content

### User Management & Authentication
- Custom user model extends AbstractUser
- Profile images and social connections
- Subscription levels and payment processing
- Developer verification and profile management

This codebase emphasizes community-driven content, automated metadata extraction, and modern Django patterns with JavaScript enhancement rather than SPA architecture.
