import os
import logging

import valkey

logger = logging.getLogger(__name__)

class CacheManager:
    """Singleton wrapper for Valkey client"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            if os.getenv("USE_CACHE", "false").lower() != "true":
                logger.info("USE_CACHE is not set to true, using NoCacheClient")
                cls._instance = NoCacheClient()
            else:
                logger.info("creating cache client")
                cls._instance = valkey.Valkey(
                    host=os.getenv("VALKEY_HOST"),
                    port=int(os.getenv("VALKEY_PORT"))
                )
                response = cls._instance.ping()
                logger.info(f"Successfully connected to Valkety - Ping response: {response}")
        logger.debug("returning cache client instance")
        return cls._instance

class NoCacheClient():
    def get(self, key):
        logger.debug(f"Cache get called with key: {key} - NoCacheClient returning None")
        return None
    
    def set(self, key, value):
        logger.debug(f"Cache set called with key: {key} and value: {value} - NoCacheClient not caching")
        return None


def CacheEntity():
    return CacheManager()