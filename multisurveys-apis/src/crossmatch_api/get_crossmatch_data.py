import requests


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
        A list of per-survey match dictionaries. Returns an error message string instead if the HTTP request fails.

    """

    base_url = "https://catshtm.alerce.online/crossmatch_all"
    params = {"ra": ra, "dec": dec, "radius": radius}

    try:
        response = requests.get(base_url, params=params)
        return response.json()

    except requests.RequestException as e:
        return f"Error: {str(e)}"
