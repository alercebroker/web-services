import requests

def get_alerce_data(ra, dec, radius):

    '''
        The catshtm api returns a list with every survey with information in a radius (we use 20 arcsec). Every element in this list is a dictionary with
        a survey and all his information. Every dictionary has a key that is the name of the survey and a value that is another dictionary with all the information.

        An example of the xmatch response of the object ZTF22aafsqud (not complete because of space):

        [{'2MASS': {'Dec': {'unit': 'deg', 'value': 12.072615}, 'Epoch': {'unit': 'JD', 'value': 2450935.7423}, 'ErrMaj': {'unit': 'arcsec', 'value': 0.22}, 'MagErr_H': {'unit': 'mag', 'value': None}, 'MagErr_J': {'unit': 'mag', 'value': 0.147}, 'MagErr_K': {'unit': 'mag', 'value': None}, 'Mag_H': {'unit': 'mag', 'value': 15.02}, 'Mag_J': {'unit': 'mag', 'value': 16.442}, 'Mag_K': {'unit': 'mag', 'value': 14.647}, 'RA': {'unit': 'deg', 'value': 207.026368}, 'distance': {'unit': 'arcsec', 'value': 8.548347834032453}}}, 
         {'2MASSxsc': {'Dec': {'unit': 'deg', 'value': 12.072708055555553}, 'H_K20e': {'unit': 'mag', 'value': 14.352999687194824}, 'Hb_a': {'unit': ' ', 'value': 0.4399999976158142}, 'Hpa': {'unit': 'deg', 'value': 30.0}, 'J_K20e': {'unit': 'mag', 'value': 14.852999687194824}, 'Jb_a': {'unit': ' ', 'value': 0.4000000059604645}, 'Jpa': {'unit': 'deg', 'value': 40.0}, 'K_K20e': {'unit': 'mag', 'value': 13.970999717712402}, 'Kb_a': {'unit': ' ', 'value': 0.4000000059604645}, 'Kpa': {'unit': 'deg', 'value': 40.0}, 'RA': {'unit': 'deg', 'value': 207.02645888888887}, 'distance': {'unit': 'arcsec', 'value': 8.286119001911564}, 'e_H_K20e': {'unit': 'mag', 'value': 0.13300000131130219}, 'e_J_K20e': {'unit': 'mag', 'value': 0.0820000022649765}, 'e_K_K20e': {'unit': 'mag', 'value': 0.1589999943971634}, 'r_K20e': {'unit': 'arcsec', 'value': 9.600000381469727}}},
         {'DECaLS': ...}, 
         ...]

        In this example we can see the name of the surveys (keys) and the values that has every survey in a dictionary (values)
    '''

    
    base_url = "https://catshtm.alerce.online/crossmatch_all"
    
    # Parameters for the API request
    params = {
        "ra": ra,
        "dec": dec,
        "radius": radius
    }
    
    # Make the GET request
    response = requests.get(base_url, params=params)
    return response.json()  # Return the JSON response
    