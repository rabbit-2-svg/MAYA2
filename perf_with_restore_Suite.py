import os
from testcase.tc_fio import tc_run_fio_by_loops
from testcase.tc_iozone import tc_run_iozone_by_loops
from common.hook import set_up, tear_down
from common.rwfile import get_benchmark_item, get_column_from_csv, assert_values_meet_benchmark
from conf.test_conf import test_conf, tc_logger
from common.deco import pass_fail_common_deco


ud_pre_case_string = ["scan_device", "get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "open_tw", "restore_wb_cur_buf", "restore_wb_avail_buf"]
ud_post_case_string = ["get_smart_info","get_health_report","clean_fio_file","fstrim","restore_wb_cur_buf","restore_wb_avail_buf","sleep:120"]
ud_pre_loop_string = ["get_wb_cur_buf","get_wb_avail_buf"]
ud_post_loop_string = ["wb_avail_buf_restore_loop_check"]

def _get_basic_perf_bm_filename():
  # return os.path.join(test_conf["chip_prod"], test_conf["chip_capacity"], test_conf["device_type"], "performance_with_restore.yaml")
  return os.path.join(test_conf["chip_prod"], test_conf["chip_capacity"], test_conf["device_type"], "performance_with_restore.yaml")

#fio 4g_restore
# FIO SR
@pass_fail_common_deco()
def FIO_4G_Restore_enough_SR_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")
  
  
  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, sub_jobs=4, rw="read", rewrite="false", block_size="512k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "FIO_4G_Restore_enough"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # SeqRead verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Sequential Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Sequential Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO SW
@pass_fail_common_deco()
def FIO_4G_Restore_enough_SW_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, sub_jobs=4, rw="write", rewrite="false", block_size="512k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "FIO_4G_Restore_enough"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # SeqWrite verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Sequential Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Sequential Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO RandRead
@pass_fail_common_deco()
def FIO_4G_Restore_enough_RR_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, sub_jobs=4, rw="randread", rewrite="false", block_size="4k", file_size="1g", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "FIO_4G_Restore_enough"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Random read verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Read(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO RangWrite
@pass_fail_common_deco()
def FIO_4G_Restore_enough_RW_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, sub_jobs=8, rw="randwrite", rewrite="false", block_size="4k", file_size="512m", runtime=600, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["FIO", "FIO_4G_Restore_enough"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  # Random Write verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[-1:] + values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, "Random Write(MB/s)" + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result
  return result

# IOzone_Seq_4G
@pass_fail_common_deco()
def IOzone_Seq_4G_Restore_enough_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")
  
  ud_pre_loop_string.extend(["file_for_assistant_test:rw=write@bs=512k@size=4g@runtime=600@fio_fg=True","wb_avail_buf_restore_loop_check"])
  ud_post_loop_string.remove("wb_avail_buf_restore_loop_check")
  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # main function
  set_up(level='case')
  func = tc_run_iozone_by_loops.__wrapped__
  func(threads=4, file_size="1024m", block_size="512k", sequential=True, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["IOZone", "IOzone_Seq_4G_Restore_enough"])
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
  result = assert_values_meet_benchmark(values, benchmark_item["SW_Initial"], False, "dc.yaml", checkpoints, True) | result
  # Rewrite verification
  checkpoints_prefix = "Rewriters(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SW_Rewriters"], False, "dc.yaml", checkpoints, True) | result
  # Read verification
  checkpoints_prefix = "Readers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR_Readers"], False, "dc.yaml", checkpoints, True) | result
  # Reread verification
  checkpoints_prefix = "Re-readers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["SR_Re-readers"], False, "dc.yaml", checkpoints, True) | result
  return result
   
# IOzone_Random_4G
@pass_fail_common_deco()
def IOzone_Rand_4G_Restore_enough_3times():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")
  
  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # main function
  set_up(level='case')
  func = tc_run_iozone_by_loops.__wrapped__
  func(threads=32, file_size="128m", block_size="4k", sequential=False, loops=3)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_basic_perf_bm_filename(), ["IOZone", "IOzone_Rand_4G_Restore_enough"])
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
  result = assert_values_meet_benchmark(values, benchmark_item["RR_bandwidth"], False, "dc.yaml", checkpoints, True) | result
  # random read iops verification
  checkpoints_prefix = "Random readers(IOPS)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RR_iops"], False, "dc.yaml", checkpoints, True) | result
  # Random Reread verification
  checkpoints_prefix = "Random writers(MB/s)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW_bandwidth"], False, "dc.yaml", checkpoints, True) | result
  # random reread iops verification
  checkpoints_prefix = "Random writers(IOPS)"
  values = get_column_from_csv(result_file, checkpoints_prefix)
  values = values[-1:] + values[:-1]
  checkpoints = [checkpoints_prefix + " - " + str(i) for i in range(1, len(values))]
  checkpoints.insert(0, checkpoints_prefix + " - avg")
  result = assert_values_meet_benchmark(values, benchmark_item["RW_iops"], False, "dc.yaml", checkpoints, True) | result
  return result
