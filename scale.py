from typing import Tuple


class ScaleLinear:
    
    def __init__(self, domain: Tuple[float, float], range: Tuple[int, int]):
        self._domain = 1.0 / (domain[1] - domain[0])
        self._domain_offset = -domain[0]
        self._range = range[1] - range[0]
        self._range_offset = range[0]
    
    def value(self, x: float) -> int:
        return int((x + self._domain_offset) * self._domain * self._range + self._range_offset)


