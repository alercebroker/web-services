def mag_parser(mag_list):
    key_mapping = {
        "band": "fid",
        "stellar": "stellar",
        "corrected": "corrected", 
        "ndubious": "ndubious",
        "magmean": "magmean",
        "magmedian": "magmedian", 
        "magmax": "magmax",
        "magmin": "magmin",
        "magsigma": "magsigma",
        "maglast": "maglast",
        "magfirst": "magfirst",
        "step_id_corr": "step_id_corr"
    }
    
    result = []
    for d in mag_list:
        new_mag_dict = {}
        
        for o_mag, n_mag in key_mapping.items():
            if o_mag in d.__dict__.keys():
                new_mag_dict[n_mag] = d.__dict__[o_mag]
            else:
                new_mag_dict[n_mag] = None
        
        new_mag_only_keys = ["ndet", "firstmjd", "lastmjd"]
        for key in new_mag_only_keys:
            new_mag_dict[key] = None
            
        result.append(new_mag_dict)
    return result