from fastapi.encoders import jsonable_encoder


def parse_sql_detection(sql_response):

    data_parsed = {}
    for row in sql_response:
        aux_dict ={}
        for model in row:
            model_parsed = jsonable_encoder(model, sqlalchemy_safe=True)
            aux_dict.update(model_parsed)
        
        data_parsed.update(aux_dict)

    
    return data_parsed


def parse_sql_non_detecions_to_multistream(sql_response):
    data_parsed = []
    for row in sql_response:
        aux_dict = {}
        for model in row:
            model_parsed = jsonable_encoder(model, sqlalchemy_safe=True)
            aux_dict.update(model_parsed)
        data_parsed.append(aux_dict)

    return data_parsed


