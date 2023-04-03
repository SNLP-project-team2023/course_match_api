from apiflask import Schema, fields


# TODO my course link, sisu link
class Course(Schema):
    """Course schema"""
    name = fields.String()
    code = fields.String()
    language = fields.String()
    period = fields.String()
    link = fields.String()
    credits = fields.Integer()
