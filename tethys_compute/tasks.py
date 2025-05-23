"""
********************************************************************************
* Name: tasks.py
* Author: Scott Christensen
* Created On: 2024
* Copyright: (c) Tethys Geoscience Foundation 2024
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
