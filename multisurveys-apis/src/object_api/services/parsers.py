from db_plugins.db.sql.models import Object
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


def convert_filters_to_sqlalchemy_statement(args):
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

    if args["ndet"]:
        ndet = Object.n_det >= args["ndet"][0]
        if len(args["ndet"]) > 1:
            ndet = ndet & (Object.n_det <= args["ndet"][1])

    if args["firstmjd"]:
        firstmjd = Object.firstmjd >= args["firstmjd"][0]
        if len(args["firstmjd"]) > 1:
            firstmjd = firstmjd & (Object.firstmjd <= args["firstmjd"][1])

    if args["lastmjd"]:
        lastmjd = Object.lastmjd >= args["lastmjd"][0]
        if len(args["lastmjd"]) > 1:
            lastmjd = lastmjd & (Object.lastmjd <= args["lastmjd"][1])

    if args["oids"]:
        if len(args["oids"]) == 1:
            filtered_oid = args["oids"][0].replace("*", "%")
            oids = Object.oid.like(filtered_oid)
        else:
            oids = Object.oid.in_(args["oids"])

    print(oids)

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
