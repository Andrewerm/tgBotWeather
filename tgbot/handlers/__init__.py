"""Import all routers and add them to routers_list."""
from .admin import admin_router  # type: ignore
from .ai import ai_router  # type: ignore
from .echo import echo_router  # type: ignore
from .profile import profile_router  # type: ignore
from .simple_menu import menu_router  # type: ignore
from .user import user_router  # type: ignore
from .weather import weather_router  # type: ignore

routers_list = [
    profile_router,
    weather_router,
    ai_router,
    # admin_router,
    # menu_router,
    # user_router,
    # echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]
