import asyncio
import logging
from services.session_manager import session_manager

logger = logging.getLogger(__name__)

async def periodic_session_cleanup(interval_seconds: int = 600):
    """Background task to clean up expired user sessions and avoid memory leaks."""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            removed = await session_manager.cleanup_inactive()
            if removed > 0:
                logger.info(f"Cleaned up {removed} expired user session(s).")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during periodic session cleanup: {e}")
