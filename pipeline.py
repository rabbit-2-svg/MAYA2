"""
Author: William Zhou
Email: william_zhou@ymtc.com
"""
import os
import inspect
from time import sleep
from common.device import Device
from conf.test_conf import test_conf, tc_logger
from common.file_plant import create_file_by_iozone
from common.rwfile import write_csv_header, write_csv_result


def _sleep(*args, **kwargs):
    """
    Sleep some time, default is 10 seconds, time as a param after sleep action has top priority
    """
    sleep_time = test_conf.get('loop_sleep', None)
    if sleep_time is None:
        sleep_time = 10
    if args:
        sleep_time = int(args[0])
    tc_logger.info('==>Sleeping {} seconds.'.format(sleep_time))
    sleep(int(sleep_time))


def _check_mtp(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_mtp()


def _switch_mtp(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.switch_mtp(*args, **kwargs)


def _set_screen(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.set_screen()


def _root_device(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.root_device()


def _reboot_device(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.reboot_device(*args, **kwargs)


# 统一参数的入口到*args, **kwargs
def _scan_device(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.scan_device(test_conf['mongo_json'])


def _get_chip_capacity(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_chip_capacity()


def _get_chip_manufacturer(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_chip_manufacturer()


def _get_host_manufacturer(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_host_manufacturer()


# For WB Feature
def _open_tw(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.open_tw(*args, **kwargs)


def _check_tw(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.check_tw(*args, **kwargs)


def _get_wb_cur_buf(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_wb_cur_buf()


def _get_wb_avail_buf(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_wb_avail_buf()


def _restore_wb_cur_buf(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.restore_wb_cur_buf(*args, **kwargs)


def _restore_wb_avail_buf(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.restore_wb_avail_buf(*args, **kwargs)


# For HPB Feature
def _switch_hpb(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.switch_hpb(*args, **kwargs)


def _check_hpb_status(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_hpb_status()


def _check_hpb_version(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_hpb_version()


def _reset_hit_count(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.reset_hit_count(*args, **kwargs)


def _check_hit_count(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_hit_count()


def _check_hit_rate(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_hit_rate()


def _check_endian(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_endian()


def _switch_endian(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.switch_endian(*args, **kwargs)


def _check_hpb_read(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_hpb_read()


def _switch_hpb_read(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.switch_hpb_read(*args, **kwargs)


def _switch_hpb_debug_mode(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.switch_hpb_debug_mode(*args, **kwargs)


def _check_hpb_debug_mode(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_hpb_debug_mode()


def _check_bkops(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.check_bkops()


def _fstrim(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.fstrim(*args, **kwargs)


def _clean_test_file(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.clean_test_file()


def _get_hba(*args, **kwargs):
    """
    Generate local hba log path and get hba log from device

    See usage in main method
    :return: None
    """
    stack = inspect.stack()
    parent_method = stack[1].function
    ancestor_method = stack[2].function
    target_location = generate_path(parent_method, ancestor_method, 'hba', **kwargs)
    Device(test_conf['device_id']).get_hba(target_location)


def _get_dmesg(*args, **kwargs):
    """
    Generate local dmesg path and get dmesg log from device

    See usage in main method
    :return: None
    """
    stack = inspect.stack()
    parent_method = stack[1].function
    ancestor_method = stack[2].function
    target_location = generate_path(parent_method, ancestor_method, 'dmesg', **kwargs)
    Device(test_conf['device_id']).get_dmesg(target_location)


# 统一参数的入口到*args, **kwargs
def _get_smart_info(*args, **kwargs):
    """
    Generate local smart info path and get smart info from device
    See usage in main method
    :return: None
    """
    stack = inspect.stack()
    parent_method = stack[1].function
    ancestor_method = stack[2].function
    path = generate_path(parent_method, ancestor_method, 'smart_info', postfix='.bin', **kwargs)
    Device(test_conf['device_id']).get_smart_info(path)


# 统一参数的入口到*args, **kwargs
def _get_health_report(*args, **kwargs):
    """
    Get health report and write the parsed health report in health_report.csv
    See usage in main method
    :return: None
    """
    stack = inspect.stack()
    parent_method = stack[1].function
    ancestor_method = stack[2].function
    report_path = generate_path(parent_method, ancestor_method, 'health_report', postfix='.bin', **kwargs)
    hr_header, hr_value = Device(test_conf['device_id']).get_health_report(result_path=report_path)
    if 'loop' in kwargs.keys():
        health_report_csv = os.path.join(test_conf['monitor_home'], 'health_report.csv')
        write_csv_header(health_report_csv, hr_header)
        write_csv_result(health_report_csv, hr_value)


def _verify_adb_connection(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.verify_adb_connection(*args, **kwargs)


def _verify_hdmi_connection(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.verify_hdmi_connection(*args, **kwargs)


def _create_file_by_iozone(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    create_file_by_iozone(*args, **kwargs)


# region Assistant Methods
def generate_path(parent_method, ancestor_method, title, postfix='', **kwargs):
    """
    Generate local file path for health report & smart info

    :param parent_method: parent method which called main method
    :param ancestor_method: ancestor method which called main method
    :param title: title of file name
    :param postfix: postfix of file name
    :param kwargs: params collection
    :return: local file path
    """
    if ancestor_method not in ['fake_deco_by_duration', 'fake_deco_by_loops']:
        if parent_method == 'set_up':
            file_name = title + '_before_execution' + postfix
        else:
            file_name = title + '_after_execution' + postfix
        path = os.path.join(test_conf['result_home'], file_name)
    else:
        file_name = None
        if 'loop' in kwargs.keys():
            if parent_method == 'set_up':
                title = title + '_pre'
            else:
                title = title + '_post'
            file_name = title + '_' + str(kwargs['loop']).zfill(6) + postfix
        path = os.path.join(test_conf['monitor_home'], file_name) if file_name else None
    return path
# endregion


# Huizi
def _check_ffu(*args, **kwargs):
    """
    use for ffu status and fw revisoin check in ffu test
    see usage in main method
    """
    device = Device(test_conf['device_id'])
    device.check_ffu()


def _file_for_assistant_test(*args, **kwargs):
    """
    write fio file for assistant test
    See usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.file_for_assistant_test(*args, **kwargs)


def _push_bin_action(*args, **kwargs):
    """
    for FFU Tc push fw bin to /data
    See usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.push_bin_action(*args, **kwargs)


def _space_decrease_chart(*args, **kwargs):
    """
    for Peformance data avail space decrease
    :param args:
    :param kwargs:
    :return:
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.space_decrease_chart(*args, **kwargs)


def _get_fio_pid(*args, **kwargs):
    """
    get fio pid
    See usage in main method
    """

    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.get_fio_pid(*args, **kwargs)


def _wb_avail_buf_restore_loop_check(*args, **kwargs):
    """
    check wb_avail_buf make less 90% ,not restore enough
    :return: None
    See usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.wb_avail_buf_restore_loop_check(*args, **kwargs)


def _wb_avail_buf_restore_loop_check_no_enough(*args, **kwargs):
    """
    check wb_avail_buf make until 100%, restore enough
    See usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.wb_avail_buf_restore_loop_check_no_enough(*args, **kwargs)


def _get_data_space_and_cur_buf(*args, **kwargs):
    """
    use for performance_data_space_decrease_check
    see usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.get_data_space_and_cur_buf(*args, **kwargs)


def _statistic_with_chart(*args, **kwargs):
    """
    for fid background process get read or write data and chart
    see usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.statistic_with_chart(*args, **kwargs)


def _check_bkop(*args, **kwargs):
    """
    check bkop status
    see usage in main method
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.check_bkop(*args, **kwargs)


def _auto_calculate_loops(*args, **kwargs):
    """
    :param args:
    :param kwargs:
    :return:
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.auto_calculate_loops(*args, **kwargs)


def _get_adb_status(*args, **kwargs):
    """
    :get adb connect status
    :param args:
    :param kwargs:
    :return: tuple
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.get_adb_status(*args, **kwargs)


def _powerboard_action(*args, **kwargs):
    """
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.powerboard_action(*args, **kwargs)


# just for fw 1998 debug methods
def _ab_stress_debug_action(*args, **kwargs):
    """

    :param args:
    :param kwargs:
    :return:
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.ab_stress_debug_action(*args, **kwargs)


# Kelly
def _enable_tw(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.enable_tw(*args, **kwargs)


def _enable_flush(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.enable_flush(*args, **kwargs)


def _enable_hibern(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.enable_hibern(*args, **kwargs)


def _verify_wb_function(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.verify_wb_function(*args, **kwargs)


def _pull_avail_buf(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.pull_avail_buf(*args, **kwargs)


def _get_flush_time(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    if 'loop' in kwargs.keys():
        del kwargs['loop']

    device = Device(test_conf['device_id'])
    device.get_flush_time(*args, **kwargs)


def _get_wb_flush_status(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_wb_flush_status()


def _get_ee_bkops_status(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.get_ee_bkops_status()


# Below methods will be deprecated
def _enable_mtp(*args, **kwargs):
    """
    See usage in main method

    :return: None
    """
    device = Device(test_conf['device_id'])
    device.switch_mtp(exp_mtp=True)


def _clean_fio_file(*args, **kwargs):
    """
    See usage in main method
    :return: None
    """
    device = Device(test_conf['device_id'])
    device.clean_test_file()
