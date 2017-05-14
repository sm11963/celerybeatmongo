import marshmallow
from marshmallow.validate import OneOf
from marshmallow import fields

from celery.beat import Scheduler, ScheduleEntry
from celery import schedules

class IntervalScheduleSchema(marshmallow.Schema):
    run_every = fields.TimeDelta(required=True)
    relative = fields.Bool(default=False, missing=False)

    @marshmallow.post_load
    def make_schedule(self, data):
        return schedules.schedule(**data)


class ScheduleSchema(marshmallow.Schema):
    """
    Schema that allows serializing a subclass of schedule. To add
    a schedule simply add it to the cls_map which is a mapping from
    name to python class type and schema for serialization.
    """

    cls_map = {
        'interval': schedules.schedule
    }

    schedule_validator = OneOf(
        cls_map.keys(),
        error="Invalid schedule type '{input}' expected one of '{choices}'"
    )
    schedule_type = fields.Str(required=True, validate=schedule_validator)

    interval = fields.Nested(IntervalScheduleSchema, default=None, missing=None)

    @marshmallow.pre_dump
    def serialize_schedule(self, obj):
        cls_map = self.__class__.cls_map
        matches = (name for name, cls in cls_map.items()
                   if isinstance(obj, cls))
        stype = next(matches, None)

        if not stype:
            raise TypeError('Unsupported class type: {}'.format(obj.__class__))

        return {'schedule_type': stype, stype: obj}

    @marshmallow.post_load
    def make_schedule(self, data):
        return data[data['schedule_type']]


class EntrySchema(marshmallow.Schema):
    name = fields.Str(required=True)
    task = fields.Str(required=True)
    last_run_at = fields.DateTime(default=None, missing=None)
    total_run_count = fields.Integer(default=0, missing=0)
    schedule = fields.Nested(ScheduleSchema, required=True)
    args = fields.List(fields.Raw(), default=[], missing=[])
    kwargs = fields.Raw(default={}, missing={})
    options = fields.Raw(default={}, missing={})

    @marshmallow.post_load
    def make_entry(self, data):
        return ScheduleEntry(**data)


class ScheduleMetadataSchema(marshmallow.Schema):
    tz = fields.Str(required=True, allow_none=True)
    utc_enabled = fields.Bool(required=True)
    version = fields.Str(required=True)
