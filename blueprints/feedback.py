from apiflask import APIBlueprint, fields
from flask import request
from schemas.feedback import Feedback
from scheduled.fetch_courses import get_saved_courses

from sentence_transformers import InputExample
import os
import pickle

feedback_blueprint = APIBlueprint('feedback', __name__)

feedback_path = "model/feedback.pickle"


def save_feedback(query_text, match_text, label):
    """
    Saves feedback

    Args:
        query_text (str): query text
        match_text (str): match text
        label (float): label
    """

    if not os.path.isfile(feedback_path):
        output_file = open(feedback_path, 'wb')
        pickle.dump([], output_file)
        output_file.close()

    feedback = pickle.load(open(feedback_path, "rb"))
    feedback.append(InputExample(texts=[query_text, match_text], label=label))

    output_file = open(feedback_path, 'wb')
    pickle.dump(feedback, output_file)
    output_file.close()


@feedback_blueprint.post('/feedback')
@feedback_blueprint.output(Feedback)
@feedback_blueprint.input(Feedback)
def feedback(feedback_data):
    """
    Saves feedback

    Args:
        feedback_data (Feedback): feedback data

    Returns:
        feedback: feedback
    """
    feedback = Feedback().load(feedback_data)
    
    if feedback['match_code'] != "":
        courses = get_saved_courses()
        feedback['query_text'] = courses.loc[courses['code'] == feedback['match_code']]['desc'].values[0]
    
    save_feedback(feedback['query_text'], feedback['match_text'], feedback['label'])

    return feedback