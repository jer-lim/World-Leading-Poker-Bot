import sys
sys.path.insert(0, './pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import time
from me import MePlayer
from argparse import ArgumentParser
from our_player import OurPlayer
from random_player import RandomPlayer
from raise_player import RaisedPlayer
from call_player import CallPlayer
from our_player_alternative import OurPlayerAlternative
from our_player_copy import OurPlayerCopy
from joblib import Parallel, delayed

import pandas as pd
"""
The module measures the performance of an agent
Assign the player you want to test as MY_PLAYER (Make sure you import the player)

Run `python measure_performance.py` in root directory
"""
MY_PLAYER = OurPlayer()

def testperf(agent_name1, agent1, agent_name2, agent2):
    num_game = 100
    max_round = 200
    initial_stack = 10000
    smallblind_amount = 20

    # Init pot of players
    agent1_pot = 0
    agent2_pot = 0

    # Setting configuration
    config = setup_config(
        max_round=max_round,
        initial_stack=initial_stack,
        small_blind_amount=smallblind_amount)

    # Register players
    config.register_player(name=agent_name1, algorithm=agent1)
    config.register_player(name=agent_name2, algorithm=agent2)

    results = pd.DataFrame(0, index = range(1,max_round+1), columns=[x.name for x in [agent1, agent2]])


    # Start playing num_game games
    def play_game(game):
        print("Game number: ", game)
        game_result, result_hist = start_poker(config, verbose=0)
        #agent1_pot = agent1_pot + game_result['players'][0]['stack']
        #agent2_pot = agent2_pot + game_result['players'][1]['stack']
        print(result_hist)
        return result_hist


    game_results = Parallel(n_jobs=-1)(delayed(play_game)(game) for game in range(1, num_game + 1))



    for r in game_results:
        results = results.add(r, fill_value=0)




    results.to_csv("data_for_alternative.csv")



    print("\n After playing {} games of {} rounds, the results are: ".format(
        num_game, max_round))
    print("\n " + agent_name1 + "'s final pot: ", agent1_pot)
    print("\n " + agent_name2 + "'s final pot: ", agent2_pot)

    if (agent1_pot < agent2_pot):
        print("\n Congratulations! " + agent_name2 + " has won.")
    elif (agent1_pot > agent2_pot):
        print("\n Congratulations! " + agent_name1 + " has won.")
    else:
        print("\n It's a draw!")


if __name__ == '__main__':
    my_name = "ME"
    my_agent = OurPlayer()
    my_agent.name = my_name

    players = {
        "no_mwu":MePlayer()
    }
    for name, base_agent in players.items():
        base_agent.name = name
        start = time.time()

        testperf(my_name, my_agent, name, base_agent)
        end = time.time()

        print("\n Time taken to play: %.4f seconds" % (end - start))
