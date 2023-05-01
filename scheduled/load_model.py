import pickle
from sentence_transformers import SentenceTransformer, util
import os
import logging

model_path = "model/model.pickle"


def load_model():
    """
    Loads model on start and save with pickle
    """
    logging.debug("Loading model")

    if not os.path.exists("model"):
        os.mkdir("model")

    if not os.path.isfile(model_path):

        model_name = os.getenv('SBERT_MODEL')
        model = SentenceTransformer(model_name, device='cpu')

        output_file = open(model_path, 'wb')
        pickle.dump(model, output_file)
        output_file.close()

    logging.debug("Finished loading model")


def get_saved_model():
    """
    Gets saved model

    Returns:
        model: saved model
    """
    return pickle.load(open(model_path, "rb"))
