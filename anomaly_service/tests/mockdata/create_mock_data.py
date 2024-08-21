from utils import TOP_CLASSES, ALL_CLASSES

if __name__ == "__main__":

    import pickle
    import random
    import pandas as pd
    import numpy as np
    import uuid

    oids = [uuid.uuid4() for _ in range(5)]
    scores = np.abs(np.random.rand((5, 22)))
    scores_top = np.abs(np.random.rand((5, 22)))

    df_scores_top = pd.Dataframe(scores_top, index=oids, columns=ALL_CLASSES)
    df_scores = pd.Dataframe(scores, index=oids, columns=TOP_CLASSES)

    data = {"scores_top": df_scores_top, "scores": df_scores, "distributions": None}

    with open("mock_data.pickle", "wb") as file:
        pickle.dump(data, file)
