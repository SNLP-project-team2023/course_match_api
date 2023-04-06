from apiflask import Schema, fields


class Course(Schema):
    """Course schema"""
    name = fields.String()
    code = fields.String()
    language = fields.String()
    desc = fields.String()
    period = fields.String()
    sisu_link = fields.String()
    mycourses_link = fields.String()
    credits = fields.Integer()
