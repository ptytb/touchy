from autoclass import autoclass


class StatefulAxes:
    def __init__(self):
        self.axis_values = {
            "x": 0, "y": 0, "z": 0,
            "dx": 0, "dy": 0, "dz": 0,
            "tx": 0, "ty": 0, "tz": 0,
            "tdx": 0, "tdy": 0, "tdz": 0,
        }
        
    def value(self, axis_values):
        for axis, value in axis_values.items():
            d = self.axis_values[axis] - value
            t = self.axis_values[f't{axis}'] + value
            self.axis_values[axis] = value
            self.axis_values[f'd{axis}'] = d
            self.axis_values[f't{axis}'] = t
            self.axis_values[f'td{axis}'] += abs(d)
        return axis_values
    
    def reset(self):
        for axis in ['tx', 'ty', 'tz', 'tdx', 'tdy', 'tdz']:
            self.axis_values[axis] = 0


@autoclass
class ThresholdAxes(StatefulAxes):
    
    def __init__(self, threshold=0):
        super().__init__()
    
    def value(self, axis_values):
        axis_values = super(ThresholdAxes, self).value(axis_values)
        ignore = all(map(lambda axis: self.axis_values[axis] < self.threshold, ['tdx', 'tdy', 'tdz']))
        if ignore:
            return None
        else:
            self.reset()
            return axis_values
    
    def saturate(self):
        for axis in ['tdx', 'tdy', 'tdz']:
            self.axis_values[axis] = self.threshold
        

class AccumulatingAxes(StatefulAxes):
    def __init__(self):
        super().__init__()

    @property
    def total(self):
        return {
            'x': self.axis_values['tx'], 'y': self.axis_values['ty'], 'z': self.axis_values['tz']
        }

    def value(self, axis_values):
        super(AccumulatingAxes, self).value(axis_values)
        return self.total
