from src.algorithms.q_learning import QLearning, QLearnConfig
from src.algorithms.trainer import Trainer
from src.utils.string_distance_calculator import DistanceType
from src.spaces.actions import ActionSuppress, ActionIdentity, ActionGeneralize, ActionTransform
from src.spaces.environment import Environment
from src.spaces.action_space import ActionSpace
from src.datasets.datasets_loaders import MockSubjectsLoader
from src.utils.reward_manager import RewardManager
from src.policies.epsilon_greedy_policy import EpsilonGreedyPolicy, EpsilonDecreaseOption
from src.utils.serial_hierarchy import SerialHierarchy


if __name__ == '__main__':

    EPS = 1.0
    GAMMA = 0.99
    ALPHA = 0.1

    # load the dataset
    ds = MockSubjectsLoader()

    # specify the action space. We need to establish how these actions
    # are performed
    action_space = ActionSpace(n=4)

    generalization_table = {"Mixed White/Asian": SerialHierarchy(values=["Mixed", ]),
                            "Chinese": SerialHierarchy(values=["Asian", ]),
                            "Indian": SerialHierarchy(values=["Asian", ]),
                            "Mixed White/Black African": SerialHierarchy(values=["Mixed", ]),
                            "Black African": SerialHierarchy(values=["Black", ]),
                            "Asian other": SerialHierarchy(values=["Asian", ]),
                            "Black other": SerialHierarchy(values=["Black", ]),
                            "Mixed White/Black Caribbean": SerialHierarchy(values=["Mixed", ]),
                            "Mixed other": SerialHierarchy(values=["Mixed", ]),
                            "Arab": SerialHierarchy(values=["Asian", ]),
                            "White Irish": SerialHierarchy(values=["White", ]),
                            "Not stated": SerialHierarchy(values=["Not stated"]),
                            "White Gypsy/Traveller": SerialHierarchy(values=["White", ]),
                            "White British": SerialHierarchy(values=["White", ]),
                            "Bangladeshi": SerialHierarchy(values=["Asian", ]),
                            "White other": SerialHierarchy(values=["White", ]),
                            "Black Caribbean": SerialHierarchy(values=["Black", ]),
                            "Pakistani": SerialHierarchy(values=["Asian", ])}

    action_space.add_many(ActionSuppress(column_name="gender", suppress_table={"F": SerialHierarchy(values=['*', ]),
                                                                               'M': SerialHierarchy(values=['*', ])}),
                          ActionIdentity(column_name="salary"), ActionIdentity(column_name="education"),
                          ActionGeneralize(column_name="ethnicity", generalization_table=generalization_table))

    # specify the reward manager to use
    reward_manager = RewardManager()

    # create the environment
    env = Environment(data_set=ds, action_space=action_space,
                      gamma=0.99, start_column="gender", reward_manager=reward_manager)
    # initialize text distances
    env.initialize_text_distances(distance_type=DistanceType.COSINE)

    algo_config = QLearnConfig()
    algo_config.n_itrs_per_episode = 1000
    algo_config.gamma = 0.99
    algo_config.alpha = 0.1
    algo_config.policy = EpsilonGreedyPolicy(eps=EPS, env=env,
                                             decay_op=EpsilonDecreaseOption.INVERSE_STEP)

    agent = QLearning(algo_config=algo_config)

    configuration = {"n_episodes": 10, "update_frequency": 100}

    # create a trainer to train the A2C agent
    trainer = Trainer(env=env, agent=agent, configuration=configuration)

    trainer.train()