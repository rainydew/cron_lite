# cron_lite
A very light library to run python functions like cron jobs do. (support cron expressions, decorator style, spawn running and graceful exit. Runs in python service like Apscheduler, no effect of system config)


### Example

```python
from cron_lite import cron_task, start_all, stop_all
import time


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


th = start_all(spawn=True)  # use bare `start_all()` to run forever as a service
print("start")
time.sleep(60)
print("stop")
stop_all(th)
print("done")
```
