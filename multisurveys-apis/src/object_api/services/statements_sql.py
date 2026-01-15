from db_plugins.db.sql.models import Object, Probability
from sqlalchemy import text


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
    statement = None
    cols = query.column_descriptions
    if order_args.order_by == 'lastmjd':
        model = cols[1]["entity"]
        attr = getattr(model, order_args.order_by, None)
        if attr is not None:
            statement = attr
    else:
        for col in cols:
            model = col["entity"]
            attr = getattr(model, order_args.order_by, None)
            if attr is not None:
                statement = attr
                break
    print('statement', statement, flush=True)
    if order_args.order_mode == "ASC":
        statement = attr.asc()
    elif order_args.order_mode == "DESC":
        statement = attr.desc()

    return statement


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
            # filtered_oid = args["oids"][0].replace("*", "%")
            oids = Object.oid == args["oids"][0]
        else:
            oids = Object.oid.in_(args["oids"])
        filters_dict.append(oids)

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

    return filters_prob_dict


def add_limits_statements(stmt, pagination_args):
    row_index = (pagination_args.page - 1) * pagination_args.page_size
    stmt = stmt.limit(pagination_args.page_size + 1).offset(row_index)

    return stmt
