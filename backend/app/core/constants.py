"""
Centralized constants for the HERCU backend.

Only includes values that are duplicated across multiple files.
Context-specific values (max_tokens, temperature per LLM call) stay local.
"""

# ============ Quality Thresholds ============
# Used by quality scorers, template services, and generation pipelines

# Minimum quality to pass (baseline)
QUALITY_BASELINE = 75.0

# Minimum quality to save as reusable template
QUALITY_TEMPLATE_SAVE = 85.0

# High quality threshold (premium templates)
QUALITY_HIGH = 90.0

# Supervisor pass threshold (chapter review)
QUALITY_SUPERVISOR_PASS = 80

# JPEG image compression quality
IMAGE_QUALITY_DEFAULT = 85
IMAGE_QUALITY_HIGH = 90

# ============ Timeouts (seconds) ============
# HTTP client timeouts for different operation types

TIMEOUT_HEALTH_CHECK = 5.0       # Quick health/ping checks
TIMEOUT_SHORT = 30.0             # Short operations (search, classify)
TIMEOUT_MEDIUM = 120.0           # Standard LLM calls
TIMEOUT_LONG = 300.0             # Complex generation (multi-step)
TIMEOUT_EXTRA_LONG = 600.0       # Agent simulator generation

# ============ Retry & Batch ============

MAX_RETRIES = 3                  # Default retry count for LLM calls
QUIZ_BATCH_SIZE = 5              # Questions per batch in quiz generation

# ============ Message Limits ============
# Different limits for different contexts (intentional)

MAX_MESSAGE_LENGTH_USER = 2000       # User-facing input (AI tutor)
MAX_MESSAGE_LENGTH_INTERNAL = 50000  # Internal/proxy calls (grinder SVG)

# ============ Template Retrieval ============

TEMPLATE_RETRIEVE_LIMIT_SMALL = 2    # For chapter generation
TEMPLATE_RETRIEVE_LIMIT_DEFAULT = 3  # For quiz/dialogue
TEMPLATE_RETRIEVE_LIMIT_LARGE = 10   # For browsing/listing
