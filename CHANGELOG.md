# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Types of changes

**Added** for new features.
**Changed** for changes in existing functionality.
**Deprecated** for soon-to-be removed features.
**Removed** for now removed features.
**Fixed** for any bug fixes.
**Security** in case of vulnerabilities.

## Unreleased
### Added
- Restored production PostHog activation from the Built with Django public project key and added explicit checkout return/cancel analytics events for job, sponsored job, and Django Developers checkout flows.
- Let signed-in project submitters update their linked listing metadata and screenshot.

### Changed
- Simplified the landing page by removing the hero showcase, proof strip, and quick-link card band.
- Expanded the home page project and guide sections to show six items and gave guides and jobs full-width sections.
- Stopped capturing noisy project-like API requests in PostHog request analytics and session recording network logs while keeping explicit like/unlike events.
- Rebuilt project likes to render counts from annotated project queries and use a single toggle request instead of per-card like API reads.

### Fixed
- Returned a signup form error instead of a server error when duplicate username submissions race validation.
- Made the bottom-right desktop ad use a solid surface instead of an opacity fade.
- Reduced noisy Sentry errors when direct project HTML fetches are blocked but the Jina Reader fallback succeeds.

## [0.4.6] - 2025-12-08
### Added
- API endpoint to publish posts.
- Page to show all articles
- Proper DRF Auth
- RSS


## [0.4.5] - 2025-02-13
### Changed
- better Logfire and Sentry support
- updated a bunch of libraries which cause a few failures. so fixed all of these.


## [0.4.5] - 2025-02-13
### Added
- Support for getting ip address of user and passing it to buttondown
- Support for logfire
- Version usage for buttondown
- Added admin command to unpublish projects

### Changed
- buttondown api version we are using

### Removed
- Usage of opentelemetry directly
- Kolo and Posthog Sentry middleware

## [0.4.5] - 2025-02-13
### Added
- Added Jina Reader API and Pydantic AI to programmatically analyze newly submitted project

## [0.4.4] - 2025-02-08
### Added
- Project search functionality with autocomplete
- Pagination for projects list page

### Fixed
- Visit Website button is correct vertically aligned.

## [0.4.3] - 2025-01-15
### Added
- Testimonials on Ad pagee

### Fixed
- Image width for Testimonial

## [0.4.2] - 2024-06-12
### Added
- Added a task to check if project is active.

## [0.4.1] - 2022-07-10
### Added
- Complete Redesign.

## [0.4.0] - 2022-07-10
### Added
- Ability to comment on guides.

## [0.3.0] - 2022-04-07
### Added
- Ability to sort projects based on # of likes and comments.

## [0.2.0] - 2022-02-11
### Changed
- Only registered users can now submit projects.
- We will now slowly move away from the "Maker" model towards users being the makers.

### Added
- Added a bunch of fields to users model.

### Fixed
- Fixed the email that gets sent to me when someone submits a project.
### Removed
- Removed Support Button for now.

## [0.1.4] - 2022-02-11
### Added
- Added support for Django_q
- As a consequence added a feature where screenshot is added automatically
- Moved email notifications to background tasks

## [0.1.3] - 2022-02-07
### Added
- Exit Intent Email Form

### Fixed
- Paid job posts show up first now
- Job posts more than 2 months old are now removed
## [0.1.2] - 2022-02-04
### Added
- Filter Field with "Is Open Search".
- Remote boolean and Timezone fields to Job Posts.
