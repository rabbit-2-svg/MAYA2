"""
Author: William Zhou
Email: william_zhou@ymtc.com
"""
import os


def is_digit(value):
    try:
        float(value)
        return True
    except:
        return False


def unify_bool_value(value):
    """
    Unify True/'TRUE'/'True'/'true'/'1'/1 to True, unify False/'FALSE'/'False'/'false'/'0'/0 to False

    :param value: an object like True/'TRUE'/'True'/'true'/'1'/1
    :return: unified value
    """
    if isinstance(value, (str, int)):
        value = str(value).lower() in ['true', '1']
    return value


def convert_storage_unit(string, unit='G'):
    """
    Convert storage value to target unit

    :param string: string like, 1G, 1024MB, 1024KB
    :param unit: target unit, like G, M, K
    :return: unified value
    """
    unit = unit.lower()
    string = string.lower()
    if 'g' in string:
        value = int(string.split('g')[0])
    elif 'm' in string:
        value = int(string.split('m')[0]) / 1024
    elif 'k' in string:
        value = int(string.split('k')[0]) / 1024 / 1024
    else:
        value = int(string.split('k')[0]) / 1024 / 1024 / 1024

    if 'g' in unit:
        result = value
    elif 'm' in unit:
        result = value * 1024
    elif 'k' in unit:
        result = value * 1024 * 1024
    else:
        result = value * 1024 * 1024 * 1024
    result = str(int(result)) + unit.upper()
    return result


def update_config_path(attrs):
    """
    Update test_conf with absolute path of attribute

    :param attrs: a dict
    :return: None
    """
    for key, value in attrs.items():
        if isinstance(value, str):
            common_dir = attrs['dir']
            if key.strip().lower() != 'dir':
                attr_absolute_path = os.path.join(common_dir, attrs[key])
                attrs[key] = attr_absolute_path
        else:
            update_config_path(value)


def complete_config_path(devices, config_file):
    """
    As device attribute is not absolute path in test_conf.yaml, this method will auto complete the path

    :param devices: supported devices in test_conf.yaml
    :param config_file: test_conf
    :return: None
    """
    for device in devices:
        if config_file.get(device, None):
            attrs = config_file[device]
            update_config_path(attrs)
    return config_file


if __name__ == '__main__':
    unify_bool_value(1)
