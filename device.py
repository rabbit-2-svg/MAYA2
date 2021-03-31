"""
Author: William Zhou
Email: william_zhou@ymtc.com
"""
import os
import time
import re
import random
import inspect
import subprocess
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from time import sleep
from adb.adb import ADB
from datetime import datetime
from conf.test_conf import tc_logger, test_conf
from common.assistant import unify_bool_value, convert_storage_unit
from common.rwfile import dump_append_dict_to_json_file, write_csv_header, write_csv_result
#from common.deco import pass_fail_common_deco


class Device:

    def __init__(self, device_id):
        self.device = device_id
        self.adb = ADB(device_id)
        self.support_device = test_conf['support_device']

    def check_mtp(self):
        """
        Check MTP status

        :return: tuple
        """
        result = ['N/A']
        header = ['mtp']
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Checking MTP mode')
            if device_type == 'mi10':
                cmd = 'shell "svc usb getFunctions" 2>&1'
            else:
                # mtp info is in stderr instead of stdout
                cmd = 'shell "svc usb getFunction" 2>&1'
            output = self.adb.execute_adb_command(cmd).lower()
            mtp = True if 'mtp' in output else False
            mode = 'enable' if 'mtp' in output else 'disable'
            tc_logger.info('==>Current MTP is {}'.format(mode))
            result[0] = mtp
        return header, result

    def switch_mtp(self, exp_mtp=True, check=True, max_try=5):
        """
        switch mtp mode

        :param exp_mtp: enable or disable mtp
        :param check: check that mtp is enabled or disabled
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            exp_mtp = unify_bool_value(exp_mtp)
            action = 'enable' if exp_mtp else 'disable'
            tc_logger.info('==>{} MTP mode'.format(action.capitalize()))
            if device_type == 'mi10':
                if exp_mtp:
                    cmd = 'shell "svc usb setFunctions mtp"'
                else:
                    cmd = 'shell "svc usb setFunctions"'
            else:
                if exp_mtp:
                    cmd = 'shell "svc usb setFunction mtp"'
                else:
                    cmd = 'shell "svc usb setFunction"'

            if unify_bool_value(check):
                i = max_try
                actual_mtp = self.check_mtp()[1][0]
                while actual_mtp is not exp_mtp and i > 0:
                    self.adb.execute_adb_command(cmd, print_stdout=False)
                    sleep(10)
                    actual_mtp = self.check_mtp()[1][0]
                    i -= 1
                if actual_mtp is not exp_mtp and i <= 0:
                    raise Exception('Fail to {} mtp in {} times!'.format(action, max_try))
            else:
                self.adb.execute_adb_command(cmd, print_stdout=False)
                sleep(10)

    def root_device(self):
        """
        root device

        :return: None
        """
        tc_logger.info('==>Rooting device')
        self.adb.execute_adb_command('root')
        # device_type = self.check_device_type()
        # if device_type:
        #     tc_logger.info('==>Rooting device')
        #     self.adb.execute_adb_command('root')
            # result = self.adb.execute_adb_command('root', print_stdout=False)
            # msgs = ['adbd is already running as root', 'adbd cannot run as root in production builds']
            # if result not in msgs:
            #     sleep(wait)

    def reboot_device(self, hdmi=True, timeout=120):
        """
        Reboot device
        :param hdmi: True means to verify HDMI connection, False means to verify adb connection
        :param timeout: Max time used to verify HDMI connection or ADB connection
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to reboot device')
            self.adb.execute_adb_command('reboot', print_stdout=False)
            sleep(50)
            if unify_bool_value(hdmi):
                result = self.verify_hdmi_connection(timeout)
                if result == -1:
                    raise Exception('HDMI is not ready')
            else:
                result = self.verify_adb_connection(timeout)
                if result == -1:
                    raise Exception('OS System is not ready')
            tc_logger.info('==>Reboot device over')

    def set_screen(self):
        device_type = self.check_device_type('hikey970')
        if device_type:
            tc_logger.info('==>Setting screen display size')
            self.adb.execute_adb_command('shell "wm density 136"')

    # Return values next phase
    def check_tw(self, tw=True, flush=True, hibernate=True):
        """
        Check WB status of Mi10
        :param tw: whether to check tw_enable
        :param flush: whether to check tw_flush_en
        :param hibernate: whether to check tw_enable_autoflush_in_h8
        :return: None
        """
        device_type = self.check_device_type('mi10')
        if device_type:
            tc_logger.info('==>Start to check Mi10 write booster status')
            tw_enable = test_conf['mi10']['wb']['tw_enable']
            force_flush = test_conf['mi10']['wb']['flush']
            hibernate_flush = test_conf['mi10']['wb']['hibernate_flush']

            cat_cmd = list()
            if unify_bool_value(tw):
                cat_cmd.append('shell "cat {}"'.format(tw_enable))
            if unify_bool_value(flush):
                cat_cmd.append('shell "cat {}"'.format(force_flush))
            if unify_bool_value(hibernate):
                cat_cmd.append('shell "cat {}"'.format(hibernate_flush))

            open_tw = True
            for cmd in cat_cmd:
                status = int(self.adb.execute_adb_command(cmd))
                if status == 0:
                    open_tw = False
            if open_tw:
                if len(cat_cmd) == 3:
                    tc_logger.info('==>Mi10 write booster is open')
                else:
                    tc_logger.info('==>{} are enabled'.format(' and '.join(cat_cmd)))
            else:
                tc_logger.info('==>Mi10 write booster is closed')

    def open_tw(self, tw=True, flush=True, hibernate=True, check=True, max_try=30):
        """
        Open WB for Mi10

        :param tw: whether to enable tw_enable
        :param flush: whether to enable tw_flush_en
        :param hibernate: whether to enable tw_enable_autoflush_in_h8
        :param check: double confirm that tw, flush, hibernate are enabled
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type('mi10')
        if device_type:
            tc_logger.info('==>Start to open Mi10 host write booster')
            tw_enable = test_conf['mi10']['wb']['tw_enable']
            force_flush = test_conf['mi10']['wb']['flush']
            hibernate_flush = test_conf['mi10']['wb']['hibernate_flush']

            cat_cmd = list()
            echo_cmd = list()
            attributes = list()
            if unify_bool_value(tw):
                attributes.append(tw_enable)
                cat_cmd.append('shell "cat {}"'.format(tw_enable))
                echo_cmd.append('shell "echo 1 > {}"'.format(tw_enable))
            if unify_bool_value(flush):
                attributes.append(force_flush)
                cat_cmd.append('shell "cat {}"'.format(force_flush))
                echo_cmd.append('shell "echo 1 > {}"'.format(force_flush))
            if unify_bool_value(hibernate):
                attributes.append(hibernate_flush)
                cat_cmd.append('shell "cat {}"'.format(hibernate_flush))
                echo_cmd.append('shell "echo 1 > {}"'.format(hibernate_flush))

            i = 0
            while i < len(echo_cmd):
                if not check:
                    self.adb.execute_adb_command(echo_cmd[i], print_stdout=False)
                else:
                    status = int(self.adb.execute_adb_command(cat_cmd[i]))
                    while status != 1 and max_try > 0:
                        self.adb.execute_adb_command(echo_cmd[i], print_stdout=False)
                        status = int(self.adb.execute_adb_command(cat_cmd[i]))
                        max_try -= 1
                    if max_try <= 0:
                        raise Exception('Failed to enable {} !'.format(attributes[i]))
                i += 1
            tc_logger.info('==>Open Mi10 write booster over')

    def get_wb_cur_buf(self):
        """
        Get wb cur buf from device
        :return: tuple
        """
        header = ['wb_cur_buf']
        result = ['Invalid device']
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to get wb cur buf')
            if device_type == 'mi10':
                cur_wb_path = test_conf['mi10']['attributes']['cur_buf']
                cmd = 'shell cat {}'.format(cur_wb_path)
                _cur_wb = self.adb.execute_adb_command(cmd)
                cur_wb = self.get_readable_wb_buf(_cur_wb, _hex=True)
            elif device_type in ['hikey970', '970']:
                cur_wb_path = test_conf['hikey970']['wb']['cur_buf']
                cmd = 'shell cat {}'.format(cur_wb_path)
                _cur_wb = self.adb.execute_adb_command(cmd)
                _cur_wb = _cur_wb.split(':')[1].split('(')[0].replace(' ', '')
                cur_wb = convert_storage_unit(_cur_wb)
            else:
                regs_path = test_conf['hikey960']['wb']['regs']
                cmd = """shell 'cat {};dmesg | grep "cur wb buff size"'""".format(regs_path)
                _cur_wb = self.adb.execute_adb_command(cmd, print_stdout=False)
                _cur_wb = _cur_wb.split('cur wb buff size is')[-1].strip()
                cur_wb = self.get_readable_wb_buf(_cur_wb, _hex=True)
            result[0] = cur_wb
            tc_logger.info('==>Current wb cur buf: {}'.format(cur_wb))
        return header, result

    def restore_wb_cur_buf(self, expect_buf=None, check_flush_status=None, by_wait=False, flush_timeout=120, flush_count=5):
        """
        Restore wb cur buf by doing fstrim and flush, default restore 5 times, each time flush 2 minutes
        Will restore wb cur buf to 24G by default
        Will print warning message when fail to restore wb cur buf

        Author: William Zhou
        :param expect_buf: expected wb cur buf after restore
        :param check_flush_status: indicate whether to check flush status after flush. If it's None, will not check flush status when chip provider is SS
        :param by_wait: indicate whether to use force flush or by wait purely to restore wb cur buf
        :param flush_timeout: flush time of each flush
        :param flush_count: max flush times
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            if expect_buf is None:
                expect_buf = '12G' if test_conf['chip_capacity'] == '128G' else '24G'
            if check_flush_status is None:
                check_flush_status = True if test_conf['chip_manufacturer'] == 'ymtc' else False

            cur_wb = self.get_wb_cur_buf()[1][0]
            int_cur_wb = int(cur_wb.lower().split('g')[0])
            int_exp_buf = int(expect_buf.lower().split('g')[0])

            if int_cur_wb < int_exp_buf:
                tc_logger.info('==>WB cur buf: {0}, lower than expected: {1}, start to restore'.format(cur_wb, expect_buf.upper()))
                i = 0
                interval = 10
                total_time = int(flush_timeout) * int(flush_count)
                if unify_bool_value(by_wait):
                    clock = total_time
                    while int_cur_wb < int_exp_buf and i < clock:
                        i += interval
                        sleep(interval)
                        cur_wb = self.get_wb_cur_buf()[1][0]
                        int_cur_wb = int(cur_wb.lower().split('g')[0])
                else:
                    check_flush_status = unify_bool_value(check_flush_status)
                    clock = flush_count if check_flush_status else total_time
                    while int_cur_wb < int_exp_buf and i < clock:
                        i += 1
                        self.fstrim()
                        self.flush_wb_avail_buf()
                        if check_flush_status:
                            sleep(2)
                            _flush_timeout = flush_timeout
                            result = self.get_wb_flush_status()
                            while result != 0 and _flush_timeout > 0:
                                sleep(interval)
                                _flush_timeout -= interval
                                result = self.get_wb_flush_status()
                            if _flush_timeout <= 0:
                                tc_logger.warning('Timeout to flush, {0}st flush, cost {1} seconds!'.format(i, flush_timeout))
                        else:
                            sleep(1)
                        cur_wb = self.get_wb_cur_buf()[1][0]
                        int_cur_wb = int(cur_wb.lower().split('g')[0])
                if i >= clock:
                    tc_logger.warning('Timeout to restore wb cur buf, cost {0} seconds, wb cur buf: {1}'.format(total_time, cur_wb))
                else:
                    tc_logger.info('==>WB cur buf: {0}, equal or greater than {1}, restore over'.format(cur_wb, expect_buf.upper()))
            else:
                tc_logger.info('==>WB cur buf: {0}, equal or greater than {1}, ready to test'.format(cur_wb, expect_buf.upper()))

    def get_wb_avail_buf(self):
        """
        Get wb avail buf from device
        :return: tuple
        """
        header = ['wb_avail_buf']
        result = ['Invalid device']
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to get wb avail buf')
            if device_type == 'mi10':
                avail_wb_path = test_conf['mi10']['attributes']['avail_buf']
                cmd = 'shell "cat {}"'.format(avail_wb_path)
                _avail_wb = self.adb.execute_adb_command(cmd)
                avail_wb = self.get_readable_wb_buf(_avail_wb, _hex=True, percentage=True)
            else:
                key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
                avail_wb_path = test_conf[key]['wb']['avail_buf']
                cmd = 'shell "cat {}"'.format(avail_wb_path)
                _avail_wb = self.adb.execute_adb_command(cmd)
                if ':' in _avail_wb:
                    _avail_wb = _avail_wb.split(':')[1].strip()
                avail_wb = self.get_readable_wb_buf(_avail_wb, percentage=True)
            result[0] = avail_wb
            tc_logger.info('==>WB avail buf: {}'.format(avail_wb))
        return header, result

    def restore_wb_avail_buf(self, expect_buf=100, check_flush_status=None, by_wait=False, flush_timeout=120, flush_count=5):
        """
        Restore wb avail buf by doing flush, default flush 5 times, each time flush 2 minutes,
        Will restore avail buf to 100% by default
        Will print warning message when fail to restore wb avail buf

        Author: William Zhou
        :param expect_buf: expected wb avail buf, like 100, 90
        :param check_flush_status: indicate whether to check flush status after flush. If it's None, will not check flush status when chip provider is SS
        :param by_wait: indicate whether to use force flush or by wait purely to restore wb cur buf
        :param flush_timeout: flush time of each flush
        :param flush_count: max flush times
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            if check_flush_status is None:
                check_flush_status = True if test_conf['chip_manufacturer'] == 'ymtc' else False

            int_exp_buf = int(expect_buf)
            if int_exp_buf < 10:
                int_exp_buf = int_exp_buf * 10
            str_exp_buf = str(int_exp_buf) + '%'
            avail_wb = self.get_wb_avail_buf()[1][0]
            int_avail_wb = int(avail_wb.split('%')[0])

            if int_avail_wb < int_exp_buf:
                tc_logger.info('==>WB available buf: {0}, lower than expected: {1}, start to restore'.format(avail_wb, str_exp_buf))
                i = 0
                interval = 10
                total_time = int(flush_timeout) * int(flush_count)
                if unify_bool_value(by_wait):
                    clock = total_time
                    while int_avail_wb < int_exp_buf and i < clock:
                        i += interval
                        sleep(interval)
                        avail_wb = self.get_wb_avail_buf()[1][0]
                        int_avail_wb = int(avail_wb.split('%')[0])
                else:
                    check_flush_status = unify_bool_value(check_flush_status)
                    clock = flush_count if check_flush_status else total_time
                    while int_avail_wb < int_exp_buf and i < clock:
                        i += 1
                        self.flush_wb_avail_buf()
                        if check_flush_status:
                            sleep(2)
                            result = self.get_wb_flush_status()
                            _flush_timeout = flush_timeout
                            while result != 0 and _flush_timeout > 0:
                                sleep(interval)
                                _flush_timeout -= interval
                                result = self.get_wb_flush_status()
                            if _flush_timeout <= 0:
                                tc_logger.warning('Timeout to flush, {0}st flush, cost {1} seconds!'.format(i, flush_timeout))
                        else:
                            sleep(1)
                        avail_wb = self.get_wb_avail_buf()[1][0]
                        int_avail_wb = int(avail_wb.split('%')[0])
                    if i >= clock:
                        tc_logger.warning('Timeout to restore wb avail buf, cost {0} seconds, wb avail buf: {1}'.format(total_time, avail_wb))
                    else:
                        tc_logger.info('==>WB available buf: {0}, equal or greater than {1}, restore over'.format(avail_wb, str_exp_buf))
            else:
                tc_logger.info('==>WB available buf: {0}, equal or greater than {1}, ready to test'.format(avail_wb, str_exp_buf))

    def reset_hit_count(self, max_try=10):
        """
        Reset HPB hit count
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to reset HPB hit count')
            if device_type == 'mi10':
                hit_count_switch = test_conf['mi10']['hpb']['reset_hit_count']
            else:
                key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
                hit_count_switch = test_conf[key]['hpb']['reset_hit_count']
            cmd = 'shell "echo 1 > {}"'.format(hit_count_switch)
            hit_count = str(self.check_hit_count()[1][1])
            i = max_try
            while hit_count != '0' and i > 0:
                i -= 1
                self.adb.execute_adb_command(cmd, print_stdout=False)
                sleep(1)
                hit_count = str(self.check_hit_count()[1][1])
            if i <= 0:
                tc_logger.warning('Failed to reset HPB hit count in {} times!'.format(max_try))
                return False
            else:
                tc_logger.info('==>Reset HPB hit count to 0 over')
                return True
        return False

    def check_hpb_status(self):
        """
        Check current hpb status, this is not supported in Hikey960

        return: tuple
        """
        result = ['N/A']
        header = ['hpb_status']
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to check HPB status')
            hpb_switch = test_conf[device_type]['hpb']['disable']
            cmd = 'shell "cat {0}"'.format(hpb_switch)
            status = self.adb.execute_adb_command(cmd)
            if device_type == 'mi10':
                status = int(status.split('\n')[0].split('=')[1].strip())
                hpb_status = True if status == 1 else False
            else:
                status = int(status.split()[1].strip())
                hpb_status = True if status == 0 else False
            result[0] = hpb_status
            readable_hpb_status = 'enabled' if hpb_status else 'disabled'
            tc_logger.info('==>Check HPB status over, current is {}'.format(readable_hpb_status))
        return header, result

    def switch_hpb(self, hpb=True, check=True, max_try=5):
        """
        Enable or disable HPB, this is not supported in Hikey960

        :param hpb: True means to enable HPB, False means opposite
        :param check: indicate whether to check current hpb status after switch hpb
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            exp_hpb = unify_bool_value(hpb)
            action = 'enable' if exp_hpb else 'disable'
            tc_logger.info('==>Start to {} HPB'.format(action))
            if exp_hpb:
                value = 0
            else:
                if device_type == 'mi10':
                    value = 3
                else:
                    value = 1

            hpb_switch = test_conf[device_type]['hpb']['disable']
            cmd = 'shell "echo {0} > {1}"'.format(str(value), hpb_switch)
            if unify_bool_value(check):
                i = max_try
                cur_hpb = self.check_hpb_status()[1][0]
                while cur_hpb is not exp_hpb and i > 0:
                    i -= 1
                    self.adb.execute_adb_command(cmd, print_stdout=False)
                    sleep(1)
                    cur_hpb = self.check_hpb_status()[1][0]
                if i <= 0:
                    raise Exception('Failed to {0} HPB in {1} times, current HPB status is {2}'.format(action, max_try, cur_hpb))
            else:
                self.adb.execute_adb_command(cmd, print_stdout=False)
            tc_logger.info('==>{} HPB over'.format(action.capitalize()))

    def check_endian(self):
        """
        Check current endian, this is not supported in Mi10

        return: tuple
        """
        result = ['N/A']
        header = ['hpb_endian']
        device_type = self.check_device_type(['hikey960', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to check endian')
            key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
            endian_switch = test_conf[key]['hpb']['endian']
            cmd = 'shell "cat {0}"'.format(endian_switch)
            endian = self.adb.execute_adb_command(cmd)
            result[0] = endian.split()[0]
            tc_logger.info('==>Check endian over, current is {}'.format(endian))
        return header, result

    def switch_endian(self, endian=None, check=True, max_try=5):
        """
        Switch endian between SS endian and JEDEC endian, this is not supported in Mi10

        :param endian: JEDEC and SS, if endian is None, will switch SS endian when chip provider is SS, and switch to JEDEC when chip provider is YMTC
        :param check: indicate whether to check current endian after switch endian
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type(['hikey960', 'hikey970'])
        if device_type:
            if endian is None:
                endian = 'JEDEC' if test_conf['chip_manufacturer'] == 'ymtc' else 'SS'
            _endian = endian.upper()
            tc_logger.info('==>Start to switch to {} endian'.format(_endian))
            value = '1' if _endian == 'SS' else '0'
            key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
            endian_switch = test_conf[key]['hpb']['endian']
            cmd = 'shell "echo {0} > {1}"'.format(value, endian_switch)
            if unify_bool_value(check):
                i = max_try
                cur_endian = self.check_endian()[1][0].upper()
                while cur_endian != _endian and i > 0:
                    i -= 1
                    self.adb.execute_adb_command(cmd, print_stdout=False)
                    sleep(1)
                    cur_endian = self.check_endian()[1][0].upper()
                if i <= 0:
                    raise Exception('Failed to switch to {0} endian in {1} times, current is {2} endian'.format(endian, max_try, cur_endian))
            else:
                self.adb.execute_adb_command(cmd, print_stdout=False)
            tc_logger.info('==>Switch to {} endian over'.format(endian))

    def check_hpb_read(self):
        """
        Check current hpb read, read 16 or hpb read, this is not supported in Mi10

        return: tuple
        """
        result = ['N/A']
        header = ['hpb_read']
        device_type = self.check_device_type(['hikey960', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to check hpb read')
            key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
            hpb_read_switch = test_conf[key]['hpb']['read_mode']
            cmd = 'shell "cat {0}"'.format(hpb_read_switch)
            hpb_read = self.adb.execute_adb_command(cmd)
            result[0] = hpb_read
            tc_logger.info('==>Check hpb read over, current is {}'.format(hpb_read))
        return header, result

    def switch_hpb_read(self, hpb_read=None, check=True, max_try=5):
        """
        Switch between HPB Read and Read 16, this is not supported in Mi10

        :param hpb_read: True means HPB Read mode, False means Read 16.
                         If hpb_read is None, will switch Read 16 when chip provider is SS, and switch to JEDEC Read when chip provider is YMTC
        :param check: indicate whether to check current hpb read mode after switch
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type(['hikey960', 'hikey970'])
        if device_type:
            if hpb_read is None:
                hpb_read = True if test_conf['chip_manufacturer'] == 'ymtc' else False
            _hpb_read = unify_bool_value(hpb_read)
            value = '1' if _hpb_read else '0'
            exp_mode = 'JEDEC Read' if _hpb_read else 'Read 16'
            tc_logger.info('==>Start to switch to {}'.format(exp_mode))
            key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
            read_switch = test_conf[key]['hpb']['read_mode']
            cmd = 'shell "echo {0} > {1}"'.format(value, read_switch)
            if unify_bool_value(check):
                i = max_try
                cur_mode = self.check_hpb_read()[1][0]
                while cur_mode.upper() != exp_mode.upper() and i > 0:
                    i -= 1
                    self.adb.execute_adb_command(cmd, print_stdout=False)
                    sleep(1)
                    cur_mode = self.check_hpb_read()[1][0]
                if i <= 0:
                    raise Exception('Failed to switch to {0} in {1} times, current is {2}'.format(exp_mode, max_try, cur_mode))
            else:
                self.adb.execute_adb_command(cmd, print_stdout=False)
            tc_logger.info('==>Switch to {} over'.format(exp_mode))

    def check_hpb_debug_mode(self):
        """
        Check current hpb debug mode, this is not supported in Hikey960

        return: tuple
        """
        result = ['N/A']
        header = ['hpb_debug_mode']
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to check HPB debug mode')
            switch = test_conf[device_type]['hpb']['debug']
            cmd = 'shell "cat {0}"'.format(switch)
            status = self.adb.execute_adb_command(cmd)
            if device_type == 'mi10':
                status = int(status.split('\n')[-1].strip().split()[-1].strip())
                debug_mode = True if status == 3 else False
            else:
                status = int(status.split()[-1].strip())
                debug_mode = True if status == 1 else False
            result[0] = debug_mode
            readable_debug_mode = 'enabled' if debug_mode else 'disabled'
            tc_logger.info('==>Check HPB debug mode, current is {}'.format(readable_debug_mode))
        return header, result

    def switch_hpb_debug_mode(self, debug_mode=True, check=True, max_try=5):
        """
        Switch log debug mode, this is not supported in Hikey960

        :param debug_mode: enable or disable HPB debug mode
        :param check: indicate whether to check current debug mode after switch
        :param max_try: max execution times
        :return: None
        """
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            exp_debug_mode = unify_bool_value(debug_mode)
            action = 'enable' if exp_debug_mode else 'disable'
            tc_logger.info('==>Start to {} HPB debug mode'.format(action))
            if not exp_debug_mode:
                value = 0
            else:
                if device_type == 'mi10':
                    value = 3
                else:
                    value = 1

            switch = test_conf[device_type]['hpb']['debug']
            cmd = 'shell "echo {0} > {1}"'.format(str(value), switch)
            if unify_bool_value(check):
                i = max_try
                cur_debug_mode = self.check_hpb_debug_mode()[1][0]
                while cur_debug_mode is not exp_debug_mode and i > 0:
                    i -= 1
                    self.adb.execute_adb_command(cmd, print_stdout=False)
                    sleep(1)
                    cur_debug_mode = self.check_hpb_debug_mode()[1][0]
                if i <= 0:
                    raise Exception('Failed to {0} HPB debug mode in {1} times, current is {2}'.format(action, max_try, cur_debug_mode))
            else:
                self.adb.execute_adb_command(cmd, print_stdout=False)
            tc_logger.info('==>{} HPB debug mode over'.format(action.capitalize()))

    def clean_test_file(self):
        """
        Delete fio test files in device
        :return: None
        """
        tc_logger.info('==>Cleaning fio test files')
        commands = ['shell "rm -rf /data/fio_*"', 'shell "rm -rf /data/auto_tools/fio_*"', 'shell "rm -rf /data/auto_tools/iozone.*"', 'shell "rm -rf /data/*.1.log"']
        for cmd in commands:
            self.adb.execute_adb_command(cmd, print_stdout=False)

    def fstrim(self, exe_file=None, mount_point=None):
        """
        Execute umap command in device
        :param exe_file: fstrim exe file path
        :param mount_point: the dir which will be fstrim
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to execute fstrim')
            if mount_point is None:
                mount_point = test_conf['work_space']
            if exe_file is None:
                exe_file = test_conf['tool']['fstrim']
            command = "shell {} {}".format(exe_file, mount_point)
            self.adb.execute_adb_command(command)
            tc_logger.info('==>Execute fstrim over')

    # need to refine, 4k, 8k+, 32k+
    def check_hit_rate(self):
        """
        Check HPB hit rate
        :return: tuple of string
        """
        result = ['None'] * 2
        header = ['Hit Count', 'Hit Rate']
        file_size = test_conf.get('file_size', None)
        block_size = test_conf.get('block_size', None)
        threads = test_conf.get('threads', None)
        sub_jobs = test_conf.get('sub_jobs', None)
        common_threads = threads if threads else sub_jobs

        actual_hit_count = self.check_hit_count()[1][0]
        if actual_hit_count is None:
            tc_logger.warning('Fail to get HPB hit count, skip check HPB hit rate!')
        else:
            result[0] = actual_hit_count
            if file_size is None or block_size is None or common_threads is None:
                tc_logger.warning('File size/block size/threads/sub_jobs, at least one is not defined, skip calculating HPB hit rate!')
            else:
                tc_logger.info('==>Start to calculate HPB hit rate')
                if 'K' in file_size.upper():
                    b_file_size = int(file_size.upper().split('K')[0]) * 1024
                elif 'M' in file_size.upper():
                    b_file_size = int(file_size.upper().split('M')[0]) * 1024 * 1024
                elif 'G' in file_size.upper():
                    b_file_size = int(file_size.upper().split('G')[0]) * 1024 * 1024 * 1024
                else:
                    b_file_size = int(file_size.upper().split('B')[0])

                if 'K' in block_size.upper():
                    b_block_size = int(block_size.upper().split('K')[0]) * 1024
                elif 'M' in block_size.upper():
                    b_block_size = int(block_size.upper().split('M')[0]) * 1024 * 1024
                elif 'G' in block_size.upper():
                    b_block_size = int(block_size.upper().split('G')[0]) * 1024 * 1024 * 1024
                else:
                    b_block_size = int(block_size.upper().split('B')[0])

                expect_hit_count = b_file_size * int(common_threads) / b_block_size
                _hit_rate = '%.4f' % (int(actual_hit_count) / expect_hit_count)
                hit_rate = str(float(_hit_rate) * 100) + '%'
                result[1] = hit_rate
                tc_logger.info('Expected hit count: {0}, actual hit count: {1}'.format(int(expect_hit_count), actual_hit_count))
                tc_logger.info('==>Calculate HPB hit rate over, it is {}'.format(hit_rate))
        return header, result

    def check_hit_count(self):
        """
        Check HPB hit count

        :return: tuple
        """
        result = [None] * 5
        header = ['read_count', 'total_hit_count', '4k_hit_count', '8_32k_hit_count', '36k_plus_hit_count']
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to check HPB hit count')
            path = test_conf[device_type]['hpb']['hit_count']
            cmd = 'shell "cat {}"'.format(path)
            raw_hit_count = self.adb.execute_adb_command(cmd)
            if device_type == 'mi10':
                read_count = raw_hit_count.split('\n')[0].strip().split()[1]
                hit_count = raw_hit_count.split('\n')[1].strip().split()[1]
                result[0] = read_count
                result[1] = hit_count
                result[2] = hit_count
            else:
                read_count = raw_hit_count.split(',')[0].strip().split()[1]
                total_hit_count = raw_hit_count.split(',')[1].strip().split()[1]
                hit_count_4k = raw_hit_count.split(',')[1].strip().split()[3]
                hit_count_8_32k = raw_hit_count.split(',')[1].strip().split()[5]
                hit_count_36k_plus = raw_hit_count.split(',')[2].strip().split()[1]
                result[0] = read_count
                result[1] = total_hit_count
                result[2] = hit_count_4k
                result[3] = hit_count_8_32k
                result[4] = hit_count_36k_plus
            tc_logger.info('==>Check HPB hit count over, read_count: {0}, total_hit_count: {1}, 4k_hit_count: {2}, 8_32k_hit_count: {3}, '
                           '36k_plus_hit_count: {4}'.format(result[0], result[1], result[2], result[3], result[4]))
        return header, result

    def check_bkops(self):
        """
        Check bkops status

        :return: tuple
        """
        result = ['N/A']
        header = ['bkops_status']
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to check bkops')
            bkops_status_path = test_conf[device_type]['attributes']['bkops_status']
            cmd = 'shell "cat {}"'.format(bkops_status_path)
            _bkops_status = self.adb.execute_adb_command(cmd)
            bkops_status = str(int(_bkops_status, 16))
            tc_logger.info('Check bkops over, current bkops: {}'.format(bkops_status))
            result[0] = bkops_status
        return header, result

    def scan_device(self, json_file=None):
        """
        Fetch basic information from device
        :param json_file: json file to save device basic info
        :return: dict of device basic info
        """
        tc_logger.info('==>Start to scan device')
        result = {"device_info": {"key_info": {}, "android_props": {}}}
        kernal_version = self.adb.execute_adb_command("shell uname -a").strip().split(" ")[2].strip()
        result["device_info"]["key_info"]["kernal_version"] = kernal_version
        board_manufacturer = self.adb.execute_adb_command("shell getprop ro.product.product.manufacturer")
        result["device_info"]["key_info"]["board_manufacturer"] = board_manufacturer
        device_manufacturer = self.adb.execute_adb_command("shell getprop ro.product.manufacturer")
        result["device_info"]["key_info"]["device_manufacturer"] = device_manufacturer
        device_brand = self.adb.execute_adb_command("shell getprop ro.product.brand")
        result["device_info"]["key_info"]["device_brand"] = device_brand
        android_release = self.adb.execute_adb_command("shell getprop ro.build.version.release")
        result["device_info"]["key_info"]["android_release"] = android_release
        android_sdk = self.adb.execute_adb_command("shell getprop ro.build.version.sdk")
        result["device_info"]["key_info"]["android_sdk"] = android_sdk
        android_props = self.adb.execute_adb_command("shell getprop | grep -F [ro.").split("\n")

        for row in android_props:
            key = row.split("]: [")[0]
            if key.startswith("["):
                key = key[1:]
            key = key.replace(".", "_")
            key = key.replace("-", "_")
            value = "[" + row.split("]: [")[1]
            result["device_info"]["android_props"][key] = value
        if json_file is not None:
            dump_append_dict_to_json_file(result, json_file)
        tc_logger.info('==>Scan device over')
        return result

    def get_hba(self, target_location=None):
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to pull HBA log')
            if target_location is None:
                cur_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                target_location = os.path.join(test_conf['monitor_home'], 'hba' + cur_time)
            if device_type == 'mi10':
                source_hba = '/d/1d84000.ufshc/show_hba'
            else:
                source_hba = '/d/ff3c0000.ufs/show_hba'
            cmd = "pull {} {}".format(source_hba, target_location)
            self.adb.execute_adb_command(cmd)
            tc_logger.info('==>Pull HBA log over')

    def get_dmesg(self, target_location=None):
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to collect dmesg')
            if target_location is None:
                cur_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                target_location = os.path.join(test_conf['monitor_home'], 'dmesg' + cur_time)
            cmd = 'shell "dmesg" >> {}'.format(target_location)
            self.adb.execute_adb_command(cmd)
            tc_logger.info('==>Collect dmesg log over')

    def get_smart_info(self, result_path=None, parse=True):
        """
        Use SCSI command to generate smart info and pull it to test machine, will skip if chip provider is SS

        :param result_path: smart info path in test machine, like a PC, a RP
        :param parse: True means to parse smart info, False means the opposite
        :return: smart info path in test machine
        """
        tc_logger.info('==>Start to get smart info')
        value = ["N/A"]
        header = ["N/A"]

        if test_conf['chip_manufacturer'] != 'ymtc':
            tc_logger.warning('==>None YMTC chip has no smart info!')
            return None
        if result_path is None:
            cur_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            _smart_info_name = 'smart_info_' + cur_time + '.bin'
            result_path = os.path.join(test_conf['monitor_home'], _smart_info_name)
        smart_info_name = 'smart_info'

        all_smart_info = os.path.join(test_conf['tool']['dir'], smart_info_name + '*')
        smart_info_path = os.path.join(test_conf['tool']['dir'], smart_info_name + '.bin')
        sg3_utils_lib = os.path.join(test_conf['tool']['sg3'], 'lib')
        sg_raw = os.path.join(test_conf['tool']['sg3'], 'bin', 'sg_raw')
        smart_info_password = os.path.join(test_conf['tool']['sg3'], 'passwords', 'JGS12_SMART_INFO.bin')

        rm_cmd = 'shell "rm -f {}"'.format(all_smart_info)
        gen_cmd = 'shell "export LD_LIBRARY_PATH={0};' \
                  '{1} -s 0x2c --infile={3} /dev/block/sda 3b e1 00 00 00 00 00 00 2c 00 -v;' \
                  '{1} -r 4096 /dev/block/sda 3c c1 00 00 00 00 00 10 00 00 -v ' \
                  '--outfile={2}"'.format(sg3_utils_lib, sg_raw, smart_info_path, smart_info_password)
        save_cmd = "pull {} {}".format(smart_info_path, result_path)
        self.adb.execute_adb_command(rm_cmd)
        self.adb.execute_adb_command(gen_cmd)
        self.adb.execute_adb_command(save_cmd)
        self.adb.execute_adb_command(rm_cmd)

        if parse is True:
            tc_logger.info('==>Parsing smart info')
            readable_smart_info = os.path.join(test_conf['result_home'], 'smart_info.csv')
            with open(result_path, "rb") as f:
                byte_array = f.read()
            header = [
                'host_total_write_cmd_count', 'host_total_read_cmd_count', 'host_total_trim_cmd_count', 'host_total_flush_cmd_count',
                'host_total_ssu_cmd_count', 'host_total_write_count', 'host_total_read_count', 'host_total_uncor_err_cnt', 'medium_error_lba',
                'host_write_cmd_err_count', 'host_read_cmd_err_count', 'host_apu_reset_count', 'host_link_down_count', 'FW_commit_id', 'FW_bin_type',
                'flush_cnt_0', 'flush_cnt_1', 'flush_cnt_2', 'flush_dummy_cnt_0', 'flush_dummy_cnt_1', 'flush_dummy_cnt_2', 'flush_dummy_cnt_3',
                'flush_dummy_cnt_4', 'max_read_cnt_0', 'max_read_cnt_1', 'max_read_cnt_2', 'max_read_cnt_3', 'max_read_cnt_4', 'max_read_cnt_5',
                'max_read_cnt_6', 'max_read_cnt_7', 'max_read_cnt_8', 'max_read_cnt_9', 'max_read_cnt_10', 'max_read_cnt_11', 'max_read_cnt_12',
                'max_read_cnt_13', 'max_read_cnt_14', 'max_read_cnt_15', 'gc_fill_dummy_count', 'max_one_for_one_gc_count', 'last_spor_op_block',
                'host_initiated_defrag_count', 'debug_jira_0', 'debug_jira_1', 'latest_reset_type', 'dme_err_cnt', 'ufs_wcq_err_cnt',
                'hpb_recm_db_q_overflow_cnt', 'autostdby_db_q_cnt', 'hpb_read_total_cnt', 'hpb_read_cnt1', 'hpb_read_cnt2', 'hpb_read_hit_cnt',
                'sram_bitflip_detect_count', 'read_retry_fail_pca_0', 'read_retry_fail_pca_1', 'read_retry_fail_pca_2', 'lost_wl_page_cnt',
                'pte_gc_trigger_count', 'pte_gc_rd_trigger_count', 'data_gc_trigger_count', 'wl_trigger_count', 'rd_trigger_count', 'revoke_trigger_count',
                'bkops_trigger_count', 'gc_total_release_source_count', 'gc_release_src_0', 'gc_release_src_1', 'gc_release_src_2', 'gc_release_src_3',
                'gc_release_src_4', 'gc_release_src_5', 'gc_release_src_6', 'gc_release_src_7', 'gc_release_src_8', 'gc_release_src_9', 'gc_release_src_10',
                'gc_release_src_11', 'gc_release_src_12', 'gc_release_src_13', 'gc_release_src_14', 'gc_release_src_15', 'gc_fast_release_vc_zero_source_cnt',
                'gc_first_src_vb_vc_ratio_0', 'gc_first_src_vb_vc_ratio_1', 'gc_first_src_vb_vc_ratio_2', 'gc_first_src_vb_vc_ratio_3',
                'gc_first_src_vb_vc_ratio_4', 'gc_first_src_vb_vc_ratio_5', 'gc_first_src_vb_vc_ratio_6', 'gc_first_src_vb_vc_ratio_7',
                'gc_first_src_vb_vc_ratio_8', 'gc_first_src_vb_vc_ratio_9', 'gc_first_src_vb_vc_ratio_10', 'gc_rebuild_rtv_valid_cnt_mismatch',
                'gc_load_pte_bmp_fail_cnt', 'replace_die_src_vb_vld_cnt_zero', 'rd_src_vb_vld_cnt_zero', 'wl_src_vb_vld_cnt_zero',
                'imcomplete_src_vb_vld_cnt_zero', 'gc_vb_cnt', 'wl_vb_cnt', 'refresh_l2_uecc_happen', 'refresh_gc_uecc_happen', 'purge_trigger_count',
                'create_l2_wait_free_vb', 'create_l2_wait_free_pte', 'max_gc_life_time', 'max_l2_wait_time', 'pre_read_mistrig_count', 'pre_read_enable_count',
                'pre_read_abort_count', 'pre_read_unc_retry_count', 'pre_load_reset_count', 'pre_load_enable_count', 'pre_load_gain_count',
                'st1_full_hit_count', 'st1_full_wait_max_time', 'close_l2_vld_cnt_zero', 'l2_vb_count_0', 'l2_vb_count_1', 'l2_read_disturb_cnt',
                'total_d1_erase_count', 'total_d3_erase_count', 'total_d1_program_count', 'total_d3_program_count', 'total_d1_read_count', 'cis_rd_cnt',
                'd1_erase_fail_count', 'd3_erase_fail_count', 'd1_program_fail_count', 'd3_program_fail_count', 'd1_read_retry_ok_count',
                'd3_read_retry_ok_count', 'd1_read_retry_fail_count', 'd3_read_retry_fail_count', 'aom_read_retry_ok_count', 'aom_read_retry_fail_count',
                'd1_softbit_recovery_ok_count', 'd3_softbit_recovery_ok_count', 'd1_softbit_recovery_fail_count', 'd3_softbit_recovery_fail_count',
                'd1_raid_recovery_ok_count', 'd3_raid_recovery_ok_count', 'd1_raid_recovery_fail_count', 'd3_raid_recovery_fail_count',
                'raid_q_err_over_thres_count', 'empty_page_cnt_caused_by_prog_fail', 'd1_safe_scan_exec_cnt', 'd3_safe_scan_exec_cnt', 'pa_total_err_cnt',
                'dl_total_err_cnt', 'nl_total_err_cnt', 'tl_total_err_cnt', 'err_map', 'bad_phy_sym_cnt', 'nac_cnt', 'tc_replay_to_cnt', 'afc_req_to_cnt',
                'fc_pro_to_cnt', 'crc_cnt', 'rx_buf_overflow_cnt', 'wr_seq_num_cnt', 'frame_syntax_err_cnt', 'pa_init_err_cnt', 'pa_init_from_remote',
                'pa_init_from_local', 'link_lost_cnt', 'link_fail_cnt', 'pwr_chg_fail_cnt', 'error_fifo_0', 'error_fifo_1', 'd1_read_later_bb_cnt',
                'd3_read_later_bb_cnt', 'total_early_bb_cnt', 'total_later_bb_cnt', 'total_prog_vb_list_count', 'total_prog_split_count',
                'feh_sb_read_htllr_tbl_fail_cnt', 'feh_sb_htllr_recovery_ok_cnt', 'feh_sb_default_decode_fail_cnt', 'feh_sb_default_decode_ok_cnt',
                'feh_sb_option_adt_hb_decode_fail_cnt', 'feh_sb_option_ldpc_decode_fail_cnt', 'read_ECC_over_cnt', 'empty_page_test_cnt_C41',
                'empty_page_test_cnt_C35', 'd1_initial_read_fail_count', 'd3_initial_read_fail_count', 'd1_read_retry_step_count', 'd3_read_retry_step_count',
                'write_protect', 'l2_refresh_open_win_uecc_count', 'wl_info', 'fw_code_update_count', 'auto_idle_power_saving_count',
                'dev_sleep_power_saving_count', 'min_temperature', 'max_temperature', 'ts_level_1_cnt', 'ts_level_2_cnt', 'ts_level_3_cnt',
                'ts_speed_control_cnt', 'ts_speed_resume_cnt', 'ts_maximum', 'dvfs_osct_ts_event_cnt_0', 'dvfs_osct_ts_event_cnt_1', 'dvfs_osct_ts_event_cnt_2',
                'dvfs_osct_ts_event_cnt_3', 'dvfs_osct_ts_event_cnt_4', 'dvfs_osct_ts_event_cnt_5', 'dvfs_osct_bc_event_cnt_0', 'dvfs_osct_bc_event_cnt_1',
                'dvfs_osct_bc_event_cnt_2', 'dvfs_osct_bc_event_cnt_3', 'dvfs_osct_bc_event_cnt_4', 'dvfs_osct_bc_event_cnt_5', 'power_good_count',
                'power_bad_count', 'auto_standby_count', 'init_spare_block', 'remain_spare_block', 'previous_total_dev_erase_cnt', 'previous_total_d1_erase_cnt',
                'previous_total_d3_erase_cnt', 'l2_prog_fail_cnt', 'l2_prog_fail_only_8k_fail_cnt', 'read_refresh_cnt_0', 'read_refresh_cnt_1',
                'read_refresh_cnt_2', 'read_refresh_cnt_3', 'read_refresh_cnt_4', 'read_refresh_cnt_5', 'read_refresh_cnt_6', 'read_refresh_cnt_7',
                'read_refresh_cnt_8', 'read_refresh_cnt_9', 'read_refresh_cnt_10', 'read_refresh_cnt_11', 'read_refresh_cnt_12', 'read_refresh_cnt_13',
                'read_refresh_cnt_14', 'read_refresh_cnt_15', 'safe_scan_entry_cnt', 'safe_scan_open_entry_cnt', 'safe_scan_pass_cnt', 'safe_scan_fail_cnt',
                'save_readcnt_tbl_trig', 'save_readcnt_tbl_l2_trig', 'max_read_cnt_mode_0', 'max_read_cnt_mode_1', 'refresh_src_0', 'refresh_src_1',
                'refresh_src_2', 'refresh_src_3', 'raid_decode_fail_pca', 'raid_decode_pass_pca', 'raid_decode_pass_lca', 'host_read_fail_lca',
                'host_read_fail_pca', 'l2_refresh_open_win_uecc_pca_0', 'l2_refresh_open_win_uecc_pca_1', 'l2_refresh_open_win_uecc_pca_2',
                'rebuild_tbl_err_cnt_0', 'rebuild_tbl_err_cnt_1', 'rebuild_tbl_err_cnt_2', 'rebuild_tbl_err_cnt_3', 'rebuild_tbl_err_cnt_4',
                'rebuild_tbl_err_cnt_5', 'rebuild_tbl_err_cnt_6', 'rebuild_tbl_err_cnt_7', 'rebuild_tbl_err_cnt_8', 'rebuild_tbl_err_cnt_9',
                'rebuild_tbl_err_cnt_10', 'rebuild_tbl_err_cnt_11', 'rebuild_tbl_err_cnt_12', 'rebuild_tbl_err_cnt_13', 'vdt_vcc_cnt', 'vdt_vccq_cnt'
            ]
            value = self.convert_byte_to_string(byte_array, 0, 56, 8)
            value.extend(self.convert_byte_to_string(byte_array, 56, 72, 4))
            value.extend(self.convert_byte_to_string(byte_array, 72, 76, 2))
            value.extend(self.convert_byte_to_string(byte_array, 76, 216, 4))
            value.extend(self.convert_byte_to_string(byte_array, 216, 220, 2))
            value.extend(self.convert_byte_to_string(byte_array, 220, 512, 4))
            value.extend(self.convert_byte_to_string(byte_array, 512, 560, 8))
            value.extend(self.convert_byte_to_string(byte_array, 560, 568, 2))
            value.extend(self.convert_byte_to_string(byte_array, 568, 660, 4))
            value.extend(self.convert_byte_to_string(byte_array, 660, 684, 2))
            value.extend(self.convert_byte_to_string(byte_array, 684, 704, 4))
            value.extend(self.convert_byte_to_string(byte_array, 704, 712, 2))
            value.extend(self.convert_byte_to_string(byte_array, 712, 720, 4))
            value.extend(self.convert_byte_to_string(byte_array, 720, 724, 2))
            value.extend(self.convert_byte_to_string(byte_array, 724, 768, 4))
            value.extend(self.convert_byte_to_string(byte_array, 768, 770, 1))
            value.extend(self.convert_byte_to_string(byte_array, 770, 772, 2))
            value.extend(self.convert_byte_to_string(byte_array, 772, 784, 4))
            value.extend(self.convert_byte_to_string(byte_array, 784, 824, 2))
            value.extend(self.convert_byte_to_string(byte_array, 824, 848, 8))
            value.extend(self.convert_byte_to_string(byte_array, 848, 852, 2))
            value.extend(self.convert_byte_to_string(byte_array, 852, 876, 8))
            value.extend(self.convert_byte_to_string(byte_array, 876, 884, 4))
            value.extend(self.convert_byte_to_string(byte_array, 884, 916, 2))
            value.extend(self.convert_byte_to_string(byte_array, 916, 948, 4))
            value.extend(self.convert_byte_to_string(byte_array, 948, 956, 2))
            value.extend(self.convert_byte_to_string(byte_array, 956, 988, 4))
            value.extend(self.convert_byte_to_string(byte_array, 988, 1016, 2))
            value.extend(self.convert_byte_to_string(byte_array, 1016, 1024, 4))

            write_csv_header(readable_smart_info, test_conf["csv_delimiter"].join(header))
            write_csv_result(readable_smart_info, test_conf["csv_delimiter"].join(value))
        tc_logger.info('==>Get smart info over')
        return header, value

    def get_health_report(self, parse=True, result_path=None, _format=None):
        """
        Use SCSI command to generate health report and pull it to test machine, will skip if chip provider is SS
        :param parse: whether to parse the health report into readable content
        :param result_path: health report stored in test machine, like a PC, a RP
        :param _format: health report format
        :return: tuple which contains readable health report
        """
        tc_logger.info('==>Start to check device health')
        if _format is None:
            _format = str(test_conf.get('health_report_format', 'JGSFW12A'))
        value = ["NA"]
        header = ["Health_Report_" + _format]
        if test_conf['chip_manufacturer'] != 'ymtc':
            tc_logger.warning('==>None YMTC chip has no health report!')
            return header, value

        sg3_utils_lib = os.path.join(test_conf['tool']['sg3'], 'lib')
        sg_raw = os.path.join(test_conf['tool']['sg3'], 'bin', 'sg_raw')
        password = os.path.join(test_conf['tool']['sg3'], 'passwords', _format + '.bin')

        health_report_name = 'health_report'
        all_health_report = os.path.join(test_conf['tool']['dir'], health_report_name + '*')
        health_report_path = os.path.join(test_conf['tool']['dir'], health_report_name + '.bin')
        if result_path is None:
            cur_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            _health_report_name = 'health_report_' + cur_time + '.bin'
            result_path = os.path.join(test_conf['monitor_home'], _health_report_name)


        if _format in ["JGSFW12A", "JGSFW12B", "TASFW", "JGSFW101"]:
            rm_cmd = 'shell "rm -f {}"'.format(all_health_report)
            gen_cmd = 'shell "export LD_LIBRARY_PATH={0};' \
                      '{1} -s 0x2c --infile={2} /dev/block/sda 3b e1 00 00 00 00 00 00 2c 00 -v;' \
                      '{3} -r 4096 /dev/block/sda 3c c1 00 00 00 00 00 10 00 00 -v --outfile={4}"'\
                .format(sg3_utils_lib, sg_raw, password, sg_raw, health_report_path)
            save_cmd = "pull {} {}".format(health_report_path, result_path)
            self.adb.execute_adb_command(rm_cmd)
            self.adb.execute_adb_command(gen_cmd)
            self.adb.execute_adb_command(save_cmd)
            self.adb.execute_adb_command(rm_cmd)

        if parse is True and _format == 'JGSFW12A':
            with open(result_path, "rb") as f:
                byte_array = f.read()
            header = [
                "VDT_Vccq",
                "VDT_Vcc",
                "current_temp_NAND0",
                "current_temp_NAND1",
                "current_temp_NAND2",
                "current_temp_NAND3",
                "current_temp_NAND4",
                "current_temp_NAND5",
                "current_temp_NAND6",
                "current_temp_NAND7",
                "current_temp_CTRL",
                "min_NAND_temp",
                "max_NAND_temp",
                "SLC_read_retry_fail_count",
                "TLC_read_retry_fail_count",
                "SLC_read_retry_success_count",
                "TLC_read_retry_success_count",
                "CRTL_temp_85C_times",
                "CRTL_temp_125C_times",
                "min_ec_slc",
                "max_ec_slc",
                "avg_ec_slc",
                "min_ec_tlc",
                "max_ec_tlc",
                "avg_ec_tlc",
                "cum_host_read",
                "cum_host_write",
                "cum_ini_cnt",
                "waf"
            ]
            value = [
                str(int.from_bytes(byte_array[44:48], "big")),
                str(int.from_bytes(byte_array[48:52], "big")),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[108:112], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[112:116], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[116:120], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[120:124], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[124:128], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[128:132], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[132:136], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[136:140], "big")) * 1.15),
                '%.2f' % ((int.from_bytes(byte_array[140:144], "big") & 0x3ff) / 4
                          if (int.from_bytes(byte_array[140:144], "big") & 0x400) == 0
                          else (int.from_bytes(byte_array[140:144], "big") & 0x3ff) / -4),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[144:148], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[148:152], "big")) * 1.15),
                str(int.from_bytes(byte_array[188:192], "big")),
                str(int.from_bytes(byte_array[192:196], "big")),
                str(int.from_bytes(byte_array[196:200], "big")),
                str(int.from_bytes(byte_array[200:204], "big")),
                str(int.from_bytes(byte_array[428:432], "big")),
                str(int.from_bytes(byte_array[432:436], "big")),
                str(int.from_bytes(byte_array[68:72], "big")),
                str(int.from_bytes(byte_array[72:76], "big")),
                str(int.from_bytes(byte_array[76:80], "big")),
                str(int.from_bytes(byte_array[80:84], "big")),
                str(int.from_bytes(byte_array[84:88], "big")),
                str(int.from_bytes(byte_array[88:92], "big")),
                str(int.from_bytes(byte_array[92:96], "big")),
                str(int.from_bytes(byte_array[96:100], "big")),
                str(int.from_bytes(byte_array[100:104], "big")),
                str(int.from_bytes(byte_array[104:108], "big"))
            ]
        elif parse is True and _format == "JGSFW12B":
            with open(result_path, "rb") as f:
                byte_array = f.read()
            header = [
                "max_NAND_temp",
                "min_NAND_temp",
                "current_temp_CTRL"
            ]
            value = [
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[92:96], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[96:100], "big")) * 1.15),
                '%.2f' % ((int.from_bytes(byte_array[100:104], "big") & 0x3ff) / 4
                          if (int.from_bytes(byte_array[100:104], "big") & 0x400) == 0
                          else (int.from_bytes(byte_array[100:104], "big") & 0x3ff) / -4)
            ]
        elif parse is True and _format in ["TASFW", "JGSFW101"]:
            with open(result_path, "rb") as f:
                byte_array = f.read()
            header = [
                "current_temp_NAND0",
                "current_temp_NAND1",
                "current_temp_NAND2",
                "current_temp_NAND3",
                "current_temp_NAND4",
                "current_temp_NAND5",
                "current_temp_NAND6",
                "current_temp_NAND7",
                "current_temp_CTRL",
                "min_NAND_temp",
                "max_NAND_temp",
                "CRTL_temp_85C_times",
                "CRTL_temp_125C_times",
                "min_ec_slc",
                "max_ec_slc",
                "avg_ec_slc",
                "min_ec_tlc",
                "max_ec_tlc",
                "avg_ec_tlc",
                "cum_host_read",
                "cum_host_write",
                "cum_ini_cnt",
                "waf"
                      ]
            value = [
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[132:136], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[136:140], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[140:144], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[144:148], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[148:152], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[152:156], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[156:160], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[160:164], "big")) * 1.15),
                '%.2f' % ((int.from_bytes(byte_array[164:168], "big") & 0x3ff) / 4
                          if (int.from_bytes(byte_array[164:168], "big") & 0x400) == 0
                          else (int.from_bytes(byte_array[164:168], "big") & 0x3ff) / -4),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[168:172], "big")) * 1.15),
                '%.2f' % (85 - (111 - int.from_bytes(byte_array[172:176], "big")) * 1.15),
                str(int.from_bytes(byte_array[476:480], "big")),
                str(int.from_bytes(byte_array[480:482], "big")),
                str(int.from_bytes(byte_array[92:96], "big")),
                str(int.from_bytes(byte_array[96:100], "big")),
                str(int.from_bytes(byte_array[100:104], "big")),
                str(int.from_bytes(byte_array[104:108], "big")),
                str(int.from_bytes(byte_array[108:112], "big")),
                str(int.from_bytes(byte_array[112:116], "big")),
                str(int.from_bytes(byte_array[116:120], "big")),
                str(int.from_bytes(byte_array[120:124], "big")),
                str(int.from_bytes(byte_array[124:128], "big")),
                str(int.from_bytes(byte_array[128:132], "big"))
            ]
        tc_logger.info('==>Check device health over')
        return header, value

    def get_wb_flush_status(self):
        """
        Get wb avail buf flush status from device
        :return: int
        """
        flush_status = -1
        device_type = self.check_device_type()
        if device_type:
            if device_type == 'mi10':
                base = 16
                flush_status_path = test_conf['mi10']['attributes']['flush_status']
            else:
                base = 10
                key = 'hikey960' if device_type in ['hikey960', '960'] else 'hikey970'
                flush_status_path = test_conf[key]['wb']['flush_status']
            cmd = 'shell "cat {}"'.format(flush_status_path)
            _flush_status = self.adb.execute_adb_command(cmd).strip()
            if ':' in _flush_status:
                _flush_status = _flush_status.split(':')[1].strip()
            flush_status = int(_flush_status, base)
        return flush_status

    def verify_adb_connection(self, timeout=60):
        tc_logger.info('Start to verify adb connection')
        start_time = time.time()
        while True:
            if os.system('adb devices | grep {} | grep device'.format(self.device)) == 0:
                end_time = time.time()
                duration = end_time - start_time
                tc_logger.info('Verify adb connection over, cost {} seconds'.format(str(duration)))
                return duration
            else:
                end_time = time.time()
                if (end_time - start_time) > timeout:
                    tc_logger.error("Verify adb connection Timeout - {} seconds".format(str(timeout)))
                    return -1
            time.sleep(1)

    def verify_hdmi_connection(self, timeout=60):
        tc_logger.info("Start to verify hdmi connection")
        start_time = time.time()
        if self.verify_adb_connection(timeout) != -1:
            hdmi_kw_list = [
                "com.android.launcher3",
                "com.miui.home"
            ]
            while True:
                for hdmi_kw in hdmi_kw_list:
                    if os.system("adb -s {} shell dumpsys window displays | grep {}".format(self.device, hdmi_kw)) == 0:
                        end_time = time.time()
                        duration = end_time - start_time
                        tc_logger.info("Verify hdmi connection over, cost {} seconds".format(str(duration)))
                        return duration
                end_time = time.time()
                if (end_time - start_time) > timeout:
                    tc_logger.error("Verify hdmi connection Timeout - {} seconds".format(str(timeout)))
                    return -1
                time.sleep(1)
        else:
            return -1

    # region Assistant methods as below
    def flush_wb_avail_buf(self):
        """
        Flush wb avail buf
        :return: NOne
        """
        device_type = self.check_device_type()
        if device_type:
            flush_path = test_conf[device_type]['wb']['flush']
            cmd = 'shell "echo 1 > {}"'.format(flush_path)
            self.adb.execute_adb_command(cmd, print_stdout=False)

    @staticmethod
    def get_readable_wb_buf(number, _hex=False, percentage=False):
        """
        Convert string to a readable storage value
        :param number: numeric string
        :param _hex: indicate whether the number is hex
        :param percentage: true means to convert the calculated value a percentage string
        :return: string
        """
        wb_buf = number
        if _hex:
            wb_buf = int(wb_buf, 16)
        if percentage:
            wb_buf = str(int(wb_buf) * 10) + '%'
        else:
            wb_buf = str(int(wb_buf * 4 / 1024)) + 'G'
            # wb_buf = convert_storage_unit(wb_buf)
        return wb_buf

    def check_device_type(self, target_device=None, action='action'):
        """
        Check whether device is valid, return False when device is invalid, return lower device type when device is valid
        :param target_device: expected device type, can be string or list
        :param action: the action you will take when device type is valid
        :return: False or device type
        """
        stack = inspect.stack()
        caller = stack[1].function
        if '_' in caller:
            action = caller.replace('_', ' ')
        device_type = test_conf.get('device_type', None)
        if device_type is None:
            result = False
            tc_logger.warning('No device type, skip {}!'.format(action))
        else:
            _device_type = device_type.lower()
            if _device_type not in self.support_device:
                result = False
                tc_logger.warning('Unsupported device, skip {}!'.format(action))
            else:
                result = _device_type
                if target_device is not None:
                    if isinstance(target_device, str):
                        target_device = [target_device.lower()]
                    if isinstance(target_device, list):
                        target_device = [value.lower() for value in target_device]
                    if _device_type not in target_device:
                        result = False
                        tc_logger.warning('Unmatched device, skip {}!'.format(action))
        return result

    @staticmethod
    def convert_byte_to_string(byte_array, start, end, step):
        values = list()
        while start < end:
            value = str(int.from_bytes(byte_array[start:start + step], 'little'))
            values.append(value)
            start += step
        return values
    # endregion

    def check_ffu(self):
        """
        :HUIZI
        in FFU test use check ffu status and revision
        :return: tuple
        """
        result = ['None']*2
        header = ['FFU_status','Revision']
        device_type = self.check_device_type()
        if device_type:
            ffu_status_path = test_conf[device_type]['attributes']['ffu_status']
            product_revision_path = test_conf[device_type]['string_descriptors']['product_revision']
            ffu_status_cmd = 'shell "cat {}"'.format(ffu_status_path)
            product_revision_cmd = 'shell "cat {}"'.format(product_revision_path)
            ffu_status = self.adb.execute_adb_command(ffu_status_cmd)
            product_revision = self.adb.execute_adb_command(product_revision_cmd)
            result[0] = ffu_status
            result[1] = product_revision
        return header, result

    def push_bin_action(self):
        """
        :HUIZI
        :FFU Upgrade push bin to /data
        :return: None
        """
        bin_name = test_conf.get("bin_name", None)
        bin_path = os.path.join(test_conf.get('bin_path', test_conf["ffu_fw_home"]))
        ffu_bin_home = os.path.join(bin_path + '/' + bin_name)
        self.adb.execute_adb_command("shell rm -f /data/{}".format(bin_name))
        cmd = 'push {} {}'.format(ffu_bin_home, '/data')
        self.adb.execute_adb_command(cmd)

    def file_for_assistant_test(self, rw=None, rwmixread=None, bs=None, size=None, runtime=None, time_based=None, fio_fg=None, reporting_mode=None):
        """
        USE for write fio file for test
        :HUIZI
        :param: rw: fio run mode eg: read/write/randread/randwrite
        :param: rwmixread: for mix rw/randrw read percentage
        :param: bs: test block size: eg 4k
        :param: size: file size eg: 1g
        :param: runtime: fio runtime eg: 60(seconds)
        :param: time_based: set this will finish the set time
        :param: fio_fg : fio run in foreground process ,default is True
        :param: reporting_mode ,record bw or iops log if set
        :return: None
        """
        if rw is None:
            rw = test_conf.get("rw", "read")
        if rwmixread is None:
            rwmixread = test_conf.get('rwmixread', None)
        if bs is None:
            bs = test_conf.get('bs', '4k')
        if size is None:
            size = test_conf.get('size', '1g')
        if runtime is None:
            runtime = int(test_conf.get('runtime', 600))
        if rw in ["randrw", "rw"]:
            rw = rw + " --rwmixread=" + rwmixread
        if time_based is None:
            time_based = int(test_conf.get('time_based', 1))
        if fio_fg is None:
            fio_fg = test_conf.get('fio_fg', True)
        fio_fg = unify_bool_value(fio_fg)
        if reporting_mode is None:
            reporting_mode = test_conf.get('reporting_mode', 'iops')
        tc_logger.info('===>Start to write a {} fio_file for assistant test!'.format(size))
        rand_file = str(datetime.now().strftime("%Y-%m-%d-%H_%M_%S"))
        fio_command ="adb -s {0} shell '{1} --direct=1 --norandommap=0 --numjobs=1 --ioengine=libaio --iodepth=32" \
                     " --rw={2} --bs={3} --size={4} --runtime={5} --output-format=normal --name=job1 " \
                     "--filename=/data/fio_{6}_{7}' ".format(self.device, test_conf['tool']['fio'], rw,
                                                             bs, size, runtime, size, rand_file)
        if not fio_fg:
            fio_command = "adb -s {0} shell 'cd /data;nohup {1} --direct=1 --thread=1 --norandommap=1 --numjobs=1 " \
                          "--ioengine=libaio --iodepth=32 --rw={2} " \
                    "--bs={3} --size={4} --runtime={5} --time_based={6} " \
                    "--name=job --filename=/data/fio_{7}_{8} --randrepeat=0 --output-format=normal --group_reporting --log_avg_msec=500 " \
                          "--{9}avgtime=500 --write_{10}_log={11}_file{12} >> /data/fio_rpt_stdout 2>&1 &' "\
                .format(self.device, test_conf['tool']['fio'], rw, bs, size, runtime, time_based, size, rand_file, reporting_mode.lower(), reporting_mode.lower(), size, rand_file)
            tc_logger.info("===>start run fio process in background!!! ")
        subprocess.Popen(fio_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

    def space_decrease_chart(self):
        """
        :HUZI
        :USE FOR Performance data space decrease chart
        :return: None
        :return:
        """
        result_path = os.path.join(test_conf["result_home"]) if "result_home" in test_conf else "/tmp"
        chart_path = os.path.join(os.path.join(test_conf["result_home"], 'chart'))
        df1 = pd.read_csv(os.path.join(result_path, 'data_avail_space.csv'))
        df2 = pd.read_csv(os.path.join(result_path, 'fio_rpt.csv'))
        column_header = list(df2.columns.values)
        name = ['Read (MB/s)', 'Read IOPS', 'Write (MB/s)', 'Write IOPS']
        name_list = []
        for i in column_header:
            if i in name:
                name_list.append(i)
        length = len(name_list)
        for l in range(length):
            data_value_l = df2[name_list[l]]
            df1[name_list[l]] = data_value_l
            df1.to_csv(os.path.join(result_path, 'result_summary.csv'), index=False, header=name_list[l])
        # contact result_summary and parse smartlog(pre_loop and after_loop)
        smart_file = os.path.join(result_path, "smart_info.csv")
        sum_file = os.path.join(result_path, "result_summary.csv")
        df_sum = pd.read_csv(sum_file)
        sm_df = pd.read_csv(smart_file)
        wl_cn = sm_df["wl_trigger_count"].values
        wl_cn_pre = wl_cn[0::2]
        wl_cn_post = wl_cn[1::2]
        wl_df = {"wl_cnt_pre": wl_cn_pre, "wl_cnt_post": wl_cn_post}
        wl_frame = pd.DataFrame(wl_df)
        df = pd.concat([df_sum, wl_frame], axis=1)
        df.to_csv(sum_file, index=False, header=True)
        # ####chart#####
        df4 = pd.read_csv(os.path.join(result_path, 'result_summary.csv'))
        x1 = df4['Data_Space']
        x2 = df4['Wb_Cur_Buf']
        y1 = df4['Read (MB/s)']
        y2 = df4['Write (MB/s)']
        parameters = {'xtick.labelsize': 5, 'ytick.labelsize': 10, 'axes.labelsize': 12}
        mpl.rcParams.update(parameters)
        mpl.rcParams['figure.figsize'] = (12.0, 8.0)
        mpl.rcParams['savefig.dpi'] = 200
        for x in x1, x2:
            plt.title('ThroughPut Chart', fontsize='15')
            plt.plot(x, y1, label='Read (MB/s)', color='r', marker='.')
            plt.plot(x, y2, label='Write (MB/s)', color='b', marker='.')
            plt.ylabel('Throughput MB/s')
            plt.legend(['Read (MB/s)', 'Write (MB/s)', ])
            plt.xticks(rotation=90)
            if x is x1:
                plt.xlabel('Data_avail_space')
                plt.tight_layout()
                plt.savefig(os.path.join(chart_path, 'Data_Avail_Space.png'), dpi=200)
            else:
                plt.xlabel('WB_Cur_buf')
                plt.tight_layout()
                plt.savefig(os.path.join(chart_path, 'WB_Cur_Buf.png'), dpi=200)
            plt.close()

    def statistic_with_chart(self, result_path=None, reporting_mode=None, test_mode=None, rw=None, rwmixread=None):
        """
        :For FFU upgrade
        :HUIZI
        :param result_path: result store path
        :param reporting_mode: --write_bw_log, record mode
        :param test_mode: fio sequential or random mode
        :param rw: parameter rw of fio
        :param rwmixread: parameter rwmixread of fio
        :return: None
        """
        if result_path is None:
            result_path = os.path.join(test_conf["result_home"]) if "result_home" in test_conf else "/tmp"
        if reporting_mode is None:
            reporting_mode = test_conf.get('reporting_mode', 'iops')
        if test_mode is None:
            test_mode = test_conf.get('test_mode', 'seq')
        if rw is None:
            rw = test_conf.get("rw", "read")
        if rwmixread is None:
            rwmixread = test_conf.get('rwmixread', None)
        if rw in ["randrw", "rw"]:
            rw = rw + " --rwmixread=" + rwmixread
        strf_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        strf_path = os.path.join(test_conf["result_home"], strf_name)
        os.system("mkdir {}".format(strf_path))
        cmd1 = "shell 'cd /data;mv *{}* fio_{}_{}.txt'".format(reporting_mode.lower(), test_mode, reporting_mode)
        self.adb.execute_adb_command(cmd1)
        save_cmd1 = "pull /data/fio_{}_{}.txt {}".format(test_mode, reporting_mode, result_path)
        save_cmd2 = "pull /data/fio_rpt_stdout {}".format(result_path)
        cmd_list = [save_cmd2]
        cmd_list.append(save_cmd1)
        for cmd in cmd_list:
            self.adb.execute_adb_command(cmd)
        txt_path = []
        loc = os.path.join(result_path, 'fio_{}_{}.txt').format(test_mode, reporting_mode)
        txt_path.append(loc)
        # parse mix log
        if rwmixread:
            mix_read = np.loadtxt(loc, delimiter=',', dtype='int', unpack=False)[0::2]
            mix_write = np.loadtxt(loc, delimiter=',', dtype='int', unpack=False)[1::2]
            read_path = os.path.join(result_path, 'fio_mix_read.txt')
            write_path = os.path.join(result_path, 'fio_mix_write.txt')
            np.savetxt(read_path, mix_read, delimiter=',', fmt='%d')
            np.savetxt(write_path, mix_write, delimiter=',', fmt='%d')
            for i in read_path, write_path:
                txt_path.append(i)
        _txt_path = txt_path
        for l in _txt_path:
            f_name = os.path.splitext(l)[0].split('/')[-1]
            parameters = {'xtick.labelsize': 10, 'ytick.labelsize': 10, 'axes.labelsize': 12}
            mpl.rcParams.update(parameters)
            mpl.rcParams['figure.figsize'] = (12.0, 8.0)
            mpl.rcParams['savefig.dpi'] = 200
            x, y, z, v = np.loadtxt(l, delimiter=',', dtype='int', unpack=True)
            plt.plot(x, y, linestyle='--', marker='.', label=rw, color='red')
            plt.xlabel('time_msec')
            plt.ylabel(reporting_mode.upper())
            plt.title(reporting_mode.upper() + ' Graphy', fontsize=15)
            plt.legend()
            plt.grid()
            plt.plot(x, y)
            plt.savefig(os.path.join(os.path.join(test_conf["result_home"], 'chart'), '{}_{}.png').format(f_name, strf_name), dpi=100)
            plt.close()
            data = pd.read_table(l, sep=',', header=None)
            data.to_csv(os.path.join(result_path, '{}_data.csv').format(f_name), index=None)
            value = pd.read_csv(os.path.join(result_path, '{}_data.csv').format(f_name), usecols=[0, 1])
            _reporting_mode = reporting_mode.upper()
            if reporting_mode == 'bw':
                _reporting_mode = ''.join([reporting_mode.upper(), '(KB)'])
            value_mesc = value['0']
            _value = value['1']
            value['Time(msec)'] = value_mesc
            value[_reporting_mode] = _value
            statistic = "{}_statistic.csv".format(f_name)
            value.to_csv(os.path.join(result_path, statistic), index=False, columns=['Time(msec)', _reporting_mode])
        res_fio_path = os.path.join(test_conf["result_home"], 'fio_*')
        os.system("mv -f {} {}".format(res_fio_path, strf_path))
        # get fio stdnt error value
        err_csv = os.path.join(result_path, 'stdout_err.csv')
        ss = os.popen('cat {} |grep "err="'.format(os.path.join(strf_path, 'fio_rpt_stdout'))).read().strip('\n').split(':')[2]
        key = ss.split()[0].strip().replace('=', '')
        _value = ss.split()[1:]
        value = "".join(_value)
        data_dic = {'Stdout': [key], 'Value': [value]}
        df = pd.DataFrame(data_dic)
        if not os.path.exists(err_csv):
            df.to_csv(err_csv, mode='a', index=False, header=True, )
        else:
            df.to_csv(err_csv, mode='a', index=False, header=False)

    def get_fio_pid(self):
        """
        use for fio background get process pid
        :HUIZI
        :return: tuple
        """
        result = []
        header = ['FIO_PID']
        pid_cmd ='ps -ef |grep ioengine |grep -v grep'
        pid_len = len(os.popen('adb -s {} shell '.format(self.device) + pid_cmd).readlines())
        if pid_len == 0:
            result.append(pid_len)
            tc_logger.info("===> No Fio Search Process!")
        elif pid_len == 1:
            pid1 = os.popen('adb -s {} shell '.format(self.device) + pid_cmd).readline().strip().split()[1]
            result.append(pid1)
        else:
            tc_logger.warning('===> More than 1 fio process ,unexpected!')
        return header, result

    def wb_avail_buf_restore_loop_check(self, sleep_interval=2, restore_timeout=240):
        """
        USE for every loop check_avail_buf make restore wb buf until 100%
        :param: sleep_interval, restore sleep interval time,second int
        :param: restore_timeout, second int
        :HUIZI
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('=======>Start to get wb avail buf')
            start_time = time.time()
            while True:
                if device_type == 'mi10':
                    wb_avail_buf_cmd = "shell 'cat {}'".format(test_conf[device_type]['attributes']['avail_buf'])
                    wb_cur_buf_cmd = "shell 'cat {}'".format(test_conf[device_type]['attributes']['cur_buf'])
                    wb_flush_status_cmd = "shell 'cat {}'".format(test_conf[device_type]['attributes']['flush_status'])
                    wb_avail_buf = self.adb.execute_adb_command(wb_avail_buf_cmd)
                    wb_cur_buf = self.adb.execute_adb_command(wb_cur_buf_cmd)
                    wb_flush_status = self.adb.execute_adb_command(wb_flush_status_cmd)
                    if wb_avail_buf == '0x0000000A':
                        if wb_flush_status == '0x00000003' or wb_flush_status == '0x00000000':
                            tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                            tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                            tc_logger.info("=======>the wb_cur_buf now is :" + wb_cur_buf)
                            break
                        else:
                            time.sleep(1)
                    else:
                        tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                        tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                        time.sleep(sleep_interval)
                elif device_type == 'hikey970':
                    wb_avail_buf_cmd = "shell 'cat {}'".format(test_conf[device_type]['wb']['avail_buf'])
                    wb_flush_status_cmd = "shell 'cat {}'".format(test_conf[device_type]['wb']['flush_status'])
                    _wb_avail_buf = self.adb.execute_adb_command(wb_avail_buf_cmd)
                    _wb_flush_status = self.adb.execute_adb_command(wb_flush_status_cmd)
                    wb_avail_buf = re.findall(r"\d+", _wb_avail_buf)[0]
                    wb_flush_status = re.findall(r"\d+", _wb_flush_status)[0]
                    if int(wb_avail_buf) == 10:
                        if int(wb_flush_status) == 3 or int(wb_flush_status) == 0:
                            tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                            tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                            break
                        else:
                            time.sleep(1)
                    else:
                        tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                        tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                        time.sleep(sleep_interval)
                end_whi_time = time.time()
                if int(end_whi_time - start_time) >= restore_timeout:
                    raise Exception('=======>the restore has timeout {} s ,restore fail!!'.format(restore_timeout))
                else:
                    pass
            end_time = time.time()
            time.sleep(2)
            tc_logger.info('=======>the restore time is {} second'.format(end_time - start_time))

    def wb_avail_buf_restore_loop_check_no_enough(self, sleep_interval=2, restore_timeout=240, expect_avail_buf=9):
        """
        USE for every loop check_avail_buf make restore less 90%
        :param sleep_interval, restore sleep interval time,second int
        :param restore_timeout, second int
        :param expect_avail_buf ,expect restore to 9 ,8 mean 90%, 80%
        :HUIZI
        :return: None
        """
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('=======>Start to get wb avail buf')
            start_time = time.time()
            while True:
                if device_type == 'mi10':
                    wb_avail_buf_cmd = "shell 'cat {}'".format(test_conf[device_type]['attributes']['avail_buf'])
                    wb_flush_status_cmd = "shell 'cat {}'".format(test_conf[device_type]['attributes']['flush_status'])
                    wb_avail_buf = self.adb.execute_adb_command(wb_avail_buf_cmd)
                    wb_flush_status = self.adb.execute_adb_command(wb_flush_status_cmd)
                    if int(wb_avail_buf, 16) >= expect_avail_buf:
                        tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                        tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                        break
                    else:
                        tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                        tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                        time.sleep(sleep_interval)
                elif device_type == 'hikey970':
                    wb_avail_buf_cmd = "shell 'cat {}'".format(test_conf[device_type]['wb']['avail_buf'])
                    wb_flush_status_cmd = "shell 'cat {}'".format(test_conf[device_type]['wb']['flush_status'])
                    _wb_avail_buf = self.adb.execute_adb_command(wb_avail_buf_cmd)
                    _wb_flush_status = self.adb.execute_adb_command(wb_flush_status_cmd)
                    wb_avail_buf = re.findall(r"\d+", _wb_avail_buf)[0]
                    wb_flush_status = re.findall(r"\d+", _wb_flush_status)[0]
                    if int(wb_avail_buf) >= expect_avail_buf:
                        tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                        tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                        break
                    else:
                        tc_logger.info("the wb_avail buf now is :" + wb_avail_buf)
                        tc_logger.info("the wb_flush_status now is :" + wb_flush_status)
                        time.sleep(sleep_interval)
                end_whi_time = time.time()
                if int(end_whi_time - start_time) >= restore_timeout:
                    raise Exception('=======>the restore has timeout {} s ,restore fail!!'.format(restore_timeout))
                else:
                    pass
            end_time = time.time()
            tc_logger.info('=======>the restore time is {} second'.format(end_time-start_time))

    def get_data_space_and_cur_buf(self, data_avail_space=None,):
        """
        USE for data space decrease performance test for cur buf and data space value check
        :param data_avail_start,before test the devices data avail space ,like 218G
        :param data_avail_space ,the data space and wb cur buf CSV path
        :HUIZI
        :return: None
        """
        if data_avail_space is None:
            data_avail_space = os.path.join(test_conf["result_home"],
                                            'data_avail_space') if "result_home" in test_conf else "/tmp/data_avail_space"
        device_type = self.check_device_type()
        if device_type:
            _wb_cur_buf = self.get_wb_cur_buf()[1][0]
            wb_cur_buf = re.findall(r"\d+", _wb_cur_buf)[0]
            if wb_cur_buf != "0":
                self.wb_avail_buf_restore_loop_check()
                time.sleep(5)
            else:
                tc_logger.info("=======>The WB current buf now is {}, WB SLC buf all used!!".format(wb_cur_buf))
                time.sleep(30)
            data_df_cmd = "shell 'df -h |tail -n1'"
            data_avail = self.adb.execute_adb_command(data_df_cmd).split()[3]
            tc_logger.info("=======>the /data avail space now is :{}".format(data_avail))
            wb_cur_af = self.get_wb_cur_buf()[1][0]
            # Bkops status and ee
            dl = {'Data_Space': [data_avail], 'Wb_Cur_Buf': [wb_cur_af]}
            data_list = pd.DataFrame(dl)
            if not os.path.exists(data_avail_space + '.csv'):
                data_list.to_csv(data_avail_space + '.csv', mode='a', index=False, header=True)
            else:
                data_list.to_csv(data_avail_space + '.csv', mode='a', index=False, header=False)

    def check_bkop(self):
        """
        :HUIZI
        :check bkop and ee status
        :return:None
        """
        result = ['NA']*4
        header = ['bkops_enable', 'bkops_status', 'exception_event_control', 'exception_event_status']
        device_type = self.check_device_type()
        flags_list = ['bkops_enable']
        attributes_list = ['bkops_status', 'exception_event_control', 'exception_event_status']
        for flag_check in flags_list:
            bkop_enable_cmd = "shell 'cat {}'".format(test_conf[device_type]['flags'][flag_check])
            result[0] = self.adb.execute_adb_command(bkop_enable_cmd, print_stdout=False)
        for i in range(len(attributes_list)):
            check_cmd = "shell 'cat {}'".format(test_conf[device_type]['attributes'][attributes_list[i]])
            check_value = self.adb.execute_adb_command(check_cmd, print_stdout=False)
            result[i+1] = check_value
        return header, result

    def auto_calculate_loops(self):
        """
        :HUIZI
        :For storage used space increasement by data avail auto calculate loops
        :return: tuple
        """
        result = ['None']
        header = ['Loops']
        file_size = test_conf.get('file_size', None)
        _file_size = re.findall(r'\d+', file_size)[0]
        sub_jobs = test_conf.get('sub_jobs', None)
        file_total_size = int(_file_size) * int(sub_jobs)
        data_df_cmd = "shell 'df -h |tail -n1'"
        data_avail = self.adb.execute_adb_command(data_df_cmd).split()[3]
        data_avail_value = re.findall(r'\d+', data_avail)[0]
        loops = int(data_avail_value) // file_total_size
        result[0] = loops
        return header, result

    def get_adb_status(self):
        """
        :HUIZI
        :get hikey adb connect status
        :return: tuple
        """
        result = ['NA']
        header = ['adb_status']
        device_cmd = "adb devices |grep -v 'List of devices attached'|grep '{}'".format(self.device)
        pid_len = len(os.popen(device_cmd).readlines())
        if pid_len == 0:
            tc_logger.info('==>No search devices, devices disconnect')
            result[0] = 'disconnect'
        elif pid_len == 1:
            device_status = os.popen(device_cmd).readline().strip().split()[1]
            if device_status == 'offline':
                result[0] = 'offline'
            elif device_status == 'device':
                result[0] = 'connect'
        return header, result

    def powerboard_action(self):
        """
        :HUIZI
        :For multi loops reboot hikey devices offline workaround
        :return: None
        """
        device_type = self.check_device_type()
        if device_type == 'mi10':
            time.sleep(60)
        if device_type == 'hikey970':
            pd_path = '/Automation/android-test-program/tools/powerboard'
            pd_py = os.path.join(pd_path, 'ufs_auto.py')
            pd_cmd = 'python3 {} list_pb_sn'.format(pd_py)
            _pd_id = os.popen(pd_cmd).readline().strip('\n')
            pd_id = re.findall(r'\w+', _pd_id)[0]
            pd_cmd_list = ['powerdown', 'powerup']
            power_count = 0
            while power_count < 3:
                time.sleep(70)
                adb_status = self.get_adb_status()[1][0]
                tc_logger.info('==>The adb status is :{}'.format(adb_status))
                if adb_status == 'connect':
                    break
                else:
                    tc_logger.info("==>Now do powerdown and powerup action")
                    for cmd in pd_cmd_list:
                        action_cmd = 'python3 {} {} {}'.format(pd_py, cmd, pd_id)
                        subprocess.Popen(action_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
                        time.sleep(3)
                    power_count += 1
            if power_count >= 3:
                raise Exception('==>After 3 powerdown and powerup adb still disconnect!')

    def ab_stress_debug_action(self, expect_sr=1400, result_path=None):
        """
        :HUIZI
        :param expect_sr: you expect SR values,
        :param result_path: the AB csv exsit path
        :return:
        """
        if result_path is None:
            result_path = os.path.join(test_conf["result_home"]) if "result_home" in test_conf else "/tmp"
        ab_file = os.path.join(result_path, "androbench_result.csv")
        df = pd.read_csv(ab_file)
        df_sr = df['Sequential Read(MB/s)'].values.tolist()
        df_value = df_sr[-1]
        tc_logger.info("==> Current loop SR is {} MB/s".format(df_value))
        if df_value > int(expect_sr):
            pass
        else:
            tc_logger.warning("==>The AB SR is reach threshold ,now is {} Mb/s".format(df_value))
            raise Exception("The Perf is low, test will exception and stop")

    def get_host_manufacturer(self):
        """
        Check host manufacturer

        return: string/None
        """
        result = ['N/A']
        header = ['host_manufacturer']
        tc_logger.info('==>Detecting host manufacturer')
        output = self.adb.execute_adb_command('shell getprop ro.product.manufacturer').lower()
        if output == 'xiaomi':
            manufacturer = 'Mi10'
        elif output == 'unknown':
            manufacturer = 'Hikey970'
        else:
            manufacturer = None
        result[0] = manufacturer
        tc_logger.info('==>Host manufacturer is {}'.format(manufacturer))
        return header, result

    def get_chip_manufacturer(self):
        """
        Check host manufacturer, this is not supported in Hikey960

        return: string/None
        """
        result = ['N/A']
        header = ['chip_manufacturer']
        tc_logger.info('==>Detecting chip manufacturer')
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            path = test_conf[device_type]['string_descriptors']['manufacturer']
            cmd = 'shell "cat {}"'.format(path)
            manufacturer = None
            try:
                output = self.adb.execute_adb_command(cmd).lower()
                if 'ymtc' in output:
                    manufacturer = 'ymtc'
                elif 'ss' in output:
                    manufacturer = 'ss'
                tc_logger.info('==>Chip manufacturer is {}'.format(str(manufacturer)))
            except:
                tc_logger.warning('==>Maybe an unroot device!')
            result[0] = manufacturer
        return header, result

    def check_hpb_version(self):
        """
        Check current hpb version, this is not supported in Hikey960

        return: tuple
        """
        result = ['N/A']
        header = ['hpb_version']
        device_type = self.check_device_type(['mi10', 'hikey970'])
        if device_type:
            tc_logger.info('==>Start to check HPB version')
            switch = test_conf[device_type]['hpb']['hpb_version']
            cmd = 'shell "cat {0}"'.format(switch)
            status = self.adb.execute_adb_command(cmd)
            if device_type == 'mi10':
                hpb_version = status.split('=')[1].strip().split()[0]
            else:
                hpb_version = status.split()[2]
            result[0] = hpb_version
            tc_logger.info('==>Check HPB version over, current is {}'.format(hpb_version))
        return header, result

    def get_chip_capacity(self):
        """
        Check chip capacity

        return: tuple
        """
        result = ['N/A']
        header = ['capacity']
        device_type = self.check_device_type()
        if device_type:
            tc_logger.info('==>Start to get chip capacity')
            _capacity = self.adb.execute_adb_command('shell "df -h  | grep /data"')
            # if device_type == 'mi10':
            #     data_capacity = _capacity.split('\n')[1].split()[1].upper().split('G')[0]
            # else:
            data_capacity = _capacity.split('\n')[0].split()[1].upper().split('G')[0]
            capacity = '256G' if int(data_capacity) >= 200 else '128G'
            result[0] = capacity
            tc_logger.info('==>Check chip capacity over, current is {}'.format(capacity))
        return header, result

    # wb add by kelly
    def enable_tw(self, switch=True, max_try=300):
        """
        Open WB but close flush and h8 mode
        :param max_try: max execution times
        :param switch: True means enable flush, False means disable flush
        :return: None
        """
        device_type = test_conf.get('device_type', 'None')
        if device_type.lower() == 'mi10':
            tw_enable_path = test_conf['mi10']['wb']['tw_enable']
            cat_cmd = ['shell "cat {}"'.format(tw_enable_path)]
            echo_cmd = ['shell "echo 1 > {}"'.format(tw_enable_path), 'shell "echo 0 > {}"'.format(tw_enable_path)]
            status = int(self.adb.execute_adb_command(cat_cmd[0]))
            if switch == True:
                while status != 1 and max_try > 0:
                    tc_logger.info('==>Start to enable flush')
                    self.adb.execute_adb_command(echo_cmd[0])
                    status = int(self.adb.execute_adb_command(cat_cmd[0]))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Enable write booster failed in command: {}'.format(echo_cmd[0]))
            else:
                while status != 0 and max_try > 0:
                    tc_logger.info('==>Start to enable flush')
                    self.adb.execute_adb_command(echo_cmd[1])
                    status = int(self.adb.execute_adb_command(cat_cmd[0]))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Disable write booster failed in command: {}'.format(echo_cmd[1]))
        else:
            tc_logger.info('==>Start to enable write booster')
            tw_enable_path = test_conf['hikey970']['wb']['tw_enable']
            cat_cmd = ['shell "cat {}"'.format(tw_enable_path)]
            echo_cmd = ['shell "echo 1 > {}"'.format(tw_enable_path), 'shell "echo 0 > {}"'.format(tw_enable_path)]
            result = re.match(r'.*read (\d).*', self.adb.execute_adb_command(cat_cmd[0]))
            status = int(result.group(1))
            if switch == True:
                while status != 1 and max_try > 0:
                    self.adb.execute_adb_command(echo_cmd[0])
                    result = re.match(r'.*read (\d).*', self.adb.execute_adb_command(cat_cmd[0]))
                    status = int(result.group(1))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Enable write booster failed in command: {}'.format(echo_cmd[0]))
            else:
                while status != 0 and max_try > 0:
                    self.adb.execute_adb_command(echo_cmd[1])
                    result = re.match(r'.*read (\d).*', self.adb.execute_adb_command(cat_cmd[0]))
                    status = int(result.group(1))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Disable write booster failed in command: {}'.format(echo_cmd[1]))

    def enable_flush(self, switch=True, max_try=300):
        """
        enable flush
        :param max_try: max execution times
        :param switch: True means enable flush, False means disable flush
        :return: None
        """
        device_type = test_conf.get('device_type', 'None')
        if device_type.lower() == 'mi10':
            tw_flush_path = test_conf['mi10']['wb']['flush']
            cat_cmd = ['shell "cat {}"'.format(tw_flush_path)]
            echo_cmd = ['shell "echo 1 > {}"'.format(tw_flush_path), 'shell "echo 0 > {}"'.format(tw_flush_path)]
            status = int(self.adb.execute_adb_command(cat_cmd[0]))
            if switch == True:
                while status != 1 and max_try > 0:
                    tc_logger.info('==>Start to enable flush')
                    self.adb.execute_adb_command(echo_cmd[0])
                    status = int(self.adb.execute_adb_command(cat_cmd[0]))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Enable flush failed in command: {}'.format(echo_cmd[0]))
            else:
                while status != 0 and max_try > 0:
                    tc_logger.info('==>Start to disable flush')
                    self.adb.execute_adb_command(echo_cmd[1])
                    status = int(self.adb.execute_adb_command(cat_cmd[0]))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Disable flush failed in command: {}'.format(echo_cmd[1]))
        else:
            tw_flush_path = test_conf['hikey970']['wb']['flush']
            cat_cmd = ['shell "cat {}"'.format(tw_flush_path)]
            echo_cmd = ['shell "echo 1 > {}"'.format(tw_flush_path), 'shell "echo 0 > {}"'.format(tw_flush_path)]
            result = re.match(r'.*actual enable status (\d).*', self.adb.execute_adb_command(cat_cmd[0]))
            status = int(result.group(1))
            if switch == True:
                while status != 1 and max_try > 0:
                    tc_logger.info('==>Start to enable flush')
                    self.adb.execute_adb_command(echo_cmd[0])
                    result = re.match(r'.*actual enable status (\d).*', self.adb.execute_adb_command(cat_cmd[0]))
                    status = int(result.group(1))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Enable flush failed in command: {}'.format(echo_cmd[0]))
            else:
                while status != 0 and max_try > 0:
                    tc_logger.info('==>Start to disable flush')
                    self.adb.execute_adb_command(echo_cmd[1])
                    result = re.match(r'.*actual enable status (\d).*', self.adb.execute_adb_command(cat_cmd[0]))
                    status = int(result.group(1))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Disable flush failed in command: {}'.format(echo_cmd[1]))

    def enable_hibern(self, switch=True, max_try=300):
        """
        enable hibern flush
        :param max_try: max execution times
        :param switch: True means enable flush, False means disable flush
        :return: None
        """
        device_type = test_conf.get('device_type', 'None')
        if device_type.lower() == 'mi10':
            tw_auto_flush_path = test_conf['mi10']['wb']['hibernate_flush']
            cat_cmd = ['shell "cat {}"'.format(tw_auto_flush_path)]
            echo_cmd = ['shell "echo 1 > {}"'.format(tw_auto_flush_path),
                        'shell "echo 0 > {}"'.format(tw_auto_flush_path)]
            status = int(self.adb.execute_adb_command(cat_cmd[0]))
            if switch == True:
                while status != 1 and max_try > 0:
                    tc_logger.info('==>Start to enable hibern flush')
                    self.adb.execute_adb_command(echo_cmd[0])
                    status = int(self.adb.execute_adb_command(cat_cmd[0]))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Enable hibern flush failed in command: {}'.format(echo_cmd[0]))
            else:
                while status != 0 and max_try > 0:
                    tc_logger.info('==>Start to disable hibern flush')
                    self.adb.execute_adb_command(echo_cmd[1])
                    status = int(self.adb.execute_adb_command(cat_cmd[0]))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Disable hibern flush failed in command: {}'.format(echo_cmd[1]))
        else:
            tc_logger.info('==>Start to enable hibern flush')
            tw_auto_flush_path = test_conf['hikey970']['wb']['hibernate_flush']
            cat_cmd = ['shell "cat {}"'.format(tw_auto_flush_path)]
            echo_cmd = ['shell "echo 1 > {}"'.format(tw_auto_flush_path),
                        'shell "echo 0 > {}"'.format(tw_auto_flush_path)]
            result = re.match(r'TW_flush_during_hibern_enter: (\d)', self.adb.execute_adb_command(cat_cmd[0]))
            status = int(result.group(1))
            if switch == True:
                while status != 1 and max_try > 0:
                    self.adb.execute_adb_command(echo_cmd[0])
                    result = re.match(r'.*TW_flush_during_hibern_enter: (\d)', self.adb.execute_adb_command(cat_cmd[0]))
                    status = int(result.group(1))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Enable hibern flush failed in command: {}'.format(echo_cmd[0]))
            else:
                while status != 0 and max_try > 0:
                    self.adb.execute_adb_command(echo_cmd[1])
                    result = re.match(r'TW_flush_during_hibern_enter: (\d)', self.adb.execute_adb_command(cat_cmd[0]))
                    status = int(result.group(1))
                    max_try -= 1
                if max_try <= 0:
                    raise Exception('Disable hibern flush failed in command: {}'.format(echo_cmd[1]))

    #@pass_fail_common_deco()
    def verify_wb_function(self, expect_buf=0):
        """
        check if wb avail buf is equal expect value
        :param expect_buf: expected wb avail buf, like 100, 90
        :return: None
        """

        device_type = test_conf.get('device_type', 'None')
        if device_type is None:
            tc_logger.warning('No device type, skip restoring wb avail buf!')
        else:
            _device_type = device_type.lower()
            if _device_type not in self.support_device:
                tc_logger.warning('Invalid device, skip restoring avail wb buf!')
            else:
                avail_wb = self.get_wb_avail_buf()[1][0]
                int_avail_wb = int(avail_wb.split('%')[0])
                int_expect_buf = int(expect_buf)
                flag = 0
                if int_avail_wb == int_expect_buf:
                    tc_logger.info('==>Current wb available buf: {} is same with expect_buf is:{}'.format(avail_wb, int_expect_buf))
                elif int_expect_buf - 10 <= int_avail_wb <= int_expect_buf + 10:
                    tc_logger.info('==>Current wb available buf: {} is in range with expect_buf is:{}'.format(avail_wb, int_expect_buf))
                else:
                    flag = 1
                    tc_logger.warning("Case failed at wb_avail_buf:{} is different with expect_buf:{}".format(avail_wb, int_expect_buf))
        return flag

    #@pass_fail_common_deco()
    def pull_avail_buf(self, expect_buf=100, max_try=500):
        """
        check if wb avail buf is equal expect value
        :param expect_buf: expected wb avail buf, like 100, 90
        :return: None
        """

        device_type = test_conf.get('device_type', 'None')
        if device_type is None:
            tc_logger.warning('No device type, skip restoring wb avail buf!')
        else:
            _device_type = device_type.lower()
            if _device_type not in self.support_device:
                tc_logger.warning('Invalid device, skip restoring avail wb buf!')
            else:
                avail_wb = self.get_wb_avail_buf()[1][0]
                int_avail_wb = int(avail_wb.split('%')[0])
                pull_times = 0
                flag = 0
                result = re.match(r'\d+@', str(expect_buf))
                if result != None:
                    expect_buf_list = expect_buf.split('@')
                    int_expect_buf_list = [int(i) for i in expect_buf_list]
                else:
                    int_expect_buf_list = [int(expect_buf)]
                while pull_times < max_try:
                    if int_avail_wb in int_expect_buf_list:
                        break
                    else:
                        sleep(1)
                        avail_wb = self.get_wb_avail_buf()[1][0]
                        int_avail_wb = int(avail_wb.split('%')[0])
                        pull_times += 1
                if pull_times == max_try:
                    flag = 1
                    tc_logger.warning("Case failed at wb_avail_buf can't pull to {}".format(expect_buf))
        return flag

    def get_flush_time(self, expect_buf=100, max_try=1000):
        """
        check if wb avail buf is equal expect value
        :param expect_buf: expected wb avail buf, like 100, 90
        :return: None
        """

        device_type = test_conf.get('device_type', 'None')
        if device_type is None:
            tc_logger.warning('No device type, skip restoring wb avail buf!')
        else:
            _device_type = device_type.lower()
            if _device_type not in self.support_device:
                tc_logger.warning('Invalid device, skip restoring avail wb buf!')
            else:
                flush_status = self.get_wb_flush_status()
                avail_wb = self.get_wb_avail_buf()[1][0]
                int_avail_wb = int(avail_wb.split('%')[0])
                tc_logger.info("Start to pull available buffer to 100%")
                start_time = time.time()
                pull_times = 0
                result = re.match(r'\d+@', str(expect_buf))
                if result != None:
                    expect_buf_list = expect_buf.split('@')
                    int_expect_buf_list = [int(i) for i in expect_buf_list]
                else:
                    int_expect_buf_list = [int(expect_buf)]
                while pull_times < max_try:
                    if int_avail_wb in int_expect_buf_list:
                        end_time = time.time()
                        break
                    else:
                        sleep(1)
                        avail_wb = self.get_wb_avail_buf()[1][0]
                        int_avail_wb = int(avail_wb.split('%')[0])
                        flush_status = self.get_wb_flush_status()
                        pull_times == pull_times + 1
                if pull_times == 1000:
                    raise Exception("Case failed at wb_avail_buf can't pull to {}".format(expect_buf))
                flush_time = end_time - start_time
                tc_logger.info(
                    "available buffer size restore from 0 to expect_buf {},flush time is {} seconds".format(expect_buf,
                                                                                                            flush_time))
                return flush_time

    #@pass_fail_common_deco()
    def get_ee_bkops_status(self, ee_status=True, expect_ee_status="0x00000020", ee_control=True, bkops_status=True, bkops_en=True):
        """
        Check bkops/ee status of Mi10/hikey970
        :return: None
        """
        flag = 0
        device_type = test_conf.get('device_type', 'None')
        if device_type.lower() == 'mi10':
            tc_logger.info('==>Start to check Mi10 bkops/ee status')
            exception_event_status = test_conf['mi10']['attributes']['exception_event_status']
            exception_event_control = test_conf['mi10']['attributes']['exception_event_control']
            bkops_status_path = test_conf['mi10']['attributes']['bkops_status']
            #bkops_enable = test_conf['mi10']['attributes']['bkops_enable']
            cat_cmd = list()
            if unify_bool_value(ee_status):
                cat_cmd.append('shell "cat {}"'.format(exception_event_status))
            if unify_bool_value(ee_control):
                cat_cmd.append('shell "cat {}"'.format(exception_event_control))
            if unify_bool_value(bkops_status):
                cat_cmd.append('shell "cat {}"'.format(bkops_status_path))
            #if unify_bool_value(bkops_en):
                #cat_cmd.append('shell "cat {}"'.format(bkops_enable))
            i = 0
            while i < len(cat_cmd):
                if i == 0:
                    cat_ee_status = self.adb.execute_adb_command(cat_cmd[i])
                    if cat_ee_status != expect_ee_status:
                        flag = 1
                        tc_logger.warning(
                            "ee_status {} is not same as expect_ee_status {}".format(cat_ee_status,
                                                                                     expect_ee_status))
                else:
                    self.adb.execute_adb_command(cat_cmd[i])
                i += 1
            tc_logger.info('==>Open cat bkops/ee over')
        elif device_type.lower() == 'hikey970':
            tc_logger.info('==>Start to check hikey970 bkops/ee status')
            bkops_status_path = test_conf['hikey970']['attributes']['bkops_status']
            exception_event_status = test_conf['hikey970']['attributes']['exception_event_status']
            exception_event_control = test_conf['hikey970']['attributes']['exception_event_control']
            cat_cmd = list()
            if unify_bool_value(ee_status):
                cat_cmd.append('shell "cat {}"'.format(exception_event_status))
            if unify_bool_value(ee_control):
                cat_cmd.append('shell "cat {}"'.format(exception_event_control))
            if unify_bool_value(bkops_status):
                cat_cmd.append('shell "cat {}"'.format(bkops_status_path))
            i = 0
            while i < len(cat_cmd):
                if i == 0:
                    cat_ee_status = self.adb.execute_adb_command(cat_cmd[i])
                    if cat_ee_status != expect_ee_status:
                        flag = 1
                        tc_logger.warning(
                            "ee_status {} is not same as expect_ee_status {}".format(cat_ee_status, expect_ee_status))
                else:
                    self.adb.execute_adb_command(cat_cmd[i])
                i += 1
            tc_logger.info('==>Open cat bkops/ee over')
        return flag


if __name__ == '__main__':
    device = Device('572ce282')
    device.space_decrease_chart()



