from sqlalchemy import text
from core.repository.models.object import Object


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

    print(ndet)

    # if args["firstmjd"]:
    #     firstmjd = DBPObject.firstmjd >= args["firstmjd"][0]
    #     if len(args["firstmjd"]) > 1:
    #         firstmjd = firstmjd & (
    #             DBPObject.firstmjd <= args["firstmjd"][1]
    #         )

    # if args["lastmjd"]:
    #     lastmjd = DBPObject.lastmjd >= args["lastmjd"][0]
    #     if len(args["lastmjd"]) > 1:
    #         lastmjd = lastmjd & (DBPObject.lastmjd <= args["lastmjd"][1])

    # if args["oid"]:
    #     if len(args["oid"]) == 1:
    #         filtered_oid = args["oid"][0].replace("*", "%")
    #         oids = DBPObject.oid.like(filtered_oid)
    #     else:
    #         oids = DBPObject.oid.in_(args["oid"])

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