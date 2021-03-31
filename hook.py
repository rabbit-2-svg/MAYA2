"""
Author: William Zhou
Email: william_zhou@ymtc.com
"""
from common import pipeline
from conf.test_conf import test_conf, tc_logger


def set_up(level, **kwargs):
    """
    A hook that will be executed before execution
    :param level: case level or loop level
    :return: None
    """
    pre_actions = gather_action(precondition=True, level=level)
    for action in pre_actions:
        _action, param, kw_param = handle_action(action)
        func = getattr(pipeline, _action)
        if 'loop' not in kwargs.keys():
            func(*param, **kw_param)
        else:
            kw_param['loop'] = kwargs['loop']
            if kwargs['loop'] % test_conf.get('loop_interval', 1) == 0:
                func(*param, **kw_param)


def tear_down(level, **kwargs):
    """
    A hook that will be executed after execution
    :return: None
    """
    post_actions = gather_action(precondition=False, level=level)
    for action in post_actions:
        _action, param, kw_param = handle_action(action)
        func = getattr(pipeline, _action)
        if 'loop' not in kwargs.keys():
            func(*param, **kw_param)
        else:
            kw_param['loop'] = kwargs['loop']
            if kwargs['loop'] % test_conf.get('loop_interval', 1) == 0:
                func(*param, **kw_param)


def handle_action(raw_action, param_sep='@', kv_sep='='):
    """
    Split action, param and keywords param from raw action

    :param raw_action: raw action from user input, like restore_wb_avail_buf:100&check_flush_status=false&by_wait=false
    :param param_sep: parameter separator
    :param kv_sep: key value separator
    :return: tuple
    """
    param = list()
    kw_param = dict()
    _action = '_' + raw_action
    if ':' in raw_action:
        entity = raw_action.split(':')
        _action = '_' + entity[0].strip()
        argument = entity[1].strip()
        if param_sep in argument:
            arguments = argument.split(param_sep)
            for p in arguments:
                if kv_sep in p:
                    pair = p.split(kv_sep)
                    k = pair[0].strip()
                    v = pair[1].strip()
                    kw_param[k] = v
                else:
                    param.append(p.strip())
        else:
            if kv_sep in argument:
                pair = argument.split(kv_sep)
                k = pair[0].strip()
                v = pair[1].strip()
                kw_param[k] = v
            else:
                param.append(argument)
    return _action, param, kw_param


def gather_action(precondition=True, level='case'):
    """
    Combine default precondition in test_conf.ymal with custom precondition from set_up_case/tear_down_case
    :param precondition: True means it's precondition, False means post condition
    :param level: case level or loop level
    :return: actions, list
    """
    default_action = get_default_action(precondition, level)
    exclusive_action = get_exclusive_action(precondition, level)
    additional_action = get_additional_action(precondition, level)
    txt = 'All pre {} actions'.format(level) if precondition else 'All post {} actions'.format(level)

    if exclusive_action:
        actions = exclusive_action
    else:
        for action in additional_action:
            if action not in default_action:
                default_action.append(action)
        actions = default_action
    tc_logger.info('==>{}: {}'.format(txt, actions))
    return actions


def get_default_action(precondition=True, level='case'):
    """
    Get default action from input
    :param precondition: True means it's precondition, False means post condition
    :param level: case level or loop level
    :return: default action, list
    """
    default_action = list()
    if level == 'case':
        key = 'pre_case' if precondition else 'post_case'
    else:
        key = 'pre_loop' if precondition else 'post_loop'
    pre_key = test_conf.get(key, None)
    if pre_key:
        default_action = test_conf.get(pre_key, list())
        if default_action is None:
            default_action = list()
        else:
            if None in default_action:
                default_action.remove(None)
    if default_action:
        tc_logger.info('==>Default {} action: {}'.format(key, default_action))
    return default_action


def get_exclusive_action(precondition=True, level='case'):
    """
    Get exclusive action from input
    :param precondition: True means it's precondition, False means post condition
    :param level: case level or loop level
    :return: exclusive action, list
    """
    if level == 'case':
        key = 'ud_pre_case' if precondition else 'ud_post_case'
    else:
        key = 'ud_pre_loop' if precondition else 'ud_post_loop'
    exclusive_action = test_conf.get(key, list())
    if isinstance(exclusive_action, str):
        exclusive_action = [exclusive_action]
    if exclusive_action:
        tc_logger.info('==>Exclusive action: {}'.format(exclusive_action))
    return exclusive_action


def get_additional_action(precondition=True, level='case'):
    """
    Get additional action from input
    :param precondition: True means it's precondition, False means post condition
    :param level: case level or loop level
    :return: additional action, list
    """
    if level == 'case':
        key = 'add_pre_case' if precondition else 'add_post_case'
    else:
        key = 'add_pre_loop' if precondition else 'add_post_loop'
    additional_action = test_conf.get(key, list())
    if isinstance(additional_action, str):
        additional_action = [additional_action]
    if additional_action:
        tc_logger.info('==>Additional action: {}'.format(additional_action))
    return additional_action
