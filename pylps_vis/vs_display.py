from pylps.constants import *

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import *


class VSDisplay(BoxLayout):
    identity = StringProperty()
    time = StringProperty()
    height = NumericProperty()

    def __init__(self, visual_state, vis_config):
        super().__init__()
        self.display_classes = vis_config.display_classes
        self.display_funcs = vis_config.display_funcs
        self.height = 100

        self.identity = 'time' + str(visual_state.time)
        self.visual_state = visual_state
        self.time = str(self.visual_state.time)
        self.displayed_actions = []
        self.displayed_fluents = []
        self.cnt = 0

        self.apply_display_funcs()

        # Display only
        for cls_name, cls in self.display_classes.items():

            if cls_name in self.visual_state.actions.keys():
                states = self.visual_state.actions[cls_name]

                for args in states:
                    self.display(ACTION, cls, list(args))

            if cls_name in self.visual_state.fluents.keys():
                states = self.visual_state.fluents[cls_name]

                for args in states:
                    self.display(FLUENT, cls, list(args))

    def display(self, d_type, cls, args):

        w = cls(*args).get_widget()

        self.ids.tpdisplay.add_widget(w)

        if d_type is ACTION:
            self.displayed_actions.append(w)

        if d_type is FLUENT:
            self.displayed_fluents.append(w)

    def apply_display_funcs(self):

        actions = self.visual_state.actions
        fluents = self.visual_state.fluents

        state_objs = {}

        for k, v in actions.items():
            state_objs[k] = v

        for k, v in fluents.items():
            state_objs[k] = v

        for f in self.display_funcs:

            f_ret = f(state_objs)

            for name, v in f_ret.items():
                if name == 'height':
                    self.height = v
                    continue

                if actions.get(name, None):
                    self.visual_state.actions[name] = v
                    continue

                if fluents.get(name, None):
                    self.visual_state.fluents[name] = v
                    continue
