#!/usr/bin/env python3.6
# coding: utf-8
from croniter import croniter
from typing import Optional
import sched
import time
import traceback
import threading

scheduler = sched.scheduler(time.time, time.sleep)
_switch = False
_error_handler = print
_info_handler = print


def _reigster_next(base_func, cron_expr, till_time_stamp):
    next_time = int(croniter(cron_expr).get_next())
    if till_time_stamp is None or next_time <= till_time_stamp:
        scheduler.enterabs(next_time, 0, base_func)


def _start():
    global _switch
    _info_handler("cron started")
    while True:
        t = scheduler.run(False)
        if t is None or not _switch:
            _info_handler("cron finished")
            _switch = False  # ensure close when there are no more tasks with switch open
            return
        time.sleep(t)


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
                _error_handler(f"run {func.__name__} failed\n" + traceback.format_exc())
            _reigster_next(inner, cron_expr, till_time_stamp)

        _reigster_next(inner, cron_expr, till_time_stamp)
        return inner
    return deco


def start_all(spawn: bool = True, info_handler = None, error_handler = None) -> Optional[threading.Thread]:
    """
    start_all starts all cron tasks registered before.
    :param spawn: whether to start a new thread for scheduler. If not, the action will block the current thread
    :param info_handler: handle info output (scheduler start / stop), default = print, can use logging.info
    :param error_handler: handle error output (task execute exception), default = print, can use logging.error
    :raise RuntimeError: if the tasks are already started and still running we cannot start again. The feature is not concurrent-safe
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
    :param wait_thread: join() the spawned scheduler thread (if you started it as spawn) to ensure all jobs to finish
    :return:
    """
    global _switch
    _switch = False
    if wait_thread:
        wait_thread.join()


if __name__ == '__main__':
    @cron_task("* * * * * 0/3")
    def event1():
        print("event1", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    @cron_task("* * * * * 0/4")
    def event2():
        print("event2", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    t = start_all(spawn=True)
    time.sleep(9)
    stop_all(t)
    print("done")
