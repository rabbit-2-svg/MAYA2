import os
from testcase.tc_androbench import tc_run_micro_by_loops
from testcase.tc_fio import tc_run_fio_by_loops
from testcase.tc_iozone import tc_run_iozone_by_loops
from common.hook import set_up, tear_down
from common.rwfile import get_benchmark_item, get_column_from_csv, assert_values_meet_benchmark
from conf.test_conf import test_conf, tc_logger
from common.deco import pass_fail_common_deco


ud_pre_case_string = ["scan_device", "get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "open_tw",
                      "restore_wb_cur_buf", "restore_wb_avail_buf", "enable_mtp"]
ud_post_case_string = ["get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "restore_wb_cur_buf",
                       "restore_wb_avail_buf"]
ud_pre_loop_string = ["get_wb_cur_buf", "get_wb_avail_buf"]
ud_post_loop_string = ["clean_fio_file", "fstrim", "restore_wb_cur_buf", "restore_wb_avail_buf"]

def _get_basic_perf_bm_filename():
  return os.path.join(test_conf["chip_prod"], test_conf["chip_capacity"], test_conf["device_type"], "basic_performance.yaml")

@pass_fail_common_deco()
def tc2_AB_default_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  # tc_run_micro_by_loops(loops=3)
  func = tc_run_micro_by_loops.__wrapped__
  func(loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["AB", "default"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "androbench_result.csv")
  result = 0
  # SR verification
  checkpoints_prefix = "Sequential Read(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result
  # SW verification
  checkpoints_prefix = "Sequential Write(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  # RR verification
  checkpoints_prefix = "Random Read(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  # RW verification
  checkpoints_prefix = "Random Write(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result
  
  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_SeqRead_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="read", block_size="512k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Read verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Sequential Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Sequential Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_SeqWrite_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="write", block_size="512k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Write verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Sequential Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Sequential Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_RandRead_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randread", block_size="4k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Read verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_RandWrite_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randwrite", block_size="4k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Write verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_RandRW37_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randrw", rwmixread="30", block_size="4k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic_randrw37"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Read verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  # Write verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_RandRW55_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randrw", rwmixread="50", block_size="4k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic_randrw55"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Read verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  # Read verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_FIO_basic_RandRW73_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randrw", rwmixread="70", block_size="4k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "basic_randrw73"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Read verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  # Read verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_IOZone_basic_Seq_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_iozone_by_loops.__wrapped__
  func(threads=8, file_size="128m", block_size="512k", sequential=True, loops=3)
  
  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["IOZone", "basic"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "iozone_result.csv")
  result = 0
  # Initial Write verification
  checkpoints_prefix = "Initial Writers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  # Rewrite verification
  checkpoints_prefix = "Rewriters(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  # Read verification
  checkpoints_prefix = "Readers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result
  # Reread verification
  checkpoints_prefix = "Re-readers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

@pass_fail_common_deco()
def tc2_IOZone_basic_Rand_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_iozone_by_loops.__wrapped__
  func(threads=8, file_size="128m", block_size="4k", sequential=False, loops=3)
  
  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["IOZone", "basic"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "iozone_result.csv")
  result = 0
  # Random Read verification
  checkpoints_prefix = "Random readers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  # Random Reread verification
  checkpoints_prefix = "Random writers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result

  # return result
  return result

