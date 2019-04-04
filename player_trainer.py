import sys
sys.path.insert(0, './pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import time


""" =========== *Remember to import your agent!!! =========== """
from random_player import RandomPlayer
from scaramucci import BootStrapBot
from our_player import OurPlayer
""" ========================================================= """

def start_bot_trainer(num_trials):
    start = time.time()
    initial_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    for i in range(num_trials):
        # 'algorithm' field is irrelevant here, just a placeholder. We specify it under Register Players.
        initial_weights = train_bots('agent1', RandomPlayer(), 'agent2', RandomPlayer(), initial_weights)
        print("Iteration %d complete: Weights are now: %s\n" % (i, str(initial_weights)))

    end = time.time()
    print("\nTime taken to train: %.4f seconds" % (end-start))
    print("Final Weights: %s" % str(initial_weights))


"""
Notes for Trainer:

Trainer for weights for heuristic function. Each weight is a value from 0 to 1.
Training is done by varying individual weights one at a time from 0 to 1 with divisions of 1/100.
In each iteration of the weights, the best performing weights given all other weights are fixed is kept and reused.

Ideally, we should stop when the weights no longer fluctuate too wildly.

-----------------------------------------------

Notes for Player:

In order to make a player trainable, it must contain:

Attributes: The individual values are irrelevant at this point, as the trainer will reset these values.
    self.heuristic_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    
Method: Trainer uses this method to modify the weights on the bots.
        def set_heuristic_weights(self, index, value):
        self.heuristic_weights[index] = value
"""

def train_bots(agent_name1, agent1, agent_name2, agent2, initial_weights):

    # Init to play 500 games of 1000 rounds
    num_game = 1
    max_round = 10
    initial_stack = 10000
    smallblind_amount = 20

    trial_weights = []
    initial_weights = initial_weights
    weight_count = len(initial_weights)
    partition_interval_number = 100
    last_net_winnings = 0

    # Partitioning step to get the weights to be tested
    for p in range(0, partition_interval_number + 1):
        trial_weights.append(p * float(1) / partition_interval_number)

    for i in range(weight_count):
        print("Testing weight %d ..." % (i))
        print("Current w%d is now: %d" % (i, initial_weights[i]))
        print("Current weights are now %s" % (str(initial_weights)))

        current_best = (float("-inf"), 0)

        for weight in trial_weights:
            # Init pot of players
            agent1_pot = 0
            agent2_pot = 0

            # Setting configuration
            config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)

            # Register players
            config.register_player(name=agent_name1, algorithm=OurPlayer())
            config.register_player(name=agent_name2, algorithm=BootStrapBot())
            # config.register_player(name=agent_name1, algorithm=agent1())
            # config.register_player(name=agent_name2, algorithm=agent2())

            # Configuring other weights
            config.players_info[0]['algorithm'].w = initial_weights

            # Set trainedplayer weights
            config.players_info[0]['algorithm'].w[i] = weight

            # Start playing num_game games
            for game in range(1, num_game + 1):
                game_result = start_poker(config, verbose=0)
                agent1_pot = agent1_pot + game_result[0]['players'][0]['stack']
                agent2_pot = agent2_pot + game_result[0]['players'][1]['stack']

            if agent1_pot - agent2_pot > current_best[0]:
                current_best = (agent1_pot - agent2_pot, weight)
                print("Current best w%d is now: %s" % (i, str(current_best)))

        initial_weights[i] = current_best[1]

    last_net_winnings = check_perf(initial_weights, last_net_winnings)
    return initial_weights


"""
Method used to check increase in performance after each iteration of weights
"""


def check_perf(weights, last_net_winnings):
    # Init to play 500 games of 1000 rounds
    num_game = 1
    max_round = 10
    initial_stack = 10000
    smallblind_amount = 0

    # Init pot of players
    agent1_pot = 0
    agent2_pot = 0

    # Setting configuration
    config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)

    # Register players
    config.register_player(name="agent_name1", algorithm=OurPlayer())
    config.register_player(name="agent_name2", algorithm=BootStrapBot())

    # Configuring other weights
    config.players_info[0]['algorithm'].w = weights

    # Start playing num_game games
    for game in range(1, num_game + 1):
        game_result = start_poker(config, verbose=0)
        agent1_pot = agent1_pot + game_result[0]['players'][0]['stack']
        agent2_pot = agent2_pot + game_result[0]['players'][1]['stack']

    curr_net_winnings = agent1_pot - agent2_pot
    performance_gain = 0
    if not last_net_winnings == 0:
        performance_gain = curr_net_winnings - last_net_winnings / float(last_net_winnings)
    print("Performance changed by %d percent" % (performance_gain * 100))

    return curr_net_winnings


start_bot_trainer(2)