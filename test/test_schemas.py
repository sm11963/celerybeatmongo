import pytest
import time
from datetime import timedelta, datetime, timezone

from celery.beat import Scheduler, ScheduleEntry
from celery import schedules

from celerybeatmongo.schemas import (IntervalScheduleSchema, ScheduleSchema, EntrySchema, ScheduleMetadataSchema)
from marshmallow.exceptions import ValidationError


class TestIntervalSchema():

    def test_seralization_1(self):
        isch = schedules.schedule(run_every=timedelta(minutes=23),
                                  relative=True,
                                  nowfun=time.time)
        dumped = IntervalScheduleSchema(strict=True).dump(isch).data
        loaded = IntervalScheduleSchema(strict=True).load(dumped).data

        assert isch.run_every == loaded.run_every
        assert isch.relative == loaded.relative
        assert loaded.nowfun is None

    def test_seralization_2(self):
        isch = schedules.schedule(run_every=timedelta(days=3), relative=False)
        dumped = IntervalScheduleSchema(strict=True).dump(isch).data
        loaded = IntervalScheduleSchema(strict=True).load(dumped).data

        assert isch.run_every == loaded.run_every
        assert isch.relative == loaded.relative
        assert isch.nowfun == loaded.nowfun


class TestScheduleSchema():

    def test_interval(self):
        isch = schedules.schedule(run_every=timedelta(days=3))

        dumped = ScheduleSchema(strict=True).dump(isch).data
        loaded = ScheduleSchema(strict=True).load(dumped).data

        assert isch.run_every == loaded.run_every
        assert isch.relative == loaded.relative

    def test_empty_fails(self):
        data = {}
        with pytest.raises(ValidationError):
            loaded = ScheduleSchema(strict=True).load(data).data

    def test_dump_bad_type_fails(self):
        s = 'string'
        with pytest.raises(TypeError):
            dumped = ScheduleSchema(strict=True).dump(s).data

    def test_load_bad_type_fails(self):
        data = {'schedule_type': 'string', 'string': 'hi'}
        with pytest.raises(ValidationError):
            loaded = ScheduleSchema(strict=True).load(data).data


class TestEntrySchema():

    def test_seralization_1(self):
        sch = schedules.schedule(run_every=timedelta(seconds=365))
        date = datetime(2017, 5, 3, 23, 3, 47)
        entry = ScheduleEntry(name='everytime',
                              task='celery.runtask',
                              schedule=sch,
                              args=['hello', 'world', 5],
                              kwargs={'time': 4, 'name': 'testers'},
                              options={'echo': True},
                              last_run_at=datetime.now(timezone.utc),
                              total_run_count=99)

        dumped = EntrySchema(strict=True).dump(entry).data
        loaded = EntrySchema(strict=True).load(dumped).data

        assert entry.name == loaded.name
        assert entry.task == loaded.task
        assert entry.schedule.run_every == loaded.schedule.run_every
        assert entry.args == loaded.args
        assert entry.kwargs == loaded.kwargs
        assert entry.options == loaded.options
        assert entry.last_run_at == loaded.last_run_at
        assert entry.total_run_count == loaded.total_run_count


