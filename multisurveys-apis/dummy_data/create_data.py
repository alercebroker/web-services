import polars as pl
import os
import numpy as np
import pprint
from db_plugins.db.sql._connection import PsqlDatabase
from sqlalchemy import text


db_config = {
    "USER": os.getenv("PSQL_USER"),
    "PASSWORD": os.getenv("PSQL_PASSWORD"),
    "DB_NAME": os.getenv("PSQL_DATABASE"),
    "HOST": os.getenv("PSQL_HOST"),
    "PORT": os.getenv("PSQL_PORT"),
    "SCHEMA": os.getenv("SCHEMA"),
}


def load_old_taxonomy():
    df = pl.read_csv("./taxonomy_public.csv")
    return df


def create_classifier_data(old_taxonomy_df):


    classifiers_names = old_taxonomy_df.get_column("classifier_name")
    classifier_id_array = [i for i in range(len(classifiers_names))]
    classifier_version = np.resize([0, 1], len(classifiers_names))


    data = {
        "classifier_id": classifier_id_array, 
        "classifier_name": classifiers_names,
        "classifier_version": classifier_version
    }

    df = pl.DataFrame(data)
    
    return df


def create_taxonomy_data(old_taxonomy_df):

    data = {
        "class_id": [],
        "class_name": [],
        "order": [],
        "classifier_name": [],
        "classifier_id": []
    }

    classifier_dict = classifiers_dict(old_taxonomy_df)

    index = 0
    for key, value in classifier_dict.items():
        data = stash_taxonomy_data(data, value, key, index)
        index += 1

    df = pl.DataFrame(data)

    return df


def classifiers_dict(old_taxonomy_df):
    classifiers_names = old_taxonomy_df.get_column("classifier_name")
    classes = old_taxonomy_df.get_column("classes")
    response_dict = {}

    for index, classifiers in enumerate(classifiers_names):
        response_dict[classifiers] = classes[index].strip('{}').split(',')

    return response_dict


def stash_taxonomy_data(data_dict, classes_arr, classifier_name, classifier_index):
    data_len = len(data_dict["class_id"])
    for index, class_name in enumerate(classes_arr):
        data_dict["class_id"].append(index + data_len)
        data_dict["class_name"].append(class_name)
        data_dict["order"].append(index+1)
        data_dict["classifier_name"].append(classifier_name)
        data_dict["classifier_id"].append(classifier_index)

    return data_dict

def save_data(data, table, conn):
    df = pl.DataFrame(data)
    
    df.write_database(
        table_name = table,
        connection = conn,
        if_table_exists = "replace"
    )

if __name__ == "__main__":

    psql = PsqlDatabase(db_config)
    engine = psql.get_engine()

    old_taxonomy_df = load_old_taxonomy()


    with engine.connect() as conn:
       df =  create_classifier_data(old_taxonomy_df)
       save_data(df, "classifier_ms", conn)
       
       df = create_taxonomy_data(old_taxonomy_df)
       save_data(df, "taxonomy_ms", conn)

