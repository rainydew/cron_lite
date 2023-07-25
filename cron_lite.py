#!/usr/bin/env python3.6
# coding: utf-8
from functools import wraps
from croniter import croniter
from typing import Optional, Dict, Callable
from datetime import datetime
import sched
import time
import traceback
import threading
import pytz

scheduler_map: Dict[Callable, sched.scheduler] = {}
_switch = False
_error_handler = print
_info_handler = print
_time_zone: Optional[pytz.BaseTzInfo] = None


def set_time_zone(time_zone_name: str):
    global _time_zone
    _time_zone = pytz.timezone(time_zone_name)


def _register_next(base_func, cron_expr, till_time_stamp):
    cron_obj = croniter(cron_expr)
    if _time_zone:
        cron_obj.set_current(datetime.now(tz=_time_zone))
    next_time = int(cron_obj.get_next())
    if scheduler_map.get(base_func) is None:
        scheduler_map[base_func] = sched.scheduler(time.time, time.sleep)
    if till_time_stamp is None or next_time <= till_time_stamp:
        scheduler_map[base_func].enterabs(next_time, 0, base_func)


def _run_sched(scheduler: sched.scheduler):
    while True:
        if not _switch:
            scheduler.empty()
            return
        t = scheduler.run(False)
        if t is None:
            return
        st = time.time()
        while time.time() - st < t:
            if not _switch:
                scheduler.empty()
                return
            time.sleep(1)


def _start():
    global _switch
    _info_handler("cron started")
    tl = []
    for base_func, scheduler in scheduler_map.items():
        print("Registering Job:", base_func.__name__)
        t = threading.Thread(target=_run_sched, args=(scheduler, ), daemon=True)
        # 有些task非常耗时，会影响退出。目前设计改为退出时不保证task完成
        t.start()
        tl.append(t)

    for t in tl:
        t.join()
    _info_handler("cron finished")
    _switch = False  # ensure close when there are no more tasks with switch open
    scheduler_map.clear()


def cron_task(cron_expr: str, till_time_stamp: int = None):
    """
    cron_task decorator to register a function as crontab task
    :param cron_expr: the croniter accepted cron_expression. NOTICE: the default timezone is UTC and can be changed by
    `set_time_zone`. The format is `min hour day month weekday [sec]`
    :param till_time_stamp: run this jog till when. None means forever
    :return: the real decorator
    """
    assert len(cron_expr.split(" ")) in (5, 6), \
        "only supported <min hour day month weekday> and <min hour day month weekday sec>"

    def deco(func):
        @wraps(func)
        def inner():
            try:
                func()
            except Exception:
                try:
                    _error_handler(f"run {func.__name__} failed\n" + traceback.format_exc())
                except Exception:
                    _error_handler(f"run {func.__name__} failed\n")
            _register_next(inner, cron_expr, till_time_stamp)

        _register_next(inner, cron_expr, till_time_stamp)
        return inner
    return deco


def start_all(spawn: bool = True, info_handler=None, error_handler=None) -> Optional[threading.Thread]:
    """
    start_all starts all cron tasks registered before.
    :param spawn: whether to start a new thread for scheduler. If not, the action will block the current thread
    :param info_handler: handle info output (scheduler start / stop), default = print, can use logging.info
    :param error_handler: handle error output (task execute exception), default = print, can use logging.error
    :raise RuntimeError: if the tasks are already started and still running we cannot start again. The feature is not
    concurrent-safe
    :return: the new thread if spawn = True
    """
    global _switch, _info_handler, _error_handler
    if _switch:
        raise RuntimeError("the crontab was already started")
    if info_handler:
        _info_handler = info_handler
    if error_handler:
        _error_handler = error_handler

    _switch = True
    if spawn:
        t = threading.Thread(target=_start)
        t.setDaemon(True)
        t.start()
        return t
    else:
        _start()


def stop_all(wait_thread: Optional[threading.Thread] = None):
    """
    stop_all turns off the switch to stop the scheduler. Running jobs will be wait till finished.
    :param wait_thread: join() the spawned scheduler thread (if you started it as spawn and you want) to ensure all jobs
    to finish
    :return:
    """
    global _switch
    _switch = False
    if wait_thread:
        wait_thread.join()
