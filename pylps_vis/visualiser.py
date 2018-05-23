from pylps.core import *

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import *
from pylps_vis.vs_display import VSDisplay
from pylps_vis.state_generation import generate_states
kivy.require('1.0.7')


class VisConfig(object):
    def __init__(self, display_classes={}, position_funcs={},
                 stepwise=False):
        self.display_classes = display_classes
        self.position_funcs = position_funcs
        self.stepwise = stepwise


class PylpsScreenManager(ScreenManager):
    pass


class PylpsMainScreen(Screen):
    info = StringProperty()
    current_time_str = StringProperty()
    max_time_str = StringProperty()
    exec_status = StringProperty()

    def __init__(self, vis_config):
        super().__init__()
        self.vis_config = vis_config

        self.current_time = 0
        self.manual = False
        self.vs_display_widgets = {}
        self.widget_pos = {}

        self.visual_states = []
        self.max_time = 0

        self.update_visual_states()
        self.update_display()

        self.stepwise_exec = False

        if self.vis_config.stepwise:
            Clock.schedule_once(
                lambda dt: self.pylps_execute(stepwise=True), 0.01)
        else:
            Clock.schedule_once(lambda dt: self.pylps_execute(), 0.01)

    def add_vs_display(self, visual_state):
        widget = VSDisplay(visual_state, self.vis_config)
        self.vs_display_widgets[visual_state.time] = widget
        self.ids.scrollgrid.add_widget(widget)

    def update_visual_states(self):
        self.exec_status = "Done"

        if not self.visual_states:
            return

        if self.visual_states:
            self.max_time = self.visual_states[-1].time

        for v in self.visual_states:
            self.add_vs_display(v)

        self.update_display()

    def update_display(self, scroll=True):
        # Bound checking
        if self.current_time > self.max_time:
            self.current_time = self.max_time

        if self.current_time < 0:
            self.current_time = 0

        self.current_time_str = str(self.current_time)
        self.max_time_str = str(self.max_time)

        if scroll:
            try:
                self.ids.scrollgridview.scroll_to(
                    self.vs_display_widgets[self.current_time]
                )
            except KeyError:
                pass

    def reset_display(self, full_reset=False):
        if full_reset:
            self.max_time = 0
            self.stepwise_exec = False

        for _, w in self.vs_display_widgets.items():
            self.ids.scrollgrid.remove_widget(w)
        self.vs_display_widgets = {}
        self.update_display()

    def scroll_view(self):
        if self.max_time == 0:
            return

        self.manual = True
        scroll_pos = 1.1 - self.ids.scrollgridview.scroll_y
        scroll_time = scroll_pos / (1 / self.max_time)
        self.current_time = int(scroll_time)
        self.update_display(scroll=False)

    ''' BUTTONS '''

    def move_timepoint(self, command):
        commands = {
            'BACK_ALL': -2e6,
            'BACK_1': -1,
            'FWD_1': 1,
            'FWD_ALL': 2e6
        }

        self.manual = True
        self.current_time += commands[command]
        self.update_display()

    def move_auto(self, first=False):
        if self.current_time < self.max_time and not self.manual:
            self.current_time += 0 if first else 1
            self.update_display()
            Clock.schedule_once(lambda dt: self.move_auto(), 0.7)

    def play(self):
        self.manual = False
        self.move_auto(first=True)

    '''PYLPS CONTROL'''

    def update_exec_status(self, new_exec_status):
        self.exec_status = new_exec_status

    def pylps_execute(self, stepwise=False):
        self.update_exec_status("In progress")

        if stepwise:
            Clock.schedule_once(
                lambda dt: self.pylps_execute_stepwise_helper(), 0.01)
        else:
            Clock.schedule_once(
                lambda dt: self.pylps_execute_helper(), 0.01)

    def pylps_post_execute(self):
        display_log = kb_display_log()
        self.visual_states = generate_states(display_log)
        self.reset_display()
        self.update_visual_states()

    def exec_debug_delay(self):
        import time
        time.sleep(0.5)

    def pylps_execute_helper(self):
        self.exec_debug_delay()
        execute()
        self.pylps_post_execute()

    def pylps_execute_stepwise_helper(self):
        self.exec_debug_delay()
        if self.stepwise_exec:
            execute_next_step()
        else:
            self.stepwise_exec = True
            execute(stepwise=True)

        self.pylps_post_execute()

        # To force display
        self.current_time = self.max_time
        self.update_display()


class PylpsVisualiserApp(App):

    def __init__(self, display_classes={}, position_funcs={}, stepwise=False):
        super().__init__()

        self.vis_config = VisConfig(
            display_classes=display_classes,
            position_funcs=position_funcs,
            stepwise=stepwise
        )

    def build(self):
        return PylpsMainScreen(vis_config=self.vis_config)
