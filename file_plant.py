import os
import random
from adb.adb import ADB
from common.assistant import unify_bool_value
from conf.test_conf import tc_logger, test_conf


def create_file_by_iozone(block_size=None, file_size=None, threads=None):
    """
    Create file by iozone, use params from test_conf generally, this method will write file 2 times
    """
    tc_logger.info('==>Start to create file by iozone')
    device_id = test_conf["device_id"]
    exe_file = test_conf['tool']['iozone']
    exe_dir = os.path.dirname(exe_file)
    if block_size is None:
        block_size = test_conf.get('block_size', '4k').lower()
    if file_size is None:
        file_size = test_conf.get('file_size', '128m').lower()
    if threads is None:
        threads = test_conf.get('threads', '8')
    command = 'shell "cd {0};{1} -w -r {2} -s {3} -i 0 -I -t {4}"'.format(exe_dir, exe_file, block_size, file_size, str(threads))

    adb = ADB(device_id)
    adb.execute_adb_command(command)
    tc_logger.info('==>Create file by iozone over')


def read_file_by_fio(block_size=None, file_size=None, rw=None, rwmixread=None, sub_jobs=None, runtime=None):
    """
    Write file by fio, use params from test_conf generally
    """
    tc_logger.info('==>Write file by fio over')
    device_id = test_conf["device_id"]
    exe_file = test_conf['tool']['fio']
    iodepth = test_conf.get("iodepth", "32")

    if block_size is None:
        block_size = test_conf.get("block_size", "4k")
    if file_size is None:
        file_size = test_conf.get("file_size", "10G")
    if rw is None:
        rw = test_conf.get("rw", "read")
    if rwmixread is None:
        rwmixread = test_conf.get("rwmixread", "50")
    if runtime is None:
        runtime = test_conf.get("runtime", "600")
    if sub_jobs is None:
        sub_jobs = test_conf.get('sub_jobs', None)
    rewrite = unify_bool_value(test_conf.get('rewrite', True))
    filename = os.path.join(test_conf['tool']['dir'], 'fio_test_file')

    # testcase business workflow
    adb = ADB(device_id)
    if rw in ["randrw", "rw", "readwrite"]:
        rw = rw + " --rwmixread=" + rwmixread
    _sub_jobs = '--name=perf_std --filename={}'.format(filename)
    if sub_jobs:
        _sub_jobs_list = list()
        for i in range(1, int(sub_jobs) + 1):
            sub_name = 'job' + str(i)
            sub_filename = 'fio_test_' + str(file_size) + '_' + str(i)
            if not rewrite:
                rand_str = random.choice(range(10000))
                sub_filename = 'fio_test_' + str(file_size) + '_' + str(i) + '_' + str(rand_str)
            sub_file_path = os.path.join(test_conf['tool']['dir'], sub_filename)
            _sub_job = '--name={0} --filename={1}'.format(sub_name, sub_file_path)
            _sub_jobs_list.append(_sub_job)
        _sub_jobs = ' '.join(_sub_jobs_list)
    fio_command = "shell {0} --direct=1 --norandommap=0 --numjobs=1 --ioengine=libaio --iodepth={1} --rw={2} --bs={3} --size={4} --runtime={5} --output-format=json,normal {6}" \
        .format(exe_file, iodepth, rw, block_size, file_size, runtime, _sub_jobs)
    adb.execute_adb_command(fio_command)
    tc_logger.info('==>Write file by fio over')


def read_file_by_iozone(block_size=None, file_size=None, threads=None, sequential=None):
    """
    Ｒead file by iozone, will use params from test_conf generally
    """
    tc_logger.info('==>Start to read file by iozone')
    device_id = test_conf["device_id"]
    exe_file = test_conf['tool']['iozone']
    exe_dir = os.path.dirname(exe_file)
    if block_size is None:
        block_size = test_conf.get('block_size', '4k').lower()
    if file_size is None:
        file_size = test_conf.get('file_size', '128m').lower()
    if threads is None:
        threads = test_conf.get('threads', '8')
    if sequential is None:
        sequential = test_conf.get('sequential', True)
    sequential = '1' if unify_bool_value(sequential) else '2'
    command = 'shell "cd {0};{1} -w -r {2} -s {3} -i {4} -I -t {5}"'.format(exe_dir, exe_file, block_size, file_size, sequential, str(threads))

    adb = ADB(device_id)
    adb.execute_adb_command(command)
    tc_logger.info('==>Read file by iozone over')
