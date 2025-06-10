from db_plugins.db.sql.models import NonDetection, Object


def convert_filters_non_detections_sql_alchemy(oid, survey_id):

    filters = {}

    if survey_id == "ztf":
        filters['survey_id'] = (Object.tid == 1 )
    elif survey_id == "lsst":
        filters['survey_id'] = (Object.tid == 0)
    else:
        pass

    if len(oid) > 0:
        filters['oid'] = (Object.oid == oid) 

    return filters
