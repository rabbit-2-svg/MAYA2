import os
import re
import time
from multiprocessing import Process
from adb.adb import ADB
from common.device import Device
from common.rwfile import get_benchmark_item, get_column_from_csv, assert_values_meet_benchmark
from conf.test_conf import test_conf, tc_logger
from common.deco import pass_fail_common_deco
from common.hook import set_up, tear_down

ud_pre_case_string = ["scan_device", "get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "open_tw",
                      "restore_wb_cur_buf", "restore_wb_avail_buf", "enable_mtp"]
ud_post_case_string = ["get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "restore_wb_cur_buf",
                       "restore_wb_avail_buf"]


@pass_fail_common_deco()
def tc2_wb_function_sample():
    # test data and benchmark definition according to host environment
    result = 0
    if test_conf["chip_capacity"] == "256G":
        test_data = {
            "fio_file_size": "25G"
        }
        test_benchmark = {
            "fio_sw_time": {
                "min": 20,
                "max": 60,
                "comments": ["Initial Version"]
            },
            "abs_min": {
                "min": 0,
                "max": 0,
                "comments": ["available buffer size should be used up"]
            },
            "abs_max": {
                "min": 100,
                "max": 100,
                "comments": ["available buffer size should be able to recover to A within limited time"]
            },
            "abs_recover_time": {
                "min": 0,
                "max": 600,
                "comments": ["Initial Version"]
            },
            "flush_status_after_recover_1": {
                "min": 3,
                "max": 3,
                "comments": ["flush status should be set to 3 after abs recovered"]
            },
            "flush_status_after_recover_2": {
                "min": 0,
                "max": 0,
                "comments": ["flush status should be set to 0 after abs recovered and status read"]
            }
        }
    elif test_conf["chip_capacity"] == "128G":
        test_data = {
            "fio_file_size": "13G"
        }
        test_benchmark = {
            "fio_sw_time": {
                "min": 10,
                "max": 30,
                "comments": ["Initial Version"]
            },
            "abs_min": {
                "min": 0,
                "max": 0,
                "comments": ["available buffer size should be used up"]
            },
            "abs_max": {
                "min": 100,
                "max": 100,
                "comments": ["available buffer size should be able to recover to A within limited time"]
            },
            "abs_recover_time": {
                "min": 0,
                "max": 600,
                "comments": ["Initial Version"]
            },
            "flush_status_after_recover_1": {
                "min": 3,
                "max": 3,
                "comments": ["flush status should be set to 3 after abs recovered"]
            },
            "flush_status_after_recover_2": {
                "min": 0,
                "max": 0,
                "comments": ["flush status should be set to 0 after abs recovered and status read"]
            }
        }
    else:
        raise Exception("Unsupported chip capacity: " + test_conf["chip_capacity"])

    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")
    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string

    # pre case configuration
    set_up(level='case')

    # adb initialization
    adb = ADB(test_conf["device_id"])
    device = Device(test_conf["device_id"])

    # launch abs monitoring in backend
    def wb_func_abs_monitor(abs_use_up_timeout=60, abs_recover_timeout=60, monitor_interval=1, log_file=None):
        if log_file is None:
            log_file = os.path.join(test_conf["monitor_home"], "wb_func_abs_monitor.log")
        # device = Device(test_conf["device_id"])
        with open(log_file, "w") as f:
            f.write("monitor_start=" + str(time.time()) + os.linesep)

            # monitor whether abs can be used up
            time_start = time.time()
            while True:
                # monitor whether ads is used up
                time_now = time.time()
                if (time_now - time_start) > abs_use_up_timeout:
                    f.write("abs_use_up_ts=timeout" + os.linesep)
                    break
                else:
                    abs_now = device.get_wb_avail_buf()[1][0]
                    f.write(abs_now + os.linesep)
                    if abs_now == "0%":
                        f.write("abs_use_up_ts=" + str(time.time()) + os.linesep)
                        break
                f.flush()
                time.sleep(monitor_interval)

            # monitor whether abs can recover to 100%
            time_start = time.time()
            while True:
                # monitor whether ads is used up
                time_now = time.time()
                if (time_now - time_start) > abs_recover_timeout:
                    f.write("abs_recover_ts=timeout" + os.linesep)
                    break
                else:
                    abs_now = device.get_wb_avail_buf()[1][0]
                    f.write(abs_now + os.linesep)
                    if abs_now == "100%":
                        f.write("abs_recover_ts=" + str(time.time()) + os.linesep)
                        break
                f.flush()
                time.sleep(monitor_interval)
    p = Process(target=wb_func_abs_monitor,
                args=[test_benchmark["fio_sw_time"]["max"], test_benchmark["abs_recover_time"]["max"], ])
    p.daemon = True
    p.start()

    # run fio command on cell phone background
    cmd = "shell '/data/auto_tools/fio --direct=1 --norandommap=0 --numjobs=1 --ioengine=libaio " \
          + "--iodepth=32 --rw=write --size={}  --bs=512k --runtime=600" \
          + " --name=job1 --filename=/data/auto_tools/fio_test_file'"
    cmd = cmd.format(test_data["fio_file_size"])
    fio_start_ts = time.time()
    tc_logger.info("FIO cmd execution start timestamp: " + str(fio_start_ts))
    adb.execute_adb_command(cmd)
    fio_end_ts = time.time()
    tc_logger.info("FIO cmd execution end timestamp: " + str(fio_end_ts))
    result = assert_values_meet_benchmark([fio_end_ts - fio_start_ts],
                                          test_benchmark["fio_sw_time"], False, "dc.yaml", ["fio_sw_time"]) | result

    # wait for abs monitoring to completed
    p.join(test_benchmark["fio_sw_time"]["max"] + test_benchmark["abs_recover_time"]["max"])
    p.terminate()

    # verify whether abs is used up during fio execution
    monitor_log_file = os.path.join(test_conf["monitor_home"], "wb_func_abs_monitor.log")
    abs_use_up_ts_pattern = re.compile("abs_use_up_ts=(.+)")
    with open(monitor_log_file, "r") as f:
        for line in f.readlines():
            abs_use_up_ts = abs_use_up_ts_pattern.search(line)
            if abs_use_up_ts is not None:
                break
            else:
                abs_min = line
    abs_min = abs_min.split("%")[0]
    result = assert_values_meet_benchmark([int(abs_min)],
                                          test_benchmark["abs_min"], False, "dc.yaml", ["abs_min"]) | result

    # verify whether abs can fully recover
    abs_recover_ts_pattern = re.compile("abs_recover_ts=(.+)")
    with open(monitor_log_file, "r") as f:
        for line in f.readlines():
            abs_recover_ts = abs_recover_ts_pattern.search(line)
            if abs_recover_ts is not None:
                abs_recover_ts = abs_recover_ts.group(1)
                break
            else:
                abs_max = line
    abs_max = abs_max.split("%")[0]
    result = assert_values_meet_benchmark([int(abs_max)],
                                          test_benchmark["abs_max"], False, "dc.yaml", ["abs_max"]) | result

    # verify abs recover time consumption
    if abs_recover_ts == "timeout":
        abs_recover_time = -1
    else:
        abs_recover_time = float(abs_recover_ts) - fio_end_ts
    result = assert_values_meet_benchmark([abs_recover_time],
                                          test_benchmark["abs_recover_time"], False, "dc.yaml",
                                          ["abs_recover_time"]) | result

    # verify flush_status_after_recover_1
    flush_status_after_recover = device.get_wb_flush_status()
    result = assert_values_meet_benchmark([flush_status_after_recover],
                                          test_benchmark["flush_status_after_recover_1"], False, "dc.yaml",
                                          ["flush_status_after_recover_1"]) | result

    # flush_status_after_recover_2
    flush_status_after_recover = device.get_wb_flush_status()
    result = assert_values_meet_benchmark([flush_status_after_recover],
                                          test_benchmark["flush_status_after_recover_2"], False, "dc.yaml",
                                          ["flush_status_after_recover_2"]) | result

    # return test case result
    return result


