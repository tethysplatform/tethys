"""
********************************************************************************
* Name: tasks.py
* Author: Scott Christensen
* Created On: 2024
* Copyright: (c) Tethys Geospatial Foundation 2024
* License: BSD 2-Clause
********************************************************************************
"""

import asyncio
import logging

logger = logging.getLogger(f"tethys.{__name__}")


def create_task(func, /, *args, delay=0, periodic=False, count=None, **kwargs):
    """
    Schedules a task to be executed after some delay. This is run asynchronously and must be called from a context
    where there is an active event loop (e.g. from a controller).

    Can be set to run periodically (i.e. it will be rescheduled after it is run) either indefinitely or for a
    specified number of times.
    Args:
        func (callable): the function to schedule
        *args: args to pass to the function when it is called
        delay (int): number of seconds to wait before executing `func` or between calls if `periodic=True`
        periodic (bool): if `True` the function will be rescheduled after each execution until `count=0` or
            indefinitely if `count=None`
        count (int): the number of times to execute the function if `periodic=True`. If `periodic=False` then
            this argument is ignored
        **kwargs: key-word arguments to pass to `func`
    """
    asyncio.create_task(
        _run_after_delay(
            func, *args, delay=delay, periodic=periodic, count=count, **kwargs
        )
    )


async def _run_after_delay(func, /, *args, delay, periodic, count, **kwargs):
    """
    Helper function to `create_task` that delays before executing a function. It is called recursively to handle
    `periodic` tasks.

    Args:
        func (callable): the function to schedule
        *args: args to pass to the function when it is called
        delay (int): number of seconds to wait before executing `func` or between calls if `periodic=True`
        periodic (bool): if `True` the function will be rescheduled after each execution until `count=0` or
            indefinitely if `count=None`
        count (int): the number of times to execute the function if `periodic=True`. If `periodic=False` then
            this argument is ignored
        **kwargs: key-word arguments to pass to `func`
    """
    await asyncio.sleep(delay)
    try:
        logger.info(f'Running task "{func}" with args="{args}" and kwargs="{kwargs}".')
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            await result
    except Exception as e:
        logger.info(
            f'The following error occurred while running the task "{func}": {e}'
        )
    if periodic and (count is None or count > 0):
        if isinstance(count, int):
            count -= 1
        asyncio.create_task(
            _run_after_delay(
                func, *args, delay=delay, periodic=periodic, count=count, **kwargs
            )
        )


background_tasks = []


def background_task(func=None, delay=0, period=0, count=None):
    def wrapped(func):
        background_tasks.append((func, delay, period, count))
        return func

    return wrapped if func is None else wrapped(func)


def process_background_tasks():
    for func, delay, period, count in background_tasks:
        logger.info(f"Starting background task {func.__module__}.{func.__name__} with {delay=} {period=} {count=}")
        if count is None or count > 0:
            create_task(func, delay=delay)
        if count is None or count > 1:
            if count and count > 1:
                count -= 2  # since tethys calls it one extra time
            reactor.callLater(delay, partial(create_task, delay=period), func, periodic=True, count=count)


def get_countdown(time):
    """Gets the number of seconds until `time`. If `time` has already passed on the current day,
    then the number of seconds until `time` on the following day.

    Args:
        time: datetime.time object, integer (between 0-23), or string in the format (00[:00[:00]])
            representing a time of doy.

    Returns: (int) Number of seconds until the next `time`.

    """
    usage_message = (
        'The "time" argument must be a datetime.time object, an integer between 0 and 24,'
        ' or a string in the format "00:00:00".'
    )
    if isinstance(time, datetime.time):
        until_time = time
    else:
        m = re.match(r"(?P<hours>\d\d?)(?::(?P<minutes>\d\d?)(?::(?P<seconds>\d\d?))?)?", str(time))
        if m is None:
            raise ValueError(usage_message)
        hours, minutes, seconds = [int(i) if i is not None else 0 for i in m.groups()]
        until_time = datetime.time(hours, minutes, seconds)

    delay_until_time = datetime.datetime.combine(datetime.date.today(), until_time) - datetime.datetime.now()
    if delay_until_time.days < 0:
        delay_until_time += datetime.timedelta(hours=24)
    return delay_until_time.seconds


reactor.callLater(0, process_background_tasks)
