from db_plugins.db.sql.models_pipeline import Object, Probability
from sqlalchemy import text

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: object lists filtered by these classifiers only return objects with n_det >= 2.
#
# These are the classifier_ids of lc_classifier_BHRF_forced_phot and its _top, _transient, _stochastic
# and _periodic parts in the production multisurvey database. The light-curve step only classifies objects
# with at least 2 detections, so the extra filter drops nothing today. It exists for speed: 80% of ZTF
# objects have 1 detection, and without it Postgres walks through them while sorting (lists over 55 s).
#
# If a new or retrained classifier with one of these ids classifies objects with 1 detection, or the ids
# are reassigned, those objects silently disappear from the lists. Whenever a classifier is added,
# replaced or renumbered, check this set (and multisurveys-apis/CLAUDE.md, "Light-curve classifier lists").
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
LC_CLASSIFIER_IDS = frozenset({5, 6, 7, 8, 9})
LC_CLASSIFIER_MIN_N_DET = 2


def convert_conesearch_args(args):
    try:
        ra, dec, radius = args["ra"], args["dec"], args.get("radius")
        if radius is None:
            radius = 30.0
    except KeyError:
        ra, dec, radius = None, None, None

    if ra is not None and dec is not None and radius is not None:
        radius /= 3600.0  # From arcsec to deg
    return {"ra": ra, "dec": dec, "radius": radius}


def create_conesearch_statement(args):
    try:
        ra, dec, radius = args["ra"], args["dec"], args["radius"]
    except KeyError:
        ra, dec, radius = None, None, None

    if ra is not None and dec is not None and radius is not None:
        return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
    else:
        return True


def create_order_statement(query, order_args):
    if order_args.order_by is None or order_args.order_by == "oid_list":
        return []

    cols = query.column_descriptions

    first_attr = get_model_attribute(cols, order_args.order_by)
    attributes = [first_attr]

    statement = add_order_mode(attributes, order_args.order_mode)

    return statement


def get_model_attribute(cols_meta_data, order_by):
    statement = None

    if order_by == "lastmjd":
        model = cols_meta_data[1]["entity"]
        attr = getattr(model, order_by, None)
        if attr is not None:
            statement = attr

        return statement

    for col in cols_meta_data:
        model = col["entity"]
        attr = getattr(model, order_by, None)
        if attr is not None:
            statement = attr
            break

    return statement


def add_order_mode(attributes, order_mode):
    attributes = [attr for attr in attributes if attr is not None]

    if not attributes:
        return []

    if order_mode == "ASC":
        return [attr.asc() for attr in attributes]

    return [attr.desc() for attr in attributes]


def convert_filters_to_sqlalchemy_statement(args):
    filters = {
        "probability": probability_filters(args),
        "objects": object_filters(args),
    }

    return filters


def object_filters(args):
    filters_dict = []

    if args["n_det"] is not None:
        ndet = Object.n_det >= args["n_det"][0]
        if len(args["n_det"]) > 1:
            ndet = ndet & (Object.n_det <= args["n_det"][1])
        filters_dict.append(ndet)

    # See the warning on LC_CLASSIFIER_IDS.
    if args["classifier"] in LC_CLASSIFIER_IDS:
        filters_dict.append(Object.n_det >= LC_CLASSIFIER_MIN_N_DET)

    if args["firstmjd"] is not None:
        firstmjd = Object.firstmjd >= args["firstmjd"][0]
        if len(args["firstmjd"]) > 1:
            firstmjd = firstmjd & (Object.firstmjd <= args["firstmjd"][1])
        filters_dict.append(firstmjd)

    if args["lastmjd"] is not None:
        lastmjd = Object.lastmjd >= args["lastmjd"][0]
        if len(args["lastmjd"]) > 1:
            lastmjd = lastmjd & (Object.lastmjd <= args["lastmjd"][1])
        filters_dict.append(lastmjd)

    if args["oids"] is not None:
        if len(args["oids"]) == 1:
            oids = Object.oid == args["oids"][0]
        else:
            oids = Object.oid.in_(args["oids"])
        filters_dict.append(oids)

    if args["survey"] is not None:
        if args["survey"] == "ztf":
            survey = Object.sid == 0
            filters_dict.append(survey)
        if args["survey"] == "lsst":
            survey = Object.sid == 1
            filters_dict.append(survey)

    return filters_dict


def probability_filters(args):
    filters_prob_dict = []
    if args["classifier"] is not None:
        classifier = Probability.classifier_id == args["classifier"]
        filters_prob_dict.append(classifier)
    if args["class_name"] is not None:
        class_ = Probability.class_id == args["class_name"]
        filters_prob_dict.append(class_)
    if args["probability"] is not None:
        probability = Probability.probability >= args["probability"]
        filters_prob_dict.append(probability)
    if args["ranking"] is not None:
        ranking = Probability.ranking == args["ranking"]
        filters_prob_dict.append(ranking)
    elif args["ranking"] is None and (
        args["classifier"] is None or args["class"] is None or args["classifier_version"] is None
    ):
        # Default ranking 1
        ranking = Probability.ranking == 1
        filters_prob_dict.append(ranking)

    if args["survey"] is not None:
        if args["survey"] == "ztf":
            survey = Probability.sid == 0
            filters_prob_dict.append(survey)
        if args["survey"] == "lsst":
            survey = Probability.sid == 1
            filters_prob_dict.append(survey)

    return filters_prob_dict


def add_limits_statements(stmt, pagination_args):
    row_index = (pagination_args.page - 1) * pagination_args.page_size
    stmt = stmt.limit(pagination_args.page_size + 1).offset(row_index)

    return stmt
