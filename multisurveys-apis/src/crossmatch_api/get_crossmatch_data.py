import logging

import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# 3 s to connect, 10 s to wait for data. catsHTM answers in about 2 s (measured from a crossmatch pod, 01/10/2026).
CATSHTM_TIMEOUT = (3, 10)


def get_alerce_data(ra: float, dec: float, radius: int) -> list[dict]:
    """
    Query the ALeRCE catsHTM crossmatch API for catalog matches near a sky position.

    Performs a cone search against multiple astronomical surveys via the
    catsHTM crossmatch service and returns all matches found within the
    given search radius.

    Args:
        ra: Right ascension of the query position, in degrees.
        dec: Declination of the query position, in degrees.
        radius: Search radius in arcseconds (typically 20).

    Returns:
        A list of per-survey match dictionaries.

    Raises:
        HTTPException: 504 if catsHTM doesn't answer in time, 502 for any other upstream failure (connection
            error, an error status, or a body that isn't JSON).
    """

    base_url = "https://catshtm.alerce.online/crossmatch_all"
    params = {"ra": ra, "dec": dec, "radius": radius}

    try:
        response = requests.get(base_url, params=params, timeout=CATSHTM_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.Timeout as e:
        logger.warning("catsHTM timed out: %s", e)
        raise HTTPException(status_code=504, detail="The catsHTM crossmatch service did not answer in time")
    except requests.RequestException as e:
        logger.warning("catsHTM request failed: %s", e)
        raise HTTPException(status_code=502, detail="The catsHTM crossmatch service failed")
