from pylps.core import *
from pylps.lps_data_structures import LPSConstant
from pylps_vis.visualiser import *
from kivy.uix.label import Label
from collections import defaultdict

initialise(max_time=10)

create_fluents('location(_, _)')
create_actions('move(_, _)', 'say(_)')
create_events(
    'clear(_)', 'make_tower(_)',
    'make_on(_, _)', 'make_clear(_)',
)
create_variables('Block', 'Block1', 'Place', 'Places')

initially(
    location('f', 'floor'), location('b', 'f'), location('e', 'b'),
    location('a', 'floor'), location('d', 'a'), location('c', 'd'),
)

reactive_rule(True).then(
    make_tower(['a', 'b', 'c', 'floor']).frm(T1, T2),
)

reactive_rule(True).then(
    make_tower(['f', 'e', 'd', 'floor']).frm(T1, T2),
)


goal(clear(Block).at(T)).requires(
    Block != 'floor',
    ~location(_, Block).at(T),
)

goal(clear('floor').at(_))

goal(
    make_tower([Block | LPSConstant('floor')]).frm(T1, T2)
).requires(
    make_on(Block, 'floor').frm(T1, T2),
)

goal(
    make_tower([Block | [Place | Places]]).frm(T1, T3)
).requires(
    Place != 'floor',
    make_tower([Place | Places]).frm(T1, T2),
    make_on(Block, Place).frm(T2, T3),
)

goal(make_on(Block, Place).frm(T1, T2)).requires(
    ~location(Block, Place).at(T1),
    make_clear(Place).frm(T1, T2),
    make_clear(Block).frm(T2, T3),
    move(Block, Place).frm(T3, T4),
)

goal(make_on(Block, Place).frm(T, T)).requires(
    location(Block, Place).at(T),
)

goal(make_clear(Place).frm(T, T)).requires(
    clear(Place).at(T),
)

goal(make_clear(Block).frm(T1, T2)).requires(
    location(Block1, Block).at(T1),
    make_on(Block1, 'floor').frm(T1, T2),
)

move(Block, Place).initiates(location(Block, Place))
move(Block, _).terminates(location(Block, Place))


def generate_towers(locations):
    above = defaultdict(list)
    for top, bottom in locations:
        above[bottom].append(top)

    towers = []
    for block in above['floor']:
        new_tower = [block]

        cur_block = block
        while True:
            next_block = above.get(cur_block, None)

            if not next_block:
                break

            cur_block = next_block[0]
            new_tower.append(cur_block)

        towers.append(new_tower)

    return towers


def position_towers(towers):
    START_X = -300
    START_Y = 0
    pos_args = []

    for t_id, tower in enumerate(towers):
        for b_id, block in enumerate(tower):
            x = t_id * 100 + START_X
            y = b_id * 25 + START_Y
            pos_args.append((block, x, y))

    return pos_args


def location_pos(state_objects):
    height = 200
    locations = sorted(state_objects['location'])
    towers = generate_towers(locations)

    return {
        'height': height,
        'location': position_towers(towers)
    }


class LocationDisplay():
    def __init__(self, *args):
        self.block_name = args[0].upper()
        self.x = args[1]
        self.y = args[2]

    def get_widget(self):
        w = Label(
            text=self.block_name,
            pos=(self.x, self.y)
        )
        return w


display_classes = {
    'location': LocationDisplay
}

display_funcs = [location_pos]

app = PylpsVisualiserApp(
    display_classes=display_classes,
    display_funcs=display_funcs,
    stepwise=True)

app.run()
