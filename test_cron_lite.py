#!/usr/bin/env python3.6
# coding: utf-8
from cron_lite import cron_task, start_all, stop_all
import time


def run_tests():
    @cron_task("* * * * * 0/2")
    def event1():
        print("event1", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        time.sleep(3)
        print("event1 done", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    @cron_task("* * * * * 0/15")
    def event2():
        print("event2", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        time.sleep(10)
        print("event2 done", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    th = start_all(spawn=True)
    print("start")
    time.sleep(60)
    print("stop")
    stop_all(th)
    print("done")


if __name__ == '__main__':
    run_tests()
