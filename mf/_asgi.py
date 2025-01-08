from enum import Enum


class ASGIEventType(str, Enum):
    LIFESPAN = "lifespan"
    LIFESPAN_STARTUP = "lifespan.startup"
    LIFESPAN_STARTUP_FAILED = "lifespan.startup.failed"
    LIFESPAN_STARTUP_COMPLETE = "lifespan.startup.complete"
    LIFESPAN_SHUTDOWN = "lifespan.startup"
    LIFESPAN_SHUTDOWN_FAILED = "lifespan.startup.failed"
    LIFESPAN_SHUTDOWN_COMPLETE = "lifespan.startup.complete"
