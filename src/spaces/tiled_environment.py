"""
Tile environment
"""

import copy
from typing import TypeVar
from dataclasses import dataclass
from src.extern.tile_coding import IHT, tiles
from src.spaces.actions import ActionBase, ActionType
from src.spaces.time_step import TimeStep
from src.exceptions.exceptions import InvalidParamValue
from src.spaces.state import State
from src.spaces.time_step import copy_time_step

Env = TypeVar('Env')


@dataclass(init=True, repr=True)
class TiledEnvConfig(object):
    """Configuration for the TiledEnvironment
    """

    env: Env = None
    num_tilings: int = 0
    max_size: int = 0
    tiling_dim: int = 0
    column_scales: dict = None


class TiledEnv(object):
    IS_TILED_ENV_CONSTRAINT = True

    def __init__(self, config: TiledEnvConfig) -> None:

        self.env = config.env
        self.max_size = config.max_size
        self.num_tilings = config.num_tilings
        self.tiling_dim = config.tiling_dim

        # set up the columns scaling
        # only the columns that are to be altered participate in the
        # tiling
        self.column_scales = config.column_scales

        # Initialize index hash table (IHT) for tile coding.
        # This assigns a unique index to each tile up to max_size tiles.
        self._validate()
        self.iht = IHT(self.max_size)

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def n_actions(self) -> int:
        return len(self.env.action_space)

    @property
    def n_states(self) -> int:
        return self.env.n_states

    def step(self, action: ActionBase) -> TimeStep:
        """Execute the action in the environment and return
        a new state for observation

        Parameters
        ----------
        action: The action to execute

        Returns
        -------

         An instance of TimeStep type

        """

        raw_time_step = self.env.step(action)

        # a state wrapper to communicate
        state = State()

        # the raw environment returns an index
        # of the bin that the total distortion falls into
        state.bin_idx = raw_time_step.observation
        state.total_distortion = raw_time_step.info["total_distortion"]
        state.column_names = self.env.column_names

        time_step = copy_time_step(time_step=raw_time_step, **{"observation": state})
        #time_step = copy.deepcopy(raw_time_step)
        #time_step.observation = state

        return time_step

        return

    def reset(self, **options) -> TimeStep:
        """Reset the environment so that a new sequence
        of episodes can be generated

        Parameters
        ----------
        options: Client provided named options

        Returns
        -------

        An instance of TimeStep type
        """

        raw_time_step = self.env.reset(**options)

        # a state wrapper to communicate
        state = State()

        # the raw environment returns an index
        # of the bin that the total distortion falls into
        state.bin_idx = raw_time_step.observation
        state.total_distortion = raw_time_step.info["total_distortion"]
        state.column_names = self.env.column_names

        time_step = copy_time_step(time_step=raw_time_step, **{"observation": state})

        #time_step = copy.deepcopy(raw_time_step)
        #time_step.observation = state

        return time_step

    def get_action(self, aidx: int) -> ActionBase:
        return self.env.action_space[aidx]

    def save_current_dataset(self, episode_index: int, save_index: bool = False) -> None:
        """
        Save the current distorted datase for the given episode index
        :param episode_index:
        :param save_index:
        :return:
        """
        self.env.save_current_dataset(episode_index, save_index)

    def create_bins(self) -> None:
        """
        Create the bins
        :return:
        """
        self.env.create_bins()

    def get_aggregated_state(self, state_val: float) -> int:
        """
        Returns the bin index that the state_val corresponds to
        :param state_val: The value of the state. This typically will be
        either a column normalized distortion value or the dataset average total
        distortion
        :return:
        """
        return self.env.get_aggregated_state(state_val)

    def initialize_column_counts(self) -> None:
        """
        Set the column visit counts to zero
        :return:
        """
        self.env.initialize_column_counts()

    def all_columns_visited(self) -> bool:
        """
        Returns True is all column counts are greater than zero
        :return:
        """
        return self.env.all_columns_visited()

    def initialize_distances(self) -> None:
        """
        Initialize the text distances for features of type string. We set the
        normalized distance to 0.0 meaning that no distortion is assumed initially
        :return: None
        """
        self.env.initialize_distances()

    def apply_action(self, action: ActionBase):
        """
        Apply the action on the environment
        :param action: The action to apply on the environment
        :return:
        """
        self.env.apply_action(action)

    def total_current_distortion(self) -> float:
        """
        Calculates the current total distortion of the dataset.
        :return:
        """
        return self.env.total_current_distortion()

    def get_scaled_state(self, state: State) -> list:
        """
        Scales the state components ad returns the
        scaled state
        :param state:
        :return:
        """
        scaled_state_vals = []
        for name in state:
            scaled_state_vals.append(state[name] * self.columns_scales[name])

        return scaled_state_vals

    def featurize_state_action(self, state, action: ActionBase) -> None:
        """
        Returns the featurized representation for a state-action pair
        :param state:
        :param action:
        :return:
        """
        scaled_state = self.get_scaled_state(state)
        featurized = tiles(self.iht, self.num_tilings, scaled_state, [action])
        return featurized

    def _validate(self) -> None:
        if self.max_size <= 0:
            raise InvalidParamValue(param_name="max_size",
                                    param_value=str(self.max_size) + " should be > 0")

        # Ensure max_size >= total number of tiles (num_tilings x tiling_dim x tiling_dim)
        # to ensure no duplicates.
        if self.max_size < self.num_tilings * self.tiling_dim * self.tiling_dim:
            raise InvalidParamValue(param_name="max_size",
                                    param_value=str(self.max_size) +
                                    " should be >=num_tilings * tiling_dim * tiling_dim")

        if len(self.column_scales) == 0:
            raise InvalidParamValue(param_name="column_scales",
                                    param_value=str(len(self.column_scales)) + " should not be empty")
