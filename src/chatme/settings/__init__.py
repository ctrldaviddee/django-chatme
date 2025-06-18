import os

_env = os.getenv("DJANGO_ENV", "local")
if _env == "production":
    from .prod import *  # noqa: F403 F401
else:
    from .local import *  # noqa: F403 F401
