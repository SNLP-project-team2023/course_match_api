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
    Cleans text from html tags and beautifies it

    Args:
        raw_html (str): raw html text
    Returns:
        cleaned_text: cleaned text
    """
    cleaner = re.compile('<.*?>')
    cleaned_text = re.sub(cleaner, '', raw_html)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


def preprocess_courses(courses):
    """
    Preprocesses courses

    Args:
        courses (pd.Frame): raw course data
    Returns:
        courses: preprocessed courses
    """
    courses = courses[
        [
            "id",
            "code",  # MYCOURSES URL param
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

    # remove courses that have content and learning outcomes empty
    courses = courses[~((courses['content'] == '') &
                        (courses['learningOutcomes'] == ''))]

    courses['name'] = courses['name'].apply(html.unescape)
    courses['content'] = courses['content'].apply(html.unescape)
    courses['content'] = courses['content'].apply(clean_html)
    courses['learningOutcomes'] = courses['learningOutcomes'].apply(html.unescape)
    courses['learningOutcomes'] = courses['learningOutcomes'].apply(clean_html)
    courses['teachingPeriod'] = courses['teachingPeriod'].apply(html.unescape)
    courses['teachingPeriod'] = courses['teachingPeriod'].apply(clean_html)
    courses['languageOfInstructionCodes'] = courses['languageOfInstructionCodes'].apply(lambda x: x[0])

    # concat content and learning outcomes to form desc, which is used for encoding
    courses['desc'] = courses['content'] + ' ' + courses['learningOutcomes']

    del courses['content']
    del courses['learningOutcomes']

    return courses


def encode_courses(courses):
    """
    Encodes courses to embeddings

    Args:
        courses (pd.Frame): course data
    Returns:
        course_embeddings: encoded courses
    """
    model = get_saved_model()
    course_embeddings = model.encode(
        courses['desc'].tolist(), convert_to_tensor=True)

    return course_embeddings


def fetch_courses(first_run=False):
    """
    Fetches course from Aalto API gateway, clean the data and save the embeddings and data into files

    Args:
        first_run (bool): is this run first time
    """
    logging.debug("Loading courses")

    if (not os.path.isfile(courses_path) or not os.path.isfile(embeddings_path)) or not first_run:
        
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
