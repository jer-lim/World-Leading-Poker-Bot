import sys
sys.path.insert(0, './pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import time


""" =========== *Remember to import your agent!!! =========== """
from randomplayer import RandomPlayer
from trainedplayer import TrainedPlayer
from scaramucci import BootStrapBot
""" ========================================================= """

def start_bot_trainer(num_trials):
    start = time.time()
    call_weight_max = 1
    call_weight_min = 0
    raise_weight_max = 1
    raise_weight_min = 0

    for i in range(num_trials):
        # 'algorithm' field is irrelevant here, just a placeholder. We specify it under Register Players.
        results = train_bots('agent1', RandomPlayer(), 'agent2', RandomPlayer(), call_weight_max, call_weight_min,
                            raise_weight_max, raise_weight_min)

        # We want to reset the weights after each iteration
        call_weight_max = -1
        call_weight_min = 2
        raise_weight_max = -1
        raise_weight_min = 2

        for result in results:
            call_weight_max = max(call_weight_max, result[1])
            call_weight_min = min(call_weight_min, result[1])
            raise_weight_max = max(raise_weight_max, result[2])
            raise_weight_min = min(raise_weight_min, result[2])

    end = time.time()
    print("\nTime taken to train: %.4f seconds" %(end-start))
    print(f"CW - Max: {call_weight_max}, Min: {call_weight_min}, RW - Max:{raise_weight_max}, Min: {raise_weight_min}")
    return (call_weight_max, call_weight_min, raise_weight_max, raise_weight_min)

"""
Generates a 2D array of call_weight against raise_weight (details of weights in trainedplayer.py)
We vary call and raise probabilities at the same time in a 2D array to construct a 2D hill-climbing problem.

Returns 4 tuples showing 3 items: the maximum gains, the specified CW and specified RW.
These denote the maximum points, forming a plane.
"""

def train_bots(agent_name1, agent1, agent_name2, agent2, call_weight_max, call_weight_min, raise_weight_max,
               raise_weight_min):

    # Init to play 500 games of 1000 rounds
    num_game = 1
    max_round = 10
    initial_stack = 10000
    smallblind_amount = 20

    call_weight_difference = call_weight_max - call_weight_min
    raise_weight_difference = raise_weight_max - raise_weight_min
    call_weights = []
    raise_weights = []
    partition_interval_number = 10

    # Generates the cw and rw that the trainer will be testing the bots on
    for i in range(partition_interval_number+1):
        call_weights.append(call_weight_min + call_weight_difference / float(partition_interval_number) * i)
        raise_weights.append(raise_weight_min + raise_weight_difference / float(partition_interval_number) * i)

    # print(call_weights)
    # print(raise_weights)

    # Construct a 2D matrix of results to find maximum point
    result_matrix = []

    for cw in call_weights:
        for rw in raise_weights:
            print(f"Checking with weights: Call Weight = {cw}, Raise Weight = {rw}")
            result_list = []

            # Init pot of players
            agent1_pot = 0
            agent2_pot = 0

            # Setting configuration
            config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)

            # Register players
            config.register_player(name=agent_name1, algorithm=TrainedPlayer())
            config.register_player(name=agent_name2, algorithm=BootStrapBot())
            # config.register_player(name=agent_name1, algorithm=agent1())
            # config.register_player(name=agent_name2, algorithm=agent2())

            # Set trainedplayer weights
            config.players_info[0]['algorithm'].call_weight = cw
            config.players_info[0]['algorithm'].raise_weight = rw

            # Start playing num_game games
            for game in range(1, num_game + 1):
                game_result = start_poker(config, verbose=0)
                agent1_pot = agent1_pot + game_result['players'][0]['stack']
                agent2_pot = agent2_pot + game_result['players'][1]['stack']

            result_list.append(((agent1_pot - agent2_pot) / float(num_game), cw, rw))

        result_matrix.append(result_list)

    maximum_points = []
    for x in result_matrix:
        for y in x:
            if len(maximum_points) < 4:
                maximum_points.append(y)
            else:
                maximum_points.sort()
                if y[0] > maximum_points[0][0]:
                    maximum_points[0] = y

    #print(maximum_points)
    return maximum_points

start_bot_trainer(1)