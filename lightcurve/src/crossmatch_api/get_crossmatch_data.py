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
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the JSON response
        else:
            return f"Error: Received status code {response.status_code}"
    
    except requests.RequestException as e:
        return f"Error: {str(e)}"
