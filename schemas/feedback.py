from apiflask import Schema, fields


class Feedback(Schema):
    """Feedback schema"""
    query_text = fields.String(required=True)
    match_text = fields.String(required=True)
    match_code = fields.String(required=True)
    label = fields.Float(required=True)