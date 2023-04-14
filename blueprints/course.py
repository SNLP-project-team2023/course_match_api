import os

from apiflask import APIBlueprint

from scheduled.fetch_courses import get_saved_courses

from schemas.course import CourseAlias

course_blueprint = APIBlueprint('course', __name__)


@course_blueprint.get('/courses')
@course_blueprint.output(CourseAlias(many=True))
def get_courses():
    courses = get_saved_courses()

    result = []
    for index, row in courses.iterrows():
        course = CourseAlias()
        course.name = row["name"]
        course.code = row["code"]

        result.append(course)

    return result


