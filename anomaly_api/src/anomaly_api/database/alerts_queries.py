from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from anomaly_api.database.db import connect_alerts
from anomaly_api.database.result_models import Object as ObjectModel, ObjectWithProbability
from db_plugins.db.sql.models import (
    Object,
    Probability
)


class ProbabilityFilter():
    def __init__(self, classifier_name: str, class_name: str, min_probability: float = None, max_probability: float = None) -> None:
        self.classifier_name = classifier_name
        self.class_name = class_name
        self.min_probability = min_probability
        self.max_probability = max_probability

    def have_min_filter(self) -> bool:
        return not self.min_probability == None
    
    def have_max_filter(self) -> bool:
        return not self.max_probability == None

    def __str__(self) -> str:
        return f"classifier: {self.classifier_name} - {self.class_name} : {self.min_probability} to {self.max_probability}"


def get_object_list(oids: list[str] = None, min_det:int = None, max_det: int = None, probability_filter: ProbabilityFilter = None):

    engine = connect_alerts()
    with Session(engine) as  session:
        
        if probability_filter:
            print(f"DEBUG---\n {probability_filter}")
            prob_stmt = select(Probability).where(
                Probability.classifier_name == probability_filter.classifier_name,
                Probability.class_name == probability_filter.class_name
            )
            if probability_filter.have_max_filter():
                prob_stmt = prob_stmt.where(Probability.probability <= probability_filter.max_probability)
            
            if probability_filter.have_min_filter():
                prob_stmt = prob_stmt.where(Probability.probability >= probability_filter.min_probability)
            
            prob_stmt = prob_stmt.subquery()
            prob_stmt = aliased(Probability, prob_stmt)
            stmt = select(Object, prob_stmt)
        else:
            stmt = select(Object)
        
        if oids:
            stmt = stmt.where(Object.oid.in_(oids))

        if min_det:
            stmt = stmt.where(Object.ndet >= min_det)
        if max_det:
            stmt = stmt.where(Object.ndet <= max_det)
        
        if probability_filter:
            stmt = stmt.join(prob_stmt, Object.oid == prob_stmt.oid)

        result = session.execute(stmt)
        results_all = result.all()

        if len(results_all) == 0:
            raise Exception(f"No Object was found for oids {oids} and\nwith ndet between {min_det} and {max_det}\nand probabilit filters {probability_filter}")
        
        if probability_filter:
            result_dict = [ObjectWithProbability(**(dict(score[0].__dict__, **score[1].__dict__))) for score in results_all]
        else:
            result_dict = [ObjectWithProbability(**score[0].__dict__) for score in results_all]

        return result_dict

def get_objects_by_oid(oids: list[str]):
    engine = connect_alerts()
    with Session(engine) as  session:

        stmt = select(Object).where(Object.oid.in_(oids))
        result = session.execute(stmt)
        results_all = result.all()
        scores_top = [row[0] for row in results_all]

        if len(scores_top) == 0:
            raise Exception(f"No Object was found for oids {oids}")
        result_dict = [ObjectModel(**score.__dict__)  for score in scores_top]

        return result_dict
