"""
Author: William Zhou
Email: william_zhou@ymtc.com
"""
import os
import sys
import time
import logging
import yaml
from time import sleep
from common.device import Device
from multiprocessing import Pool
from importlib import import_module
from common.hook import set_up, tear_down
from common.assistant import complete_config_path
from conf.test_conf import test_conf, tc_logger, ch, result_shop
from common.rwfile import convert_csv_files_to_json_file, read_csv_to_lls


def run(**kwargs):
    process_param(**kwargs)

    def main():
        initiate_device()
        initiate_file()
        keep_monitor()

        # config tc_logger to print in log.txt
        main_log = os.path.join(test_conf['log_home'], 'log.txt')
        fh = logging.FileHandler(main_log)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        tc_logger.addHandler(fh)

        # import module and function
        set_up(level='case')
        module = import_module(test_conf['module'])
        func = getattr(module, test_conf['func'])
        try:
            func()
        except Exception as e:
            raise e
        finally:
            if test_conf['monitor'] is True:
                csv_files = [['monitor', test_conf['monitor_dir'] + '/monitor.csv']]
                convert_csv_files_to_json_file(csv_files)
            tear_down(level='case')
            if (test_conf.get("ddtf", None) is not None):
                tc_logger.removeHandler(fh)
    
    if (test_conf.get("ddtf", None) is None): 
        main()
    else:
        print ("This is DDT workflow")
        ddtf = test_conf["ddtf"]
        if (ddtf.startswith("/")):
          ddtf = ddtf
        else:
          ddtf = os.path.join(test_conf["project_home"], "ddtf", ddtf)
        print ("DDT file: " + ddtf)
        ddtd = read_csv_to_lls(ddtf)
        # temp_conf = copy.deepcopy(test_conf)
        for i in range(1, len(ddtd)):
            # test_conf = copy.deepcopy(temp_conf)
            print ("Processing DDT Line " + str(i))
            for j in range(0, len(ddtd[i])):
                value = ddtd[i][j].replace(";", ",")
                if ("," in value):
                    value = value.lower().replace(' ', '').split(',')    
                print (ddtd[0][j] + "=" + str(value))
                test_conf[ddtd[0][j]] = value
            main()


def process_param(**kwargs):
    """
    Process parameters both from command line and IDE
    :param kwargs: key value pair
    :return: None
    """
    tc_logger.info('==>Start to process parameters')
    global test_conf
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            kv = arg.strip().split('=', 1)
            key = kv[0]
            value = kv[1]
            if ',' in value:
                value = value.lower().replace(' ', '').split(',')
            test_conf[key] = value
    else:
        for k, v in kwargs.items():
            if ',' in str(v):
                v = v.lower().replace(' ', '').split(',')
            test_conf[k] = v
    # make switch input standard
    switch = ['statistics', 'chart', 'monitor', 'watchdog', 'event_trace', 'loop_health_report']
    for key in switch:
        if not isinstance(test_conf[key], bool):
            test_conf[key] = test_conf[key].lower() in ('1', 'true', 'yes', 't')

    if ("user_test_conf" in test_conf):
        tc_logger.info('==>Start to process user test conf yaml')
        with open(test_conf["user_test_conf"], 'r') as file:
            temp_conf = yaml.safe_load(file)
        for k, v in temp_conf.items():
            test_conf[k] = v
        tc_logger.info('==>Process user test conf yaml over')
    k1 = "default_suite_id"
    k2 = "default_test_id"
    v1 = test_conf[k1]
    v2 = test_conf[k2]
    for k, v in test_conf.items():
        if (type(v) == str):
            test_conf[k] = v.replace("@"+k1, v1).replace("@"+k2, v2)

    complete_config_path(test_conf['support_device'] + test_conf['support_tool'], test_conf)
    device = Device(test_conf['device_id'])
    device.root_device()
    if test_conf.get('device_type', None) is None:
        test_conf['device_type'] = device.get_host_manufacturer()[1][0]
    if test_conf.get('chip_manufacturer', None) is None:
        test_conf['chip_manufacturer'] = device.get_chip_manufacturer()[1][0]
    if test_conf.get('chip_capacity', None) is None:
        test_conf['chip_capacity'] = device.get_chip_capacity()[1][0]
    tc_logger.info('==>Process parameters over, valid parameters:')
    tc_logger.info(test_conf)


def initiate_device():
    """
    Initiate device, like set screen, enable mtp

    :return: None
    """
    tc_logger.info('==>Start to initiate devices')
    device = Device(test_conf['device_id'])
    device.root_device()
    device.verify_hdmi_connection()
    device.set_screen()
    device.switch_mtp(True)


def initiate_file():
    """
    Create dirs and files for test
    :return: None
    """

    tc_logger.info('==>Start to initiate dirs and files')
    if 'job_id' in test_conf:
        test_conf['job_home'] = os.path.join(result_shop, test_conf['job_id'])
    else:
        test_conf['job_home'] = result_shop
    if 'suite_id' in test_conf:
        test_conf['suite_home'] = os.path.join(test_conf['job_home'], test_conf['suite_id'])
    if 'test_id' in test_conf:
        test_conf['result_home'] = os.path.join(test_conf['suite_home'], test_conf['test_id'])
        test_conf['log_home'] = os.path.join(test_conf['result_home'], 'log')
        test_conf['chart_home'] = os.path.join(test_conf['result_home'], 'chart')
        test_conf['monitor_home'] = os.path.join(test_conf['result_home'], 'monitor')
        test_conf['screenshot_home'] = os.path.join(test_conf['result_home'], 'screenshot')
        test_conf['graceful_stop_point'] = os.path.join(test_conf['result_home'], 'pause')
        test_conf['mongo_json'] = os.path.join(test_conf['result_home'], 'mongo.json')
        test_conf["pass_indicator"] = os.path.join(test_conf['result_home'], 'PASS')
        test_conf["fail_indicator"] = os.path.join(test_conf['result_home'], 'FAIL')
        test_conf["exception_indicator"] = os.path.join(test_conf['result_home'], 'EXCEPTION')

    os.system('mkdir -p {}'.format(test_conf['result_home']))
    os.system('mkdir -p {}'.format(test_conf['log_home']))
    os.system('mkdir -p {}'.format(test_conf['chart_home']))
    os.system('mkdir -p {}'.format(test_conf['monitor_home']))
    os.system('mkdir -p {}'.format(test_conf['screenshot_home']))
    tc_logger.info('==>Initiate dirs and files over')


def keep_monitor():
    """
    Keep monitoring the test
    :return: None
    """
    if test_conf['monitor'] is True:
        tc_logger.info('==>Start monitoring execution')
        # config monitoring log
        tc_logger.removeHandler(ch)
        lh = logging.FileHandler(test_conf['monitor_dir'] + '/log.txt')
        lh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        lh.setFormatter(formatter)
        tc_logger.addHandler(lh)

        # start monitoring
        pool = Pool(1)
        m_module = import_module('android.monitor')
        m_func = getattr(m_module, 'monitor')
        pool.apply_async(func=m_func, args=(test_conf['device_id'], test_conf['monitor_target']))

        # revert monitoring log
        tc_logger.removeHandler(lh)
        tc_logger.addHandler(ch)
        tc_logger.info('Monitoring system is starting adbd as root, waiting for {} seconds'.format(
            str(test_conf.get('monitor_root_sleep', 30))))
        time.sleep(test_conf.get('monitor_root_sleep', 30))


if __name__ == '__main__':
     run(module='testcase.tc_androbench',
         func='tc_run_micro_by_loops',
         loops=1,
         device_type='hikey970',
         device_id='571F15F101162DE5',
         #sequential='True',
         pre_case='perf_test_precondition',
         post_case='case_post_condition',
         pre_loop='restore_wb_cur_buf,restore_wb_avail_buf',
         post_loop='fstrim'
         # user_test_conf='/opt/automation/code_repo/execution/0126/android/result/600f8c21ca3de2567a9b4fd2/EA93BE100E6489D.yaml'
         )
    # run(suite_id='Debug', test_id='debug', module='testcase.function.hpb', func='check_4k_hit_count', device_id='3BE5859E00E312C6')
