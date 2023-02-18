import numpy as np

class PredatorPolicy:
    @classmethod
    def apply(cls, pred, preds, preys, obstacles) -> np.ndarray:
        raise("Missing implementation")

class NearestPreyPolicy(PredatorPolicy):
    @classmethod
    def apply(cls, pred, preds, preys, obstacles) -> np.ndarray:
        if len(preys) == 0: return []
        prey = min(preys, key=lambda x: pred.get_square_distance(x))
        return prey.pos - pred.pos