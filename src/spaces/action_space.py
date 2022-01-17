"""
ActionSpace class. This is a wrapper to the discrete
actions in the actions.py module
"""

import numpy as np
import random
from gym.spaces.discrete import Discrete
from src.spaces.actions import ActionBase


class ActionSpace(Discrete):
    """
    ActionSpace class models a discrete action space of size n
    """

    def __init__(self, n: int) -> None:

        super(ActionSpace, self).__init__(n=n)

        # the list of actions the space contains
        self.actions = []

    def __getitem__(self, item) -> ActionBase:
        """
        Returns the item-th action
        :param item: The index of the action to return
        :return: An action obeject
        """
        return self.actions[item]

    def __setitem__(self, key: int, value: ActionBase) -> None:
        """
        Update the key-th Action with the new value
        :param key: The index to the action to update
        :param value: The new action
        :return: None
        """
        self.actions[key] = value

    def shuffle(self) -> None:
        """
        Randomly shuffle the actions in the space
        :return:
        """
        random.shuffle(self.actions)

    def get_action_by_column_name(self, column_name: str) -> ActionBase:
        """
        Get the action that corresponds to the column with
        the given name. Raises ValueError if such an action does not
        exist
        :param column_name: The column name to look for
        :return: The action that corresponds to this name
        """

        for action in self.actions:
            if action.column_name == column_name:
                return action

        raise ValueError("No action exists for column={0}".format(column_name))

    def add(self, action: ActionBase) -> None:
        """
        Add a new action in the space. Throws ValueError if the action space
        is full
        :param action: the action to add
        :return: None
        """
        if len(self.actions) >= self.n:
            raise ValueError("Action space is saturated. You cannot add a new action")

        # set a valid id for the action
        action.idx = len(self.actions)
        self.actions.append(action)

    def add_many(self, *actions) -> None:
        """
        Add many actions in one go
        :param actions: List of actions to add
        :return: None
        """
        for a in actions:
            self.add(action=a)

    def sample_and_get(self) -> ActionBase:
        """
        Sample the space and return an action to the application
        :return: The sampled action
        """
        action_idx = self.sample()
        return self.actions[action_idx]

    def get_non_exhausted_actions(self) -> list:
        """
        Returns a list of actions that have not exhausted the
        transformations that apply on a column.
        :return: list of actions. List may be empty. Client code should handle this
        """
        actions_ = []
        for action in self.actions:
            if not action.is_exhausted():
                actions_.append(action)

        return actions_

    def sample_and_get_non_exhausted(self) -> ActionBase:
        """
        Sample an action from the non exhausted actions
        :return: A non-exhausted action
        """
        actions = self.get_non_exhausted_actions()
        return np.random.choice(actions)

    def is_exhausted(self) -> bool:
        """
        Returns true if all the actions in the space are exhausted
        :return:
        """
        finished = True
        for action in self.actions:
            if not action.is_exhausted():
                return False

        return finished

    def reset(self) -> None:
        """
        Reset every action in the action space
        :return:
        """
        for action in self.actions:
            action.reinitialize()

