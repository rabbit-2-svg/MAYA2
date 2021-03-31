import os
from conf.test_conf import test_conf, tc_logger
import csv, json, yaml
import pandas as pd
import numpy as np
from pandas import Series, DataFrame


def get_screenshot_name(withPath=True):
    if (withPath == True):
        name = test_conf["screenshot_home"] + "/screenshot_" + str(test_conf["screenshot"]).zfill(2) + ".png"
    else:
        name = "screenshot_" + str(test_conf["screenshot"]).zfill(2) + ".png"
    test_conf["screenshot"] = test_conf["screenshot"] + 1
    return name


def get_index(index_width=None):
    index = test_conf["index"]
    test_conf["index"] = test_conf["index"] + 1
    if (index_width is not None):
        index_width = int(index_width)
        index = str(index).zfill(index_width)
    return index


def write_csv_header(file, header):
    if (isinstance(header, list)):
        header = [str(elem) for elem in header]
        header = test_conf["csv_delimiter"].join(header)
    if (not os.path.exists(file)):
        tc_logger.info("Creating file {}".format(file))
        os.system("touch {}".format(file))
        tc_logger.info("Writting csv header: {}".format(header))
        os.system("echo \"{}\" >> {}".format(header, file))
    else:
        tc_logger.info("File already exists: {}".format(file))
        tc_logger.info("Skip writting csv header")


def write_csv_result(file, string, new_line=True):
    if (isinstance(string, list)):
        string = [str(elem) for elem in string]
        string = test_conf["csv_delimiter"].join(string)
    if (not os.path.exists(file)):
        raise Exception("csv file doesn't exists: {}".format(file))
    tc_logger.info("Writting: {}".format(string))
    if (new_line == True):
        os.system("echo \"{}\" >> {}".format(string, file))
    else:
        os.system("echo -n \"{}\" >> {}".format(string, file))


def read_csv_to_json(file):
    if (not os.path.exists(file)):
        raise Exception("csv file doesn't exists: {}".format(file))
    tc_logger.info("Parsing {} to json".format(file))
    data = {}
    with open(file, mode='r') as f:
        header = f.readline()
        header = header.split(test_conf["csv_delimiter"])
        rows = f.readlines()
        i = 0
        for row in rows:
            temp = {}
            value = row.split(test_conf["csv_delimiter"])
            for k in range(0, len(value)):
                temp[header[k].strip()] = value[k].strip()
            data[str(i)] = temp
            i = i + 1
    return data


def read_csv_to_lls(file):
    if (not os.path.exists(file)):
        raise Exception("csv file doesn't exists: {}".format(file))
    tc_logger.info("Parsing {} to list of list of string".format(file))
    data = []
    with open(file, mode='r') as f:
        rows = f.readlines()
        for row in rows:
            data.append(row.split(test_conf["csv_delimiter"]))
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            data[i][j] = data[i][j].strip()
    return data


def convert_csv_file_to_json_file(source, target=None):
    if (target is None):
        if (source.endswith(".csv")):
            target = source[0: len(source) - 4] + ".json"
        else:
            target = source + ".json"

    data = read_csv_to_json(source)
    tc_logger.info("Dumping json to {}".format(target))
    dump_append_dict_to_json_file(data, target)


def convert_csv_files_to_json_file(source_files, target=None):
    if (target is None):
        target = test_conf["mongo_json"]

    data = {}
    for file in source_files:
        tag = file[0]
        file_name = file[1]
        data[tag] = read_csv_to_json(file_name)
    dump_append_dict_to_json_file(data, target)


def dump_append_dict_to_json_file(dictionary, json_file):
    if (os.path.isfile(json_file)):
        with open(json_file, "r") as f:
            data = json.load(f)
        data.update(dictionary)
        with open(json_file, "w") as f:
            json.dump(data, f)
    else:
        with open(json_file, "w") as f:
            json.dump(dictionary, f)

def get_benchmark(benchmark_file=None):
    if (benchmark_file is None):
        if ("benchmark_file" in test_conf):
            benchmark_file = test_conf["benchmark_file"]
        else:
            benchmark_file = test_conf["device_type"] + "_" + test_conf["chip_prod"] + "_" + test_conf["chip_capacity"] + ".yaml"
    if (not benchmark_file.startswith("/")):
        benchmark_file = os.path.join(test_conf["project_home"], "benchmark", benchmark_file)

    with open(benchmark_file, "r") as f:
        benchmark = yaml.safe_load(f)
    return benchmark

def get_benchmark_item(benchmark_file=None, item=None):
    benchmark = get_benchmark(benchmark_file)
    if (item is None or len(item) == 0):
        return benchmark
    for i in item:
        benchmark = benchmark[i]
    return benchmark

def assert_value_meet_benchmark(value, benchmark, raise_exception=True, dc_filename=None, checkpoint=None, enable_drilldown=False):
    if ((dc_filename is not None) and (not dc_filename.startswith("/"))):
        dc_filename = os.path.join(test_conf["result_home"], dc_filename)
    tc_logger.info("Value: " + str(value))
    tc_logger.info("Benchmark: " + str(benchmark))
    if (enable_drilldown == True):
        prefix = "    "
        tc_logger.info("DrillDown is enabled")
    else:
        prefix = "  "
        tc_logger.info("DrillDown is disabled")
    if (dc_filename is not None):
        tc_logger.info("dc_filename is " + dc_filename)
        if (not os.path.isfile(dc_filename)):
            with open(dc_filename, "w") as f:
                f.write("checkpoints:" + os.linesep)
        with open(dc_filename, "a") as f:
            f.write(prefix + "- name: " + checkpoint + os.linesep)
            f.write(prefix + "  value: " + str(value) + os.linesep)
            f.write(prefix + "  baseline: " + os.linesep)
            f.write(prefix + "    min: " + str(benchmark["min"]) + os.linesep)
            f.write(prefix + "    max: " + str(benchmark["max"]) + os.linesep)
            if ("comments" in benchmark):
                f.write(prefix + "    comments: " + os.linesep)
                comments = benchmark["comments"]
                for comment in comments:
                    f.write(prefix + "    - " + comment + os.linesep)
    if (value >= benchmark["min"]):
        tc_logger.info("Value is greater than benchmark minimum - PASS")
    else:
        tc_logger.info("Value is less than benchmark minimum - FAIL")
        if (dc_filename is not None):
            with open(dc_filename, "a") as f:
                f.write(prefix + "  result: FAIL" + os.linesep)
        if (raise_exception != False):
            raise Exception("Value {} is less than benchmark minimum {}".format(str(value), str(benchmark["min"])))
        else:
            return 1
    if (value <= benchmark["max"]):
        tc_logger.info("Value is less than benchmark maximum - PASS")
    else:
        tc_logger.info("Value is geater than benchmark maximum - FAIL")
        if (dc_filename is not None):
            with open(dc_filename, "a") as f:
                f.write(prefix + "  result: FAIL" + os.linesep)
        if (raise_exception != False):
            raise Exception("Value {} is geater than benchmark maximum {}".format(str(value), str(benchmark["max"])))
        else:
            return 1
    if (dc_filename is not None):
        with open(dc_filename, "a") as f:
            f.write(prefix + "  result: PASS" + os.linesep)
    return 0

def assert_values_meet_benchmark(values, benchmark, raise_exception=True, dc_filename=None, checkpoints=None, enable_drilldown=False):
    if ((dc_filename is not None) and (not dc_filename.startswith("/"))):
        dc_filename = os.path.join(test_conf["result_home"], dc_filename)
    result = 0
    result = assert_value_meet_benchmark(values[0], benchmark, raise_exception, dc_filename, checkpoints[0]) | result
    if (dc_filename is not None and enable_drilldown == True):
        with open(dc_filename, "a") as f:
            f.write("    drill_down:" + os.linesep)
    for i in range(1, len(values)):
        result = assert_value_meet_benchmark(values[i], benchmark, raise_exception, dc_filename, checkpoints[i], enable_drilldown) | result
    return result

def get_column_from_csv(csv_file, column_name):
    data = pd.read_csv(csv_file)
    data = data[column_name]
    return list(data)

if __name__ == "__main__":
    # print (read_csv_to_json("/home/ssd/git_project/android-test-program/result/Mi10/RootAB/Mi10rootAB.csv"))

    # csv_files = [["result", "/home/ssd/git_project/android-test-program/result/ts_debug/tc_debug/androbench_result.csv"], ["monitor", "/home/ssd/git_project/android-test-program/result/ts_debug/tc_debug/monitor/monitor.csv"]]
    #  convert_csv_files_to_json_file(csv_files)

    # test = {"B": {"C1": "1", "C2": "ASS"}}
    # dump_append_dict_to_json_file(test, "/home/ssd/git_project/android-test-program/test.json")
    # print(get_index(2))
    # print(get_index(3))
    # print(get_index(4))
    # benchmark_file = "/Automation/android-test-program/benchmark/Mi10_TAS_256G.yaml"
    # print (get_benchmark_item(benchmark_file, item=["AB", "default"]))
    # assert_values_meet_benchmark(["1234", "1000", 999, 10], {"min": 900, "max": 1500})
    values = get_column_from_csv("/Automation/android-test-program/result/Hikey970_Perf/debug_1/androbench_result.csv", "Sequential Read(MB/s)")
    print (values)
    test_conf["benchmark_file"] = "Mi10_TAS_256G.yaml"
    benchmark = (get_benchmark_item(item=["AB", "default", "SR"]))
    print (benchmark)
    print (assert_values_meet_benchmark(values, benchmark, False))
