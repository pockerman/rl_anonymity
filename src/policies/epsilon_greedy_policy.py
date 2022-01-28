"""
Epsilon greedy policy implementation
"""
import random
import numpy as np
from enum import Enum
from typing import Any, TypeVar

from src.utils.mixins import WithMaxActionMixin

UserDefinedDecreaseMethod = TypeVar('UserDefinedDecreaseMethod')
Env = TypeVar("Env")
QTable = TypeVar("QTable")


class EpsilonDecreaseOption(Enum):
    """
    Options for reducing epsilon
    """

    NONE = 0
    EXPONENTIAL = 1
    INVERSE_STEP = 2
    CONSTANT_RATE = 3
    USER_DEFINED = 4


class EpsilonGreedyPolicy(WithMaxActionMixin):

    def __init__(self, env: Env, eps: float,
                 decay_op: EpsilonDecreaseOption,
                 max_eps: float = 1.0, min_eps: float = 0.001,
                 epsilon_decay_factor: float = 0.01,
                 user_defined_decrease_method: UserDefinedDecreaseMethod = None) -> None:
        super(WithMaxActionMixin, self).__init__()
        self._eps = eps
        self._n_actions = env.action_space.n
        self._decay_op = decay_op
        self._max_eps = max_eps
        self._min_eps = min_eps
        self._epsilon_decay_factor = epsilon_decay_factor
        self.user_defined_decrease_method: UserDefinedDecreaseMethod = user_defined_decrease_method

    def __str__(self) -> str:
        return self.__name__

    def __call__(self, q_table: QTable, state: Any) -> int:
        """
        Execute the policy
        :param q_func:
        :param state:
        :return:
        """

        # update the store q_table
        self.q_table = q_table

        # select greedy action with probability epsilon
        if random.random() > self._eps:
            return self.max_action(state=state, n_actions=self._n_actions)
        else:

            # otherwise, select an action randomly
            # what happens if we select an action that
            # has exhausted it's transforms?
            return random.choice(np.arange(self._n_actions))

    def on_state(self, state: Any) -> int:
        """
        Returns the optimal action on the current state
        :param state:
        :return:
        """
        return self.max_action(state=state, n_actions=self._n_actions)

    def actions_after_episode(self, episode_idx: int, **options) -> None:
        """
        Apply actions on the policy after the end of the episode
        :param episode_idx: The episode index
        :param options:
        :return: None
        """

        if self._decay_op == EpsilonDecreaseOption.NONE:
            return

        if self._decay_op == EpsilonDecreaseOption.USER_DEFINED:
            self._eps = self.user_defined_decrease_method(self._eps, episode_idx)

        if self._decay_op == EpsilonDecreaseOption.INVERSE_STEP:

            if episode_idx == 0:
                episode_idx = 1

            self._eps = 1.0 / episode_idx

        elif self._decay_op == EpsilonDecreaseOption.EXPONENTIAL:
            self._eps = self._min_eps + (self._max_eps - self._min_eps) * np.exp(-self._epsilon_decay_factor * episode_idx)

        elif self._decay_op == EpsilonDecreaseOption.CONSTANT_RATE:
            self._eps -= self._epsilon_decay_factor

        if self._eps < self._min_eps:
            self._eps = self._min_eps


