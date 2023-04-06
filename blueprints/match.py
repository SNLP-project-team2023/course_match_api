import os

from apiflask import APIBlueprint, fields, abort
from sentence_transformers import util

from scheduled.fetch_courses import get_saved_courses, get_saved_embeddings
from scheduled.load_model import get_saved_model
from schemas.course import Course

match_blueprint = APIBlueprint('match', __name__)


def top_k_courses(query_text, k, exclude_self=False):
    """
    Get top k courses

    Args:
        query_text (str): query text
        k (int): k
    Returns:
        top_courses: matched courses
    """
    model = get_saved_model()
    course_embeddings = get_saved_embeddings()
    courses = get_saved_courses()
    query_embedding = model.encode(query_text, convert_to_tensor=True)

    k = k + 1 if exclude_self else k
    hits = util.semantic_search(
        query_embedding, course_embeddings, score_function=util.dot_score, top_k=k)
    hit_idxs = [hit['corpus_id'] for hit in hits[0]]
    hit_idxs = hit_idxs[1:] if exclude_self else hit_idxs
    link_sisu_prefix = os.getenv('SISU_COURSE_PREFIX')
    link_mycourses_prefix = os.getenv('MYCOURSES_COURSE_PREFIX')

    top_courses = []

    for idx in hit_idxs:
        hit_course = courses.iloc[idx]
        course = Course()

        course.name = hit_course["name"]
        course.code = hit_course["code"]
        course.language = hit_course["languageOfInstructionCodes"]
        course.desc = hit_course["desc"]
        course.period = hit_course["teachingPeriod"]
        course.sisu_link = f'{link_prefix}{hit_course["courseUnitId"]}'
        course.mycourses_link = f'{link_mycourses_prefix}{hit_course["code"]}'
        course.credits = hit_course["credits"]

        top_courses.append(course)

    return top_courses


@match_blueprint.get('/match/<course_code>')
@match_blueprint.output(Course(many=True))
def match_code(course_code):
    courses = get_saved_courses()

    found_course = courses.loc[courses['code'] == course_code]

    if found_course.empty:
        abort(400)

    query_text = found_course.iloc[0]["desc"]

    return top_k_courses(query_text, 5, exclude_self=True)


@match_blueprint.get('/match/text')
@match_blueprint.output(Course(many=True))
@match_blueprint.input({"query_text": fields.String()}, location='query')
def match_text(query):
    query_text = query["query_text"]

    return top_k_courses(query_text, 5, exclude_self=False)

