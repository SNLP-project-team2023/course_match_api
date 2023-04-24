from sentence_transformers import losses, InputExample
from torch.utils.data import DataLoader
import os
import pickle
import logging
import random

from scheduled.fetch_courses import encode_courses
from scheduled.load_model import get_saved_model
from scheduled.fetch_courses import get_saved_courses

model_path = "model/model.pickle"
embeddings_path = "model/embeddings.pickle"
feedback_path = "model/feedback.pickle"
old_feedback_path = "model/old_feedback.pickle"
feedbackToUse = 99


def clear_feedback():
    """
    Clears feedback
    """
    # save old feedback to file
    if not os.path.isfile(old_feedback_path):
        output_file = open(old_feedback_path, 'wb')
        pickle.dump([], output_file)
        output_file.close()

    feedback = pickle.load(open(feedback_path, "rb"))
    old_feedback = pickle.load(open(old_feedback_path, "rb"))
    old_feedback.extend(feedback)

    output_file = open(old_feedback_path, 'wb')
    pickle.dump(old_feedback, output_file)
    output_file.close()

    # clear feedback
    output_file = open(feedback_path, 'wb')
    pickle.dump([], output_file)
    output_file.close()


def fine_tune_model():
    """
    Fine-tunes the model with new feedback
    """
    logging.debug("Fine-tuning model")

    # load the feedback
    if not os.path.isfile(feedback_path):
        output_file = open(feedback_path, 'wb')
        pickle.dump([], output_file)
        output_file.close()
    feedback = pickle.load(open(feedback_path, "rb"))

    # Fine-tune the model every 100 new feedbacks
    if len(feedback) > 0 and len(feedback) > feedbackToUse:
        # load the pre-trained model
        model = get_saved_model()

        # define the train dataset, the dataloader and the train loss
        train_dataloader = DataLoader(feedback, shuffle=True, batch_size=16)
        train_loss = losses.CosineSimilarityLoss(model)

        # tune the model
        model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=100, show_progress_bar=True)

        # save the model
        output_file = open(model_path, 'wb')
        pickle.dump(model, output_file)
        output_file.close()

        # recalculate the embeddings
        courses = get_saved_courses()
        course_embeddings = encode_courses(courses)
        output_file = open(embeddings_path, 'wb')
        pickle.dump(course_embeddings, output_file)
        output_file.close()

        # clear the feedback
        clear_feedback()

    logging.debug("Finished fine-tuning model")