#!/usr/bin/env python3.6
# coding: utf-8
import sched
import threading
import time
import traceback
from typing import Optional, Dict, Callable

from croniter import croniter

scheduler_map: Dict[Callable, sched.scheduler] = {}
_switch = False
_error_log_handler = print
_info_log_handler = print


def _reigster_next(base_func, cron_expr, till_time_stamp):
    next_time = int(croniter(cron_expr).get_next())
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
        time.sleep(t)


def _start():
    global _switch
    _info_log_handler("cron started")
    tl = []
    for scheduler in scheduler_map.values():
        t = threading.Thread(target=_run_sched, args=(scheduler,))
        t.start()
        tl.append(t)
    for t in tl:
        t.join()
    _info_log_handler("cron finished")
    _switch = False  # ensure close when there are no more tasks with switch open
    scheduler_map.clear()


def cron_task(cron_expr: str, till_time_stamp: int = None):
    """
    cron_task decorator to register a function as crontab task
    :param cron_expr: the croniter accepted cron_expression
    :param till_time_stamp: run this jog till when. None means forever
    :return: the real decorator
    """
    assert len(cron_expr.split(" ")) in (5, 6), \
        "only supported <min hour day year weekday> and <min hour day year weekday sec>"

    def deco(func):
        def inner():
            try:
                func()
            except:
                _error_log_handler(f"run {func.__name__} failed\n" + traceback.format_exc())
            _reigster_next(inner, cron_expr, till_time_stamp)

        _reigster_next(inner, cron_expr, till_time_stamp)
        return inner

    return deco


def start_all(spawn: bool = True, info_log_handler=None, error_log_handler=None) -> Optional[threading.Thread]:
    """
    start_all starts all cron tasks registered before.
    :param spawn: whether to start a new thread for scheduler. If not, the action will block the current thread
    :param info_log_handler: handle info output (scheduler start / stop), default = print, can use logging.info
    :param error_log_handler: handle error output (task execute exception), default = print, can use logging.error
    :raise RuntimeError: if the tasks are already started and still running we cannot start again. The feature is not
    concurrency-safe
    :return: the new thread if spawn = True
    """
    global _switch, _info_log_handler, _error_log_handler
    if _switch:
        raise RuntimeError("the crontab was already started")
    if info_log_handler:
        _info_log_handler = info_log_handler
    if error_log_handler:
        _error_log_handler = error_log_handler

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
    :param wait_thread: join() the spawned scheduler thread (if you started it as spawn and you wish) to ensure all jobs
     to finish
    :return:
    """
    global _switch
    _switch = False
    if wait_thread:
        wait_thread.join()
