import requests

def get_alerce_data(ra, dec, radius):
    base_url = "https://catshtm.alerce.online/crossmatch_all"
    
    # Parameters for the API request
    params = {
        "ra": ra,
        "dec": dec,
        "radius": radius
    }
    
    try:
        # Make the GET request
        response = requests.get(base_url, params=params)
        return response.json()  # Return the JSON response
    
    except requests.RequestException as e:
        return f"Error: {str(e)}"
