import copy
from collections import defaultdict

from pylps.core import *


class LogObject(object):
    def __init__(self, display_log_item):
        self.type = display_log_item[0]
        self.name = display_log_item[1]
        self.args = display_log_item[2]

        if isinstance(display_log_item[3], tuple):
            self.start_time = display_log_item[3][0]
            self.end_time = display_log_item[3][1]
        else:
            self.start_time = display_log_item[3]
            self.end_time = self.start_time

    def __repr__(self):
        return str(tuple((self.type, self.name, self.args, self.end_time)))


class VisualState(object):
    def __init__(self, time):
        self.time = time
        self.actions = defaultdict(set)
        self.fluents = defaultdict(set)

    def __repr__(self):
        ret = "Time %s\n" % str(self.time)
        ret += "ACTIONS\n"
        for action, args in self.actions.items():
            ret += "[%s]: %s\n" % (action, str(args))

        ret += "FLUENTS\n"
        for fluent, args in self.fluents.items():
            ret += "[%s]: %s\n" % (fluent, str(sorted(args)))
        ret += '\n'
        return ret

    def add_action(self, action, args):
        self.actions[action].add(args)

    def remove_action(self, action, args):
        self.actions[action].remove(args)

    def clear_actions(self):
        self.actions = defaultdict(set)

    def add_fluent(self, fluent, args):
        self.fluents[fluent].add(args)

    def remove_fluent(self, fluent, args):
        self.fluents[fluent].remove(args)


def generate_states(display_log):
    display_log = [LogObject(i) for i in display_log]
    max_time = display_log[-1].end_time

    states = [VisualState(0)]
    ptr = 0

    for i in range(max_time + 1):
        if i > 0:
            states.append(copy.deepcopy(states[i - 1]))
            states[i].time += 1
            states[i].clear_actions()

        while ptr < len(display_log):
            log_item = display_log[ptr]
            if log_item.end_time > i:
                break

            if log_item.type is F_INITIATE:
                states[i].add_fluent(log_item.name, tuple(log_item.args))

            if log_item.type is F_TERMINATE:
                states[i].remove_fluent(log_item.name, tuple(log_item.args))

            if log_item.type is ACTION:
                states[i].add_action(log_item.name, tuple(log_item.args))

            ptr += 1

    return states
