# celerybeatmongo
A very simple Celery Beat Scheduler that stores status information in a MongoDB database.

# Install

```
pip install celerybeatmongo
```

# Details

This project provides a Celery Beat Scheduler that uses MongoDB to store the schedule stats (last run, run count, etc.). This is safer than using a file on your server which could be cleared or corrupted (on Heroku for example). This scheduler aims to replace the default Beat Scheduler provided with Celery. There are a few caveats though:

* Only supports interval scheduling (currently, easy to add support for Crontab and Solar)
* Can only pass native JSON types (dict, list, str, number) to `kwargs`, `args`, and `options` for tasks

## Motivation

I started this project because I run Celerybeat on Heroku and I started noticing that tasks were being dropped. This was because the default Celerybeat Scheduler (`[celery.beat.PersistentScheduler](http://docs.celeryproject.org/en/latest/reference/celery.beat.html#celery.beat.PersistentScheduler)`) uses a shelve database file that it adds the current directory. In Heroku this file was cleared and so the schedule data was not saved reliably. With the `celerybeatmongo.MongoPersistentScheduler` this is not an issue anymore.

# Example

Please see `examples/celery_worker.py` for a simple example to just try it out. 

Running the example requires MongoDB and Redis (you can edit it to use another Broker instead if Redis if you want).
* [Install Redis](https://redis.io/topics/quickstart)
* [Install MongoDB](https://docs.mongodb.com/manual/installation/)

You can run the following to start the example:

1. In a seperate terminal window, start Redis:
 ```shell
 $ redis-server      # start redis
 ```

2. In a seperate terminal window, start MongoDB:
 ```shell
 $ mongod
 ```

3. Then start the example worker:
 ```shell
 $ pip install redis
 $ python examples/celery_worker.py
 ```


# Contribute

Please add issues or put up pull requests if you need more functionality or have suggestions. Its a new project and should be easy to contribute to!
