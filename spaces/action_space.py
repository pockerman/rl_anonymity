
from gym.spaces.discrete import Discrete
from spaces.actions import ActionBase


class ActionSpace(Discrete):

    def __init__(self, n: int) -> None:

        super(ActionSpace, self).__init__(n=n)
        self.actions = []

    def add(self, action: ActionBase) -> None:

        if len(self.actions) >= self.n:
            raise ValueError("Action space is saturated. You cannot add a new action")

        self.actions.append(action)

    def sample_and_get(self) -> ActionBase:

        action_idx = self.sample()
        return self.actions[action_idx]