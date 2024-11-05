from sqlalchemy import select
from sqlalchemy.orm import Session

from anomaly_api.database.models import AnomalyScoreTop, AnomalyDistributions
from anomaly_api.database.result_models import AnomalyScore as AnomalyScoreModel, AnomalyDistributions as AnomalyDistributionModel
from anomaly_api.database.db import connect_scores


def get_scores_list(oids: list[str] = None, filters: list[dict] = None):
    """
    The filters are a list of dict with the following schema
        {
            category: a_category
            min_score: 0.1 a float
            max_score: 0.2 a float
        }
    """

    def get_model_category(category_name):
        if category_name == "Transient":
            return AnomalyScoreTop.Transient
        if category_name == "Stochastic":
            return AnomalyScoreTop.Stochastic
        if category_name == "Periodic":
            return AnomalyScoreTop.Periodic
        else:
            raise Exception(f"Categoy Error {category_name}")
        

    engine = connect_scores()
    with Session(engine) as  session:

        stmt = select(AnomalyScoreTop)

        if oids:
            stmt = stmt.where(AnomalyScoreTop.oid.in_(oids))

        if filters:
            for f in filters:
                s_attr = get_model_category(f.get("category"))
                min_s = f.get("min_score", None)
                max_s = f.get("max_score", None)

                if min_s:
                    stmt = stmt.where(s_attr >= min_s)
                if max_s:
                    stmt = stmt.where(s_attr <= max_s)

        print(f"------\nDEBUG: query = \n {stmt}")

        result = session.execute(stmt)
        results_all = result.all()
        scores_top = [row[0] for row in results_all]

        if len(scores_top) == 0:
            raise Exception(f"No score was found for objects {oids} and filters {filters}")
        result_dict = [AnomalyScoreModel(**score.__dict__) for score in scores_top]

        return result_dict
    

def get_scores_by_oid(oids: list[str]):
    engine = connect_scores()
    with Session(engine) as  session:

        stmt = select(AnomalyScoreTop).where(AnomalyScoreTop.oid.in_(oids))
        result = session.execute(stmt)
        results_all = result.all()
        scores_top = [row[0] for row in results_all]

        if len(scores_top) == 0:
            raise Exception(f"No score was found for objects {oids}")
        result_dict = [AnomalyScoreModel(**score.__dict__) for score in scores_top]

        return result_dict

def get_objects_by_score(filters: list[dict]):
    """
    The filters are a list of dict with the following schema
        {
            category: a_category
            min_score: 0.1 a float
            max_score: 0.2 a float
        }
    """

    def get_model_category(category_name):
        if category_name == "Transient":
            return AnomalyScoreTop.Transient
        if category_name == "Stochastic":
            return AnomalyScoreTop.Stochastic
        if category_name == "Periodic":
            return AnomalyScoreTop.Periodic
        else:
            raise Exception(f"Categoy Error {category_name}")

    engine = connect_scores()
    with Session(engine) as  session:

        stmt = select(AnomalyScoreTop)

        for f in filters:
            attribute = get_model_category(f.get("category"))
            min_s = f.get("min_score", None)
            max_s = f.get("max_score", None)

            if min_s:
                stmt = stmt.where(attribute >= min_s)
            if max_s:
                stmt = stmt.where(attribute <= max_s)

        result = session.execute(stmt)
        results_all = result.all()
        scores_top = [row[0] for row in results_all]

        if len(scores_top) == 0:
            raise Exception(f"No score was found with filters {filters}")
        
        result_dict = [AnomalyScoreModel(**score.__dict__)  for score in scores_top]

        return result_dict

def get_scores_distributions(categories: list[str]):

    engine = connect_scores()
    with Session(engine) as  session:

        stmt = select(AnomalyDistributions).where(AnomalyDistributions.category.in_(categories))
        result = session.execute(stmt)
        results_all = result.all()
        distributions = [row[0] for row in results_all]

        if len(distributions) == 0:
            raise Exception(f"No distribution was found for categories {categories}")
        result_dict = [AnomalyDistributionModel(**dist.__dict__)   for dist in distributions]

        return result_dict
