from .base import *

# Import environment-specific settings
try:
    from .local import *
except ImportError:
    try:
        from .production import *
    except ImportError:
        pass 