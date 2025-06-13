from db_plugins.db.sql.models import NonDetection, Object, ZtfForcedPhotometry


def convert_filters_non_detections_sql_alchemy(oid, survey_id):

    filters = {}

    if len(oid) > 0:
        filters['oid'] = (NonDetection.oid == oid) 

    return filters

