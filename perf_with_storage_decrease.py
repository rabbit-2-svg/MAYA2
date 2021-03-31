import os
from testcase.tc_storage_space_increasement import tc_run_fio_by_loops
from common.hook import set_up, tear_down
from common.rwfile import get_benchmark_item, get_column_from_csv, assert_values_meet_benchmark
from conf.test_conf import test_conf, tc_logger
from common.deco import pass_fail_common_deco
from common.device import Device

device = Device(test_conf['device_id'])
ud_pre_case_string = ["scan_device", "get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "open_tw", "restore_wb_avail_buf"]
ud_post_case_string = ["space_decrease_chart", "get_smart_info", "get_health_report", "clean_fio_file", "fstrim", "sleep:3600"]
ud_pre_loop_string = ["get_data_space_and_cur_buf"]
ud_post_loop_string = []
_sub_jobs = 1
_file_size = ["2g", "4g", "8g"]

def _get_perf_bm_filename():
  return os.path.join(test_conf["chip_prod"], test_conf["chip_capacity"], test_conf["device_type"], "performance_with_storage_decrease.yaml")

# FIO 2G RR
@pass_fail_common_deco()
def FIO_2G_RR_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # duration configuration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[0]
  _loops = int(device.auto_calculate_loops()[1][0])

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randread", block_size="4k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_2G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # Randread verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO 2G RW
@pass_fail_common_deco()
def FIO_2G_RW_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[0]
  _loops = int(device.auto_calculate_loops()[1][0])

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randread", block_size="4k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_2G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # Randwrite verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result
  return result
  
# FIO 4G SR
@pass_fail_common_deco()
def FIO_4G_SR_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[1]
  _loops = int(device.auto_calculate_loops()[1][0])

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="read", block_size="512k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_4G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # SeqRead verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[:-1]
  checkpoints = ["Sequential Read(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO 4G SW
@pass_fail_common_deco()
def FIO_4G_SW_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[1]
  _loops = int(device.auto_calculate_loops()[1][0])
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="write", block_size="512k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_4G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # SeqWrite verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[:-1]
  checkpoints = ["Sequential Write(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  return result


# FIO 4G RR
@pass_fail_common_deco()
def FIO_4G_RR_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[1]
  _loops = int(device.auto_calculate_loops()[1][0])

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randread", block_size="4k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_4G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0

  # RandRead verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[:-1]
  checkpoints = ["Random Read(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO 4G RW
@pass_fail_common_deco()
def FIO_4G_RW_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[1]
  _loops = int(device.auto_calculate_loops()[1][0])

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randwrite", block_size="4k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_4G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0

  # RandWrite verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[:-1]
  checkpoints = ["Random Write(MB/s)" + " - " + str(i + 1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result
  return result


# FIO 4G seqmix55
@pass_fail_common_deco()
def FIO_4G_Seqmix55_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")
  
  
  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[1]
  _loops = int(device.auto_calculate_loops()[1][0])

  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="rw", rwmixread=50, block_size="512k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_4G_MIX_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # Seqmix verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[:-1]
  checkpoints = ["SeqMix Read(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[:-1]
  checkpoints = ["SeqMix Write(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  return result

# FIO 4G randmix55
@pass_fail_common_deco()
def FIO_4G_Randmix55_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[1]
  _loops = int(device.auto_calculate_loops()[1][0])
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="randrw", rwmixread=50, block_size="4k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_4G_MIX_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # Randmix verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[:-1]
  checkpoints = ["Randmix Read(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["RR"], False, "dc.yaml", checkpoints, True) | result
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[:-1]
  checkpoints = ["Randmix Write(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["RW"], False, "dc.yaml", checkpoints, True) | result
  return result


# FIO 8G SR
@pass_fail_common_deco()
def FIO_8G_SR_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")
  
  
  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[2]
  _loops = int(device.auto_calculate_loops()[1][0])
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="read", block_size="512k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_8G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # SeqRead verification
  values = get_column_from_csv(result_file, "Read (MB/s)")
  values = values[:-1]
  checkpoints = ["Sequential Read(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["SR"], False, "dc.yaml", checkpoints, True) | result
  return result


# FIO 8G SW
@pass_fail_common_deco()
def FIO_8G_SW_Storage_Down_Perf():
  # pre_case, post_case, pre_loop and post_loop definition
  tc_logger.info("Defining pre_case, post_case, pre_loop and post_loop inside of test case")

  test_conf["ud_pre_case"] = ud_pre_case_string
  test_conf["ud_post_case"] = ud_post_case_string
  test_conf["ud_pre_loop"] = ud_pre_loop_string
  test_conf["ud_post_loop"] = ud_post_loop_string

  # loops configration
  test_conf["sub_jobs"] = _sub_jobs
  test_conf["file_size"] = _file_size[2]
  _loops = int(device.auto_calculate_loops()[1][0])
  
  # main function
  set_up(level='case')
  func = tc_run_fio_by_loops.__wrapped__
  func(iodepth=32, rw="write", block_size="512k", runtime=600, rewrite="false", loops=_loops)

  # performance result verification
  benchmark_item = get_benchmark_item(_get_perf_bm_filename(), ["FIO", "FIO_8G_Storage_Down_Perf"])
  tc_logger.info("Benchmark is as below")
  tc_logger.info(str(benchmark_item))
  result_file = os.path.join(test_conf["result_home"], "fio_rpt.csv")
  result = 0
  
  # SeqWrite verification
  values = get_column_from_csv(result_file, "Write (MB/s)")
  values = values[:-1]
  checkpoints = ["Sequential Write(MB/s)" + " - " + str(i+1) for i in range(len(values))]
  result = assert_values_meet_benchmark(values, benchmark_item["SW"], False, "dc.yaml", checkpoints, True) | result
  return result
