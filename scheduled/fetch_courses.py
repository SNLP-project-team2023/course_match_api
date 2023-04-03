import logging
import os
import pickle

import requests
import pandas as pd
import html
import re

from scheduled.load_model import get_saved_model

courses_path = "model/courses.pickle"
embeddings_path = "model/embeddings.pickle"


def clean_html(raw_html):
    """
    Cleans html tags from text

    Args:
        raw_html (str): Raw html text
    Returns:
        text: text without html tags
    """
    cleaner = re.compile('<.*?>')
    cleaned_text = re.sub(cleaner, '', raw_html)
    return cleaned_text


def preprocess_courses(courses):
    """
    Preprocess courses by dropping unnecessary fields

    Args:
        courses (pd.Frame): Raw course data
    Returns:
        processed_courses: pre-processed course data
    """
    courses = courses[
        [
            "id",
            "code",  # MYCOURSE URL param
            "name.en",
            "courseUnitId",  # SISU URL param
            "languageOfInstructionCodes",
            "credits.max",
            "summary.learningOutcomes.en",
            "summary.content.en",
            "summary.teachingPeriod.en"
        ]
    ]

    courses = courses.rename(columns={
        "summary.learningOutcomes.en": "learningOutcomes",
        "summary.content.en": "content",
        "credits.max": "credits",
        "name.en": "name",
        "summary.teachingPeriod.en": "teachingPeriod"
    })

    # remove duplicates
    courses = courses.drop_duplicates(subset=["code"], keep="first")
    courses = courses.reset_index(drop=True)

    # remove courses that have content or learning outcomes empty
    courses = courses[~((courses['content'] == '') |
                        (courses['learningOutcomes'] == ''))]

    courses['name'] = courses['name'].apply(html.unescape)
    courses['content'] = courses['content'].apply(html.unescape)
    courses['content'] = courses['content'].apply(clean_html)
    courses['learningOutcomes'] = courses['learningOutcomes'].apply(html.unescape)
    courses['learningOutcomes'] = courses['learningOutcomes'].apply(clean_html)
    courses['teachingPeriod'] = courses['teachingPeriod'].apply(html.unescape)
    courses['languageOfInstructionCodes'] = courses['languageOfInstructionCodes'].apply(lambda x: x[0])

    # Concat content and learning outcomes to form desc with is used for calculating embeddings
    courses['desc'] = courses['content'] + ' ' + courses['learningOutcomes']

    del courses['content']
    del courses['learningOutcomes']
    return courses


def encode_courses(courses):
    """
    Encodes courses to embeddings

    Args:
        courses (pd.Frame): Course data
    Returns:
        corpus_embeddings: course description embeddings
    """
    model = get_saved_model()
    course_embeddings = model.encode(
        courses['desc'].tolist(), convert_to_tensor=True)

    return course_embeddings


def fetch_courses():
    """
    Fetches course from Aalto API gateway, clean the data and save the embeddings and data into files
    """
    logging.debug("Loading courses")

    if not os.path.isfile(courses_path) and not os.path.isfile(embeddings_path):

        api_url = os.getenv('COURSE_API_URL')
        api_key = os.getenv('COURSE_API_KEY')
        r = requests.get(api_url + api_key)

        # get data
        raw_data = r.json()

        en_data = [
            course for course in raw_data if 'en' in course['languageOfInstructionCodes']]

        logging.debug("Processing courses")
        courses = pd.json_normalize(en_data)
        courses = preprocess_courses(courses)
        course_embeddings = encode_courses(courses)

        output_file = open(courses_path, 'wb')
        pickle.dump(courses, output_file)
        output_file.close()

        output_file = open(embeddings_path, 'wb')
        pickle.dump(course_embeddings, output_file)
        output_file.close()

    logging.debug("Courses saved")


def get_saved_courses():
    """
    Gets saved courses

    Returns:
        courses: saved courses
    """
    return pickle.load(open(courses_path, "rb"))


def get_saved_embeddings():
    """
    Gets saved embeddings

    Returns:
        embeddings: saved embeddings
    """
    return pickle.load(open(embeddings_path, "rb"))