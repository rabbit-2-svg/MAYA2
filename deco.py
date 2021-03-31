import os
import time
import copy
import threading
import traceback
import queue as Queue
from functools import wraps
from common.hook import set_up, tear_down
from conf.test_conf import test_conf, tc_logger
from common.rwfile import write_csv_header, write_csv_result


def fake_deco_by_duration(duration, func, *args, **kw):
    duration = int(duration)
    main_start_time = int(time.time())
    main_current_time = main_start_time

    i = 0
    while (main_current_time - main_start_time) < duration:
        i = i + 1
        tc_logger.info("***** {} *****".format(i))
        set_up(level='loop', loop=i)

        if test_conf["event_trace"] is True:
            command = "{} {} > {} &".format(test_conf["event_trace_home"] + "/" + "trace_enable.sh",
                                            test_conf["device_id"],
                                            test_conf["log_home"] + "/" + "event_trace_" + str(i) + ".log")
            tc_logger.info("Enable event_trace with command: {}".format(command))
            os.system(command)
        func(*args, **kw)
        tear_down(level='loop', loop=i)
        if test_conf["event_trace"] is True:
            command = "{} {}".format(test_conf["event_trace_home"] + "/" + "trace_disable.sh", test_conf["device_id"])
            tc_logger.info("Disable event_trace with command: {}".format(command))
            os.system(command)
        main_current_time = int(time.time())
        if os.path.exists(test_conf["graceful_stop_point"]):
            tc_logger.info("File exists: " + test_conf["graceful_stop_point"])
            tc_logger.info("Exit loop before duration threshold")
            break

    tc_logger.info("Main Logic End Time = " + time.strftime("%Y-%m-%d  %H:%M:%S"))
    tc_logger.info("Main Logic End Time = " + str(int(time.time())))


def fake_deco_by_loops(loops, result_file, func, *args, **kw):
    i = 1
    loops = int(loops)
    while i <= loops:
        tc_logger.info("***** {} *****".format(i))
        set_up(level='loop', loop=i)
        if test_conf["event_trace"] is True:
            command = "{} {} > {} &".format(test_conf["event_trace_home"] + "/" + "trace_enable.sh",
                                            test_conf["device_id"],
                                            test_conf["log_home"] + "/" + "event_trace_" + str(i) + ".log")
            tc_logger.info("Enable event_trace with command: {}".format(command))
            os.system(command)
        result_header, result_value = func(*args, **kw)
        tear_down(level='loop', loop=i)
        if test_conf["event_trace"] is True:
            command = "{} {}".format(test_conf["event_trace_home"] + "/" + "trace_disable.sh", test_conf["device_id"])
            tc_logger.info("Disable event_trace with command: {}".format(command))
            os.system(command)
        result_header_copy = copy.deepcopy(result_header)
        result_header_copy.insert(0, "Loop")
        result_value.insert(0, str(i))
        write_csv_header(result_file, result_header_copy)
        write_csv_result(result_file, result_value)
        if os.path.exists(test_conf["graceful_stop_point"]):
            tc_logger.info("File exists: " + test_conf["graceful_stop_point"])
            tc_logger.info("Exit loop before duration threshold")
            break
        i = i + 1


def watchdog(timeout, func, *args, **kw):
    if test_conf["watchdog"] is not True:
        return func(*args, **kw)
    else:
        if timeout is None:
            timeout = int(test_conf.get("watchdog_timeout", 300))
        que = Queue.Queue(1)
        thread = threading.Thread(target=lambda q: q.put(func(*args, **kw)), args=(que,))
        thread.setDaemon(True)
        thread.start()
        try:
            result = que.get(timeout=timeout)
        except Queue.Empty:
            tc_logger.error("Watchgod TimeOut - {} seconds".format(str(timeout)))
            raise
        return result


def pass_fail_common_deco(default_result=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            case_name = func.__name__
            try:
                result = func(*args, **kw)
                if (result is None):
                    result = default_result
                if (result == 0 or result == "0"):
                    os.system("touch {}".format(test_conf["pass_indicator"]))
                    tc_logger.info('[PASS] -- Test case {}'.format(case_name))
                else:
                    os.system("touch {}".format(test_conf["fail_indicator"]))
                    tc_logger.info('[FAIL] -- Test case {}'.format(case_name))
            except Exception as e:
                os.system("touch {}".format(test_conf["exception_indicator"]))
                # traceback.print_exc()
                tc_logger.error(traceback.format_exc())
                tc_logger.info('[FAIL] -- Test case {}'.format(case_name))
        return wrapper
    return decorator


def skip_if(condition, reason):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if condition:
                tc_logger.info('[Skip] {}'.format(reason))
            else:
                func(*args, **kwargs)
        return wrapper
    return decorator


def _test(name, location):
    print("My name is " + name)
    time.sleep(2)
    print(name)
    return name + "@" + location


def fake_deco_by_loops_ffu(loops, func, *args, **kw):
    i = 1
    loops = int(loops)
    while i <= loops:
        tc_logger.info("***** {} *****".format(i))
        set_up(level='loop', loop=i)
        if test_conf["event_trace"] is True:
            command = "{} {} > {} &".format(test_conf["event_trace_home"] + "/" + "trace_enable.sh",
                                            test_conf["device_id"],
                                            test_conf["log_home"] + "/" + "event_trace_" + str(i) + ".log")
            tc_logger.info("Enable event_trace with command: {}".format(command))
            os.system(command)
        func(*args, **kw)
        tear_down(level='loop', loop=i)
        if test_conf["event_trace"] is True:
            command = "{} {}".format(test_conf["event_trace_home"] + "/" + "trace_disable.sh", test_conf["device_id"])
            tc_logger.info("Disable event_trace with command: {}".format(command))
            os.system(command)
        if os.path.exists(test_conf["graceful_stop_point"]):
            tc_logger.info("File exists: " + test_conf["graceful_stop_point"])
            tc_logger.info("Exit loop before duration threshold")
            break
        i = i + 1

# @pass_fail_common_deco()
# def _test_none1():
#     print ("This test is designed to return None")
#
# @pass_fail_common_deco(0)
# def _test_none2():
#     print ("This test is designed to return None")
#
# @pass_fail_common_deco()
# def _test_pass1():
#     print ("This test is designed to return number 0")
#     return 0
#
# @pass_fail_common_deco()
# def _test_pass2():
#     print ("This test is designed to return string 0")
#     return "0"
#
# @pass_fail_common_deco(0)
# def _test_fail1():
#     print ("This test is designed to return number 1")
#     return 1
#
# @pass_fail_common_deco(0)
# def _test_fail2():
#     print ("This test is designed to return string 1")
#     return "1"
#
# @pass_fail_common_deco(0)
# def _test_others():
#     print ("This test is designed to return a tuple")
#     return 0,1,2,3
#
# @pass_fail_common_deco(0)
# def _test_exception():
#     print ("This test is designed to raise an exception")
#     raise Exception ("I'm dead now!!!")
#     return 0

if __name__ == "__main__":
    _test_exception()
    # print(watchdog(1, _test, "Monkey", location="Shanghai"))
    # fake_deco_by_duration(5, _test, "Monkey")
