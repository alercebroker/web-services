from db_plugins.db.sql import models
from sqlalchemy.orm import aliased, Session

def query_get_objects(
        session_factory: Session, 
        search_params, 
        parsed_params
    ):

    classifer_name = search_params.filter_args.classifier
    classifier_version = search_params.filter_args.classifier_version
    ranking = search_params.filter_args.ranking

    consearch = parsed_params["consearch_statement"]
    consearch_args = parsed_params["consearch_args"]
    
    with session_factory() as session:
        join_table = (
            session.query(models.Probability)
            .filter(models.Probability.classifier_name == classifer_name)
            .filter(models.Probability.classifier_version == classifier_version)
            .filter(models.Probability.ranking == ranking)
            .subquery("probability")
        )

        join_table = aliased(models.Probability, join_table)

        # query = (
        #     session.query(models.Object, join_table)
        #     .outerjoin(join_table)
        #     .filter(consearch)
        #     .filter(*filters)
        #     .params(**consearch_args)
        # )

    pass