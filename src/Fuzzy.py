import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
error_x = ctrl.Antecedent(np.arange(-320, 321, 1), 'error_x')
error_y = ctrl.Antecedent(np.arange(-240, 241, 1), 'error_y')
yaw     = ctrl.Consequent(np.arange(-100, 101, 1), 'yaw')
vert    = ctrl.Consequent(np.arange(-40, 41, 1), 'vert')

error_x['neg']  = fuzz.gaussmf(error_x.universe, -160, 80)
error_x['zero'] = fuzz.gaussmf(error_x.universe,    0, 30)
error_x['pos']  = fuzz.gaussmf(error_x.universe,  160, 80)

error_y['neg']  = fuzz.gaussmf(error_y.universe, -120, 60)
error_y['zero'] = fuzz.gaussmf(error_y.universe,    0, 30)
error_y['pos']  = fuzz.gaussmf(error_y.universe,  120, 60)

yaw['neg']  = fuzz.gaussmf(yaw.universe, -60, 25)
yaw['zero'] = fuzz.gaussmf(yaw.universe,   0, 10)
yaw['pos']  = fuzz.gaussmf(yaw.universe,  60, 25)

vert['neg']  = fuzz.gaussmf(vert.universe, -35, 15)
vert['zero'] = fuzz.gaussmf(vert.universe,   0, 20)
vert['pos']  = fuzz.gaussmf(vert.universe,  35, 15)

rules = [
    ctrl.Rule(error_x['neg'],  yaw['neg']),
    ctrl.Rule(error_x['zero'], yaw['zero']),
    ctrl.Rule(error_x['pos'],  yaw['pos']),
    ctrl.Rule(error_y['neg'],  vert['pos']),
    ctrl.Rule(error_y['zero'], vert['zero']),
    ctrl.Rule(error_y['pos'],  vert['neg']),
]

fuzzy_ctrl = ctrl.ControlSystem(rules)
_sim = ctrl.ControlSystemSimulation(fuzzy_ctrl)


def compute_fuzzy_yaw_vert(h_offset: float, v_offset: float) -> (int, int):
    _sim.input['error_x'] = h_offset
    if abs(v_offset) < 5:
        _sim.input['error_y'] = 0
        _sim.compute()
        yaw_out = int(_sim.output['yaw'])
        return yaw_out, 0

    _sim.input['error_y'] = v_offset
    _sim.compute()
    yaw_out = int(_sim.output['yaw'])
    vert_out = int(_sim.output['vert'])
    return yaw_out, vert_out
