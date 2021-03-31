import os
from common.hook import set_up, tear_down
from conf.test_conf import test_conf, tc_logger
from common.deco import pass_fail_common_deco
from testcase.tc_androbench import tc_run_micro_by_duration
from testcase.tc_fio import tc_run_fio_by_duration
from testcase.tc_iozone import tc_run_iozone_by_duration
from common.rwfile import get_benchmark_item, get_column_from_csv, assert_values_meet_benchmark


ud_pre_case_string = ["scan_device", "get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "open_tw",
                      "restore_wb_cur_buf", "restore_wb_avail_buf", "enable_mtp"]
ud_post_case_string = ["get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "restore_wb_cur_buf",
                       "restore_wb_avail_buf"]
ud_pre_loop_string = ["get_wb_cur_buf", "get_wb_avail_buf"]
ud_post_loop_string = ["clean_fio_file", "fstrim"]


def stress_statistics_validation(statistics_file, statistics_column,
                                 benchmark_file, benchmark_group, checkpoint_prefix):
    statistics_results = get_column_from_csv(statistics_file, statistics_column)
    statistics_results.pop(2)
    statistics_results.pop(0)
    benchmark_group_content = get_benchmark_item(benchmark_file, benchmark_group)
    statistics_index = ["mean", "min", "percent_1", "percent_10", "percent_25", "percent_50", "percent_75",
                        "percent_90", "percent_99", "max"]
    checkpoints = [checkpoint_prefix + " - " + x for x in statistics_index]
    validation_result = 0
    for i in range(0, len(statistics_index)):
        result = [statistics_results[i]]
        benchmark_item = benchmark_group_content[statistics_index[i]]
        checkpoint = [checkpoints[i]]
        validation_result = assert_values_meet_benchmark(result, benchmark_item,
                                                         False, "dc.yaml", checkpoint) | validation_result
    return validation_result


def _get_basic_stress_bm_filename():
    return os.path.join(test_conf["chip_prod"], test_conf["chip_capacity"],
                        test_conf["device_type"], "basic_stress.yaml")


@pass_fail_common_deco()
def tc2_ab_default_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_micro_by_duration
    func(duration=duration)

    result = 0
    # result validation - Sequential Read
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Sequential Read(MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["AB", "default", "SR"]
    checkpoint_prefix = "Sequential Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Sequential Write
    statistics_column = "Sequential Write(MB/s)"
    benchmark_group = ["AB", "default", "SW"]
    checkpoint_prefix = "Sequential Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Random Read
    statistics_column = "Random Read(MB/s)"
    benchmark_group = ["AB", "default", "RR"]
    checkpoint_prefix = "Random Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Random Write
    statistics_column = "Random Write(MB/s)"
    benchmark_group = ["AB", "default", "RW"]
    checkpoint_prefix = "Random Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_sr_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='512k', duration=duration, file_size='10g', runtime='600', iodepth='32', rw='read')

    result = 0
    # result validation
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Read (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic", "SR"]
    checkpoint_prefix = "Sequential Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_sw_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='512k', duration=duration, file_size='10g', runtime='600', iodepth='32', rw='write')

    result = 0
    # result validation
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Write (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic", "SW"]
    checkpoint_prefix = "Sequential Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_rr_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='4k', duration=duration, file_size='10g', iodepth='32', runtime='600', rw='randread')

    result = 0
    # result validation
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Read (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic", "RR"]
    checkpoint_prefix = "Random Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_rw_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='4k', duration=duration, file_size='10g', iodepth='32', runtime='600', rw='randwrite')

    result = 0
    # result validation
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Write (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic", "RW"]
    checkpoint_prefix = "Random Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_mixrw_30_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='4k', duration=duration, file_size='10g', iodepth='32', runtime='600', rw='randrw', rwmixread='30')

    result = 0
    # result validation - Random Read
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Read (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic_randrw37", "RR"]
    checkpoint_prefix = "Random Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Random Write
    statistics_column = "Write (MB/s)"
    benchmark_group = ["FIO", "basic_randrw37", "RW"]
    checkpoint_prefix = "Random Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_mixrw_50_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='4k', duration=duration, file_size='10g', iodepth='32', runtime='600', rw='randrw', rwmixread='50')

    result = 0
    # result validation - Random Read
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Read (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic_randrw55", "RR"]
    checkpoint_prefix = "Random Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Random Write
    statistics_column = "Write (MB/s)"
    benchmark_group = ["FIO", "basic_randrw55", "RW"]
    checkpoint_prefix = "Random Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_fio_mixrw_70_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_fio_by_duration
    func(block_size='4k', duration=duration, file_size='10g', iodepth='32', runtime='600', rw='randrw', rwmixread='70')

    result = 0
    # result validation - Random Read
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Read (MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["FIO", "basic_randrw55", "RR"]
    checkpoint_prefix = "Random Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Random Write
    statistics_column = "Write (MB/s)"
    benchmark_group = ["FIO", "basic_randrw73", "RW"]
    checkpoint_prefix = "Random Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_iozone_sequential_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_iozone_by_duration
    func(block_size='512k', duration=duration, file_size='128m', sequential='True', threads='8')

    result = 0
    # result validation - Initial Writer
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Initial Writers(MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["IOZone", "basic", "SW"]
    checkpoint_prefix = "Initial Writers"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Initial Writer
    statistics_column = "Rewriters(MB/s)"
    benchmark_group = ["IOZone", "basic", "SW"]
    checkpoint_prefix = "Rewriters"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Reader
    statistics_column = "Readers(MB/s)"
    benchmark_group = ["IOZone", "basic", "SR"]
    checkpoint_prefix = "Readers"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Re-Reader
    statistics_column = "Re-readers(MB/s)"
    benchmark_group = ["IOZone", "basic", "SR"]
    checkpoint_prefix = "Readers"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result


@pass_fail_common_deco()
def tc2_iozone_random_sr_stress():
    # pre_case, post_case, pre_loop and post_loop definition
    tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

    test_conf["ud_pre_case"] = ud_pre_case_string
    test_conf["ud_post_case"] = ud_post_case_string
    test_conf["ud_pre_loop"] = ud_pre_loop_string
    test_conf["ud_post_loop"] = ud_post_loop_string

    # duration configuration
    if "duration" in test_conf:
        duration = test_conf["duration"]
    else:
        duration = 300

    # main function
    set_up(level='case')
    func = tc_run_iozone_by_duration
    func(block_size='512k', duration=duration, file_size='128m', sequential='False', threads='8')

    result = 0
    # result validation - Random Read
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Random readers(MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["IOZone", "basic", "RR"]
    checkpoint_prefix = "Random Read"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    # result validation - Random Write
    statistic_file = os.path.join(test_conf["result_home"], "statistics.csv")
    statistics_column = "Random writers(MB/s)"
    benchmark_file = _get_basic_stress_bm_filename()
    benchmark_group = ["IOZone", "basic", "RW"]
    checkpoint_prefix = "Random Write"
    result = stress_statistics_validation(statistic_file, statistics_column, benchmark_file,
                                          benchmark_group, checkpoint_prefix) | result

    return result
