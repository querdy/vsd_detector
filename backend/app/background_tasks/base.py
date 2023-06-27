import asyncio
from asyncio import CancelledError
from typing import Callable


__all__ = ['add_bg_task', 'get_tasks', 'cancel_tasks']

from httpx import ReadTimeout
from loguru import logger

_background_tasks: set[asyncio.Task] = set()


def exception_trap(task: asyncio.Task):
    try:
        task.result()
    except ReadTimeout as e:
        logger.error(f'{e}')
    except CancelledError:
        logger.debug(f'Корутины предварительно прерваны')
    except Exception:
        logger.exception('Неизвестная ошибка = %r', task)


async def add_bg_task(func: Callable, **kwargs):
    task = asyncio.create_task(func(**kwargs))
    _background_tasks.add(task)
    task.add_done_callback(exception_trap)
    task.add_done_callback(_background_tasks.discard)


def get_tasks():
    return _background_tasks


def cancel_tasks():
    for task in _background_tasks:
        task.cancel()
