from apiflask import Schema, fields


class Course(Schema):
    """Course schema"""
    name = fields.String(required=True)
    code = fields.String(required=True)
    language = fields.String(required=True)
    desc = fields.String()
    period = fields.String()
    sisu_link = fields.String()
    mycourses_link = fields.String()
    credits = fields.Integer(required=True)


class CourseAlias(Schema):
    """Course Alias schema"""
    name = fields.String(required=True)
    code = fields.String(required=True)
