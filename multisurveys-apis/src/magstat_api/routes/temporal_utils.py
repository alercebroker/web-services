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
                if isinstance(d.__dict__[o_mag], float):
                    new_mag_dict[n_mag] = round(d.__dict__[o_mag], 3)
                else:
                    new_mag_dict[n_mag] = d.__dict__[o_mag]
            else:
                new_mag_dict[n_mag] = '-'
        
        new_mag_only_keys = ["ndet", "firstmjd", "lastmjd"]
        for key in new_mag_only_keys:
            new_mag_dict[key] = '-'
            
        result.append(new_mag_dict)
    return result

def parse_lsst_dia_objects_to_dict(lsst_list):
    result = []
    
    for obj in lsst_list:
        obj_dict = obj.model_dump(mode='json')
        
        for key, value in obj_dict.items():
            if isinstance(value, float):
                obj_dict[key] = round(value, 3)
        
        result.append(obj_dict)
    
    return result