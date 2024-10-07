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
    asyncio.create_task(
        _run_after_delay(
            func, *args, delay=delay, periodic=periodic, count=count, **kwargs
        )
    )


async def _run_after_delay(func, /, *args, delay, periodic, count, **kwargs):
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
