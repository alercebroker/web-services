
from db_plugins.db.sql.models import Probability, Object as DBPObject


def _convert_filters_to_sqlalchemy_statement(args):
    (
        classifier,
        classifier_version,
        class_,
        ndet,
        firstmjd,
        lastmjd,
        probability,
        ranking,
        oids,
    ) = (True, True, True, True, True, True, True, True, True)
    if args["classifier"]:
        classifier = Probability.classifier_name == args["classifier"]
    if args["class_name"]:
        class_ = Probability.class_name == args["class_name"]
    if args["ndet"]:
        ndet = DBPObject.ndet >= args["ndet"][0]
        if len(args["ndet"]) > 1:
            ndet = ndet & (DBPObject.ndet <= args["ndet"][1])
    if args["firstmjd"]:
        firstmjd = DBPObject.firstmjd >= args["firstmjd"][0]
        if len(args["firstmjd"]) > 1:
            firstmjd = firstmjd & (
                DBPObject.firstmjd <= args["firstmjd"][1]
            )
    if args["lastmjd"]:
        lastmjd = DBPObject.lastmjd >= args["lastmjd"][0]
        if len(args["lastmjd"]) > 1:
            lastmjd = lastmjd & (DBPObject.lastmjd <= args["lastmjd"][1])
    if args["probability"]:
        probability = Probability.probability >= args["probability"]
    if args["ranking"]:
        ranking = Probability.ranking == args["ranking"]
    elif not args["ranking"] and (
        args["classifier"] or args["class"] or args["classifier_version"]
    ):
        # Default ranking 1
        ranking = Probability.ranking == 1

    if args["classifier_version"]:
        classifier_version = (
            Probability.classifier_version == args["classifier_version"]
        )

    if args["oid"]:
        if len(args["oid"]) == 1:
            filtered_oid = args["oid"][0].replace("*", "%")
            oids = DBPObject.oid.like(filtered_oid)
        else:
            oids = DBPObject.oid.in_(args["oid"])

    return (
        classifier,
        classifier_version,
        class_,
        ndet,
        firstmjd,
        lastmjd,
        probability,
        ranking,
        oids,
    )


def serialize_items(data):
    ret = []

    for obj, prob in data:
        obj = {**obj.__dict__}
        prob = {**prob.__dict__} if prob else {}
        ret.append({**obj, **prob})
    return ret