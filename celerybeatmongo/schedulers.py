"""The periodic task scheduler."""
from __future__ import absolute_import, unicode_literals

from celery import current_app
from celery.utils.log import get_logger
from celery.beat import Scheduler

from pymongo import MongoClient
from marshmallow.exceptions import ValidationError

from . import __version__
from .schemas import EntrySchema, ScheduleMetadataSchema


__all__ = [
    'MongoPersistentScheduler'
]

logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)


class MongoPersistentScheduler(Scheduler):
    """Scheduler backed by :mod:`MongoDB` database."""

    def _clear_entries(self):
        info("MongoPersistentScheduler: Clearing all persisted schedule data.")
        self._meta_col.delete_many({})
        self._entries_col.delete_many({})

    def _update_meta(self, meta):
        serial_meta = ScheduleMetadataSchema(strict=True).dump(meta).data
        self._meta_col.find_one_and_replace({}, serial_meta, upsert=True)

    def _fetch_meta(self):
        metas = self._meta_col.find()
        if metas.count() > 1:
            warning("MongoPersistentScheduler: multiple metadatas found")

        if metas.count() == 0:
            return None

        return ScheduleMetadataSchema(strict=True).load(next(metas)).data

    def _fetch_entries(self):
        raw_entries = list(self._entries_col.find())
        entries = EntrySchema(many=True, strict=True).load(raw_entries).data
        return dict( (e.name, e) for e in entries )

    def _update_entries(self, entries):
        serial_entries = EntrySchema(many=True, strict=True).dump(entries).data
        self._entries_col.delete_many({})
        if len(serial_entries) > 0:
            self._entries_col.insert_many(serial_entries)

    def setup_schedule(self):
        # Only supports URI config right now, other connection methods should
        # be easy to support.
        db_uri = getattr(current_app.conf,
                         "CELERY_MONGO_SCHEDULER_URI",
                         "mongodb://localhost:27017/celerybeat")

        db_entries_col = getattr(current_app.conf,
                                 "CELERY_MONGO_SCHEDULER_ENTRIES_COL",
                                 "celerybeat_entries")

        db_meta_col = getattr(current_app.conf,
                              "CELERY_MONGO_SCHEDULER_META_COL",
                              "celerybeat_meta")

        info("MongoPersistentScheduler: using %s:%s,%s",
             db_uri, db_entries_col, db_meta_col)

        self._db = MongoClient(db_uri).get_default_database()
        self._entries_col = self._db[db_entries_col]
        self._meta_col = self._db[db_meta_col]

        try:
            meta = self._fetch_meta()
        except ValidationError as e:
            warning("MongoPersistentScheduler: invalid metadata schema. %s",
                    e.messages)
            self._clear_entries()
            meta = None

        try:
            self._fetch_entries()
        except ValidationError as e:
            warning("MongoPersistentScheduler: invalid entries schema: %s",
                    e.messages)
            self._clear_entries()

        tz = self.app.conf.timezone
        utc = self.app.conf.enable_utc
        if meta is not None:
            if meta['tz'] != tz:
                warning('MongoPersistentScheduler: Reset - Timezone changed from %r to %r', stored_tz, tz)
                self._clear_entries()   # Timezone changed, reset db!
            if meta['utc_enabled'] != utc:
                choices = {True: 'enabled', False: 'disabled'}
                warning('Reset: UTC changed from %s to %s',
                        choices[stored_utc], choices[utc])
                self._clear_entries()   # UTC setting changed, reset db!

        self.schedule = self._fetch_entries()
        self.merge_inplace(self.app.conf.beat_schedule)
        self.install_default_entries(self.schedule)
        self._update_meta({
            str('version'): __version__,
            str('tz'): tz,
            str('utc_enabled'): utc,
        })
        self.sync()
        entries = self._fetch_entries()
        debug('Current schedule:\n' + '\n'.join(
            repr(entry) for entry in entries.values()))

    def sync(self):
        self._update_entries(self.schedule.values())

    def close(self):
        self.sync()


