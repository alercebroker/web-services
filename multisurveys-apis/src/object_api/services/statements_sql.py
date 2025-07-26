from db_plugins.db.sql.models import Object, Probability_ms
from sqlalchemy import text

def convert_conesearch_args(args):
    try:
        ra, dec, radius = args["ra"], args["dec"], args.get("radius")
        if radius is None:
            radius = 30.0
    except KeyError:
        ra, dec, radius = None, None, None

    if ra and dec and radius:
        radius /= 3600.0  # From arcsec to deg
    return {"ra": ra, "dec": dec, "radius": radius}


def create_conesearch_statement(args):
    try:
        ra, dec, radius = args["ra"], args["dec"], args["radius"]
    except KeyError:
        ra, dec, radius = None, None, None

    if ra and dec and radius:
        return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
    else:
        return True
    

def create_order_statement(query, order_args):
    statement = None
    cols = query.column_descriptions

    for col in cols:
        model = col["entity"]
        attr = getattr(model, order_args.order_by, None)
        if attr:
            statement = attr
            break
    
    if order_args.order_mode == "ASC":
        statement = attr.asc()
    elif order_args.order_mode == "DESC":
        statement = attr.desc()

    return statement


def convert_filters_to_sqlalchemy_statement(args):
    filters = {
        "probability": probability_filters(args),
        "objects": object_filters(args)
    }

    return filters


def object_filters(args):
    filters_dict = []

    if args["n_det"]:
        ndet = Object.n_det >= args["n_det"][0]
        if len(args["n_det"]) > 1:
            ndet = ndet & (Object.n_det <= args["n_det"][1])
        filters_dict.append(ndet)

    if args["firstmjd"]:
        firstmjd = Object.firstmjd >= args["firstmjd"][0]
        if len(args["firstmjd"]) > 1:
            firstmjd = firstmjd & (Object.firstmjd <= args["firstmjd"][1])
        filters_dict.append(firstmjd)

    if args["lastmjd"]:
        lastmjd = Object.lastmjd >= args["lastmjd"][0]
        if len(args["lastmjd"]) > 1:
            lastmjd = lastmjd & (Object.lastmjd <= args["lastmjd"][1])
        filters_dict.append(lastmjd)

    if args["oids"]:
        if len(args["oids"]) == 1:
            filtered_oid = args["oids"][0].replace("*", "%")
            oids = (Object.oid == filtered_oid)
        else:
            oids = Object.oid.in_(args["oids"])
        filters_dict.append(oids)

    return filters_dict


def probability_filters(args):
    filters_prob_dict = []

    if args["classifier"]:
        classifier = Probability_ms.classifier_id == args["classifier"]
        filters_prob_dict.append(classifier)
    if args["class_name"]:
        class_ = Probability_ms.class_id == args["class_name"]
        filters_prob_dict.append(class_)
    if args["probability"]:
        probability = Probability_ms.probability >= args["probability"]
        filters_prob_dict.append(probability)
    if args["ranking"]:
        ranking = Probability_ms.ranking == args["ranking"]
        filters_prob_dict.append(ranking)
    elif not args["ranking"] and (
        args["classifier"] or args["class"] or args["classifier_version"]
    ):
        # Default ranking 1
        ranking = Probability_ms.ranking == 1
        filters_prob_dict.append(ranking)

    return filters_prob_dict


def add_limits_statements(stmt, pagination_args):
    row_index = (pagination_args.page-1) * pagination_args.page_size
    print(row_index)
    stmt = stmt.limit(pagination_args.page_size + 1).offset(row_index)

    return stmt