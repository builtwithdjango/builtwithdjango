<!-- don't do this now, feels to complex -->

# Improve Active Site Check Specification

## Problem Statement

The current `check_project_is_active()` method in `projects/models.py` is producing **false negatives** - marking active websites as inactive. This causes legitimate projects to be filtered out of the main project listings, negatively impacting user experience and project visibility.

## Current Implementation Analysis

### Current Code Flow
1. `check_all_projects()` in `projects/tasks.py` iterates through all projects
2. For each project, `update_project_active_status(project_id)` is called asynchronously via Django-Q2
3. `update_project_active_status()` calls `project.check_project_is_active()`
4. `check_project_is_active()` makes a simple GET request with 7-second timeout
5. Only marks as inactive if response status is NOT 200, doesn't update to active if it IS 200

### Current Issues Identified

```python
def check_project_is_active(self):
    try:
        response = requests.get(self.url, timeout=7)
        self.active = response.status_code == 200
    except (requests.RequestException, ConnectionError, requests.exceptions.ConnectTimeout) as e:
        logger.error(f"check_project_is_active error: {e}")
        self.active = False

    return self.active
```

**Problems:**
1. **No User-Agent**: Many modern websites block requests without proper User-Agent headers
2. **No redirect handling**: Websites with HTTPS redirects (301/302) might fail
3. **Short timeout**: 7 seconds may be too short for some slower sites
4. **No retry logic**: Temporary network issues cause false negatives
5. **Limited status code acceptance**: Some sites return 201, 202, or other 2xx codes for valid responses
6. **No SSL certificate validation handling**: Sites with certificate issues might be valid but fail
7. **Missing headers**: Some sites require specific headers (Accept, etc.)
8. **CDN/Protection services**: Cloudflare and similar services might block basic requests
9. **Database update inconsistency**: The method sets `self.active` but doesn't save to database in the method itself
10. **No status persistence**: Only saves when inactive, not when active (causing potential data inconsistency)

## Proposed Solution

### Enhanced Site Checking Strategy

Implement a **multi-layered approach** with progressive fallbacks:

#### Layer 1: Standard HTTP Check (Most Sites)
- Proper User-Agent string
- Follow redirects automatically
- Accept all 2xx status codes
- Extended timeout (15-20 seconds)
- Standard headers (Accept, Accept-Language, etc.)

#### Layer 2: Browser-like Check (Protected Sites)
- More sophisticated User-Agent
- Additional browser headers
- Handle JavaScript redirects
- Support for sites with bot protection

#### Layer 3: Alternative Verification (Edge Cases)
- HEAD request instead of GET (lighter)
- Different endpoints (e.g., /robots.txt, /favicon.ico)
- SSL verification disabled for self-signed certificates

#### Layer 4: Manual Review Queue
- Sites that fail all automated checks
- Admin notification system
- Grace period before marking inactive

### Technical Implementation Plan

#### 1. Enhanced `check_project_is_active()` Method

```python
def check_project_is_active(self):
    """
    Multi-layered site availability check with fallbacks.
    Returns tuple: (is_active: bool, check_details: dict)
    """
    check_details = {
        'timestamp': timezone.now(),
        'checks_performed': [],
        'final_status': None,
        'error_details': None
    }

    # Layer 1: Standard check
    is_active = self._standard_http_check(check_details)
    if is_active:
        return True, check_details

    # Layer 2: Browser-like check
    is_active = self._browser_like_check(check_details)
    if is_active:
        return True, check_details

    # Layer 3: Alternative verification
    is_active = self._alternative_verification_check(check_details)
    if is_active:
        return True, check_details

    # All checks failed
    check_details['final_status'] = 'failed_all_checks'
    return False, check_details
```

#### 2. New Model Fields

Add fields to track checking history and reliability:

```python
class Project(models.Model):
    # ... existing fields ...

    # Enhanced active checking
    last_activity_check = models.DateTimeField(null=True, blank=True)
    activity_check_details = models.JSONField(default=dict, blank=True)
    consecutive_failures = models.PositiveIntegerField(default=0)
    check_retry_after = models.DateTimeField(null=True, blank=True)
    requires_manual_review = models.BooleanField(default=False)
    activity_check_method = models.CharField(max_length=50, blank=True)  # 'standard', 'browser_like', 'alternative'
```

#### 3. Improved Request Configuration

```python
class SiteChecker:
    STANDARD_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (compatible; BuiltWithDjango/1.0; +https://builtwithdjango.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
```

#### 4. Retry and Backoff Logic

```python
def should_retry_check(self):
    """Determine if this project should be rechecked based on failure history."""
    if not self.check_retry_after:
        return True

    if timezone.now() < self.check_retry_after:
        return False

    return True

def calculate_next_retry(self):
    """Calculate exponential backoff for failed checks."""
    if self.consecutive_failures == 0:
        return None

    # Exponential backoff: 1h, 4h, 12h, 24h, 48h, then weekly
    hours_delay = min(2 ** (self.consecutive_failures - 1), 168)  # Max 1 week
    return timezone.now() + timedelta(hours=hours_delay)
```

#### 5. Enhanced Task Functions

```python
def update_project_active_status(project_id):
    """Enhanced project status checking with detailed logging."""
    project = Project.objects.get(id=project_id)

    # Skip if in retry backoff period
    if not project.should_retry_check():
        logger.info(f"Skipping {project.title} - in retry backoff until {project.check_retry_after}")
        return f"Project {project.title} skipped - retry later"

    # Perform the check
    is_active, check_details = project.check_project_is_active()

    # Update project status
    previous_active = project.active
    project.active = is_active
    project.last_activity_check = timezone.now()
    project.activity_check_details = check_details

    if is_active:
        # Reset failure tracking on success
        project.consecutive_failures = 0
        project.check_retry_after = None
        project.requires_manual_review = False
        status_change = "reactivated" if not previous_active else "confirmed active"
    else:
        # Increment failure count and set retry backoff
        project.consecutive_failures += 1
        project.check_retry_after = project.calculate_next_retry()

        # Flag for manual review after multiple failures
        if project.consecutive_failures >= 3:
            project.requires_manual_review = True

        status_change = "deactivated" if previous_active else "confirmed inactive"

    project.save(update_fields=[
        'active', 'last_activity_check', 'activity_check_details',
        'consecutive_failures', 'check_retry_after', 'requires_manual_review'
    ])

    # Log significant status changes
    if previous_active != is_active:
        logger.warning(f"Project {project.title} status changed: {status_change}")

    return f"Project {project.title} is active: {is_active} ({status_change})"
```

#### 6. Monitoring and Admin Interface

**Admin Enhancements:**
- Filter projects by `requires_manual_review`
- Display `consecutive_failures` and `last_activity_check` in admin list
- Bulk action to force recheck projects
- Admin action to mark projects as "manually verified active"

**Management Commands:**
```bash
# Check projects that need retry
python manage.py check_projects --retry-only

# Force check specific projects
python manage.py check_projects --project-ids 1,2,3

# Check projects flagged for manual review
python manage.py check_projects --manual-review-only

# Reset failure counters
python manage.py reset_project_check_failures
```

#### 7. Notification System

**For Admin:**
- Daily email digest of projects requiring manual review
- Slack/Discord notifications for projects with status changes
- Weekly report of checking statistics

### Testing Strategy

#### Unit Tests
- Test each layer of checking logic
- Mock different HTTP response scenarios
- Test retry backoff calculations
- Test status change logging

#### Integration Tests
- Test against real websites with different characteristics:
  - Standard HTTP sites
  - HTTPS with redirects
  - Sites with bot protection (Cloudflare)
  - Sites with unusual status codes
  - Temporarily unavailable sites

#### Performance Tests
- Ensure checking doesn't overwhelm target sites
- Test timeout handling
- Test concurrent checking limits

### Deployment Strategy

#### Phase 1: Enhanced Checking Logic
- Deploy new checking methods
- Run in parallel with current system
- Log results for comparison

#### Phase 2: Database Schema Migration
- Add new tracking fields
- Migrate existing data
- Backfill check history

#### Phase 3: Full Activation
- Switch to new checking system
- Enable retry logic and manual review
- Set up monitoring and notifications

#### Phase 4: Optimization
- Analyze false positive/negative rates
- Fine-tune timeouts and retry logic
- Optimize checking frequency

### Configuration Options

Add to Django settings:
```python
# Site checking configuration
SITE_CHECKER = {
    'STANDARD_TIMEOUT': 20,  # seconds
    'BROWSER_TIMEOUT': 30,   # seconds
    'MAX_REDIRECTS': 10,
    'RETRY_DELAYS': [1, 4, 12, 24, 48, 168],  # hours
    'MANUAL_REVIEW_THRESHOLD': 3,  # consecutive failures
    'CHECK_CONCURRENCY': 5,  # max concurrent checks
    'RATE_LIMIT_DELAY': 1,   # seconds between requests to same domain
}
```

### Expected Outcomes

1. **Reduced False Negatives**: Multi-layered checking should catch sites that current method misses
2. **Better User Experience**: Fewer legitimate projects incorrectly marked as inactive
3. **Improved Reliability**: Retry logic handles temporary network issues
4. **Better Monitoring**: Detailed logging and admin tools for managing edge cases
5. **Scalability**: Backoff logic reduces unnecessary checking of problematic sites

### Success Metrics

- **False Negative Rate**: Reduce from current level to <5%
- **Manual Review Queue**: <10 projects requiring manual review per day
- **Check Success Rate**: >90% of active projects correctly identified
- **Performance**: Average check time <30 seconds per project
- **Admin Efficiency**: Reduce manual intervention by 80%

### Risk Mitigation

1. **Gradual Rollout**: Deploy in phases with monitoring
2. **Fallback Option**: Keep current method available as backup
3. **Rate Limiting**: Prevent overwhelming target websites
4. **Manual Override**: Admin can force active status regardless of checks
5. **Monitoring**: Alerts for unusual patterns or failures

This comprehensive approach should significantly reduce false negatives while providing better tools for managing edge cases and monitoring the health of the checking system.
