import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import time
from argparse import ArgumentParser
import multiprocessing
from multiprocessing import Process, Queue


""" =========== *Remember to import your agent!!! =========== """
from random_player import RandomPlayer
from raise_player import RaisedPlayer
from scaramucci import BootStrapBot
from our_player_no_mwu import OurPlayerNoMwu
from Group01Player import Group01Player
from hand_strength import HandStrengthBot
# from smartwarrior import SmartWarrior
""" ========================================================= """

""" Example---To run testperf.py with random warrior AI against itself. 

$ python testperf.py -n1 "Random Warrior 1" -a1 RandomPlayer -n2 "Random Warrior 2" -a2 RandomPlayer
"""

def testperf(agent_name1, agent1, agent_name2, agent2):

	# Init to play 500 games of 1000 rounds
	num_game = 100
	max_round = 1000
	initial_stack = 10000
	smallblind_amount = 20

	# Init pot of players
	agent1_pot = 0
	agent2_pot = 0

	# Setting configuration
	config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)
	
	# Register players
	config.register_player(name=agent_name1, algorithm=OurPlayerNoMwu([0.8425,2.3519,0.19,1.6801,0.7491,0.3869,0.855,0.7166,-0.24,0.085,-0.21,0.035,0.52,0.16,0.18]))
	#config.register_player(name=agent_name2, algorithm=OurPlayerNoMwu([0.63,0.83,0.4,1,0.75,0.49,0.38,0.87,0.21,0,0,0.14,0.44]))
	config.register_player(name=agent_name2, algorithm=Group01Player([0.8425,2.3519,0.19,1.6801,0.7491,0.3869,0.855,0.7166,-0.24,0.085,-0.21,0.035,0.52,0.16,0.18]))
	# config.register_player(name=agent_name1, algorithm=agent1())
	# config.register_player(name=agent_name2, algorithm=agent2())
	
	return_queue = Queue()
	num_threads = multiprocessing.cpu_count() - 1
	games = num_game
	num_games_ran = 0
	while games > 0:
		# start a thread for each remaining game up to threadcount limit
		threads = []
		game_runners = []
		for i in range(0, num_threads):
			if games > 0:
				games -= 1
				num_games_ran += 1
				game_runners += [GameRunner(config, return_queue)]
				threads += [Process(target = game_runners[i].start_game)]
				print("Game Number " + str(num_games_ran))
				threads[i].start()

		# join all threads
		for i in range(0, len(threads)):
			threads[i].join()

		# process returned data
		while not return_queue.empty():
			result = return_queue.get()
			agent1_pot = agent1_pot + result[0]
			agent2_pot = agent2_pot + result[1]
			print(str(agent1_pot) + " vs " + str(agent2_pot))

	print("\n After playing {} games of {} rounds, the results are: ".format(num_game, max_round))
	# print("\n Agent 1's final pot: ", agent1_pot)
	print("\n " + agent_name1 + "'s final pot: ", agent1_pot)
	print("\n " + agent_name2 + "'s final pot: ", agent2_pot)

	# print("\n ", game_result)
	# print("\n Random player's final stack: ", game_result['players'][0]['stack'])
	# print("\n " + agent_name + "'s final stack: ", game_result['players'][1]['stack'])

	if (agent1_pot<agent2_pot):
		print("\n Congratulations! " + agent_name2 + " has won.")
	elif(agent1_pot>agent2_pot):
		print("\n Congratulations! " + agent_name1 + " has won.")
		# print("\n Random Player has won!")
	else:
		Print("\n It's a draw!") 

class GameRunner(object):
    def __init__(self, config, return_queue):
        self.config = config
        self.return_queue = return_queue

    def start_game(self):
        game_result = start_poker(self.config, verbose=0)
        result = (game_result['players'][0]['stack'], game_result['players'][1]['stack'])
        self.return_queue.put(result)


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-n1', '--agent_name1', help="Name of agent 1", default="Your agent", type=str)
    parser.add_argument('-a1', '--agent1', help="Agent 1", default=RandomPlayer())    
    parser.add_argument('-n2', '--agent_name2', help="Name of agent 2", default="Your agent", type=str)
    parser.add_argument('-a2', '--agent2', help="Agent 2", default=RandomPlayer())    
    args = parser.parse_args()
    return args.agent_name1, args.agent1, args.agent_name2, args.agent2

if __name__ == '__main__':
	name1, agent1, name2, agent2 = parse_arguments()
	start = time.time()
	testperf(name1, agent1, name2, agent2)
	end = time.time()

	print("\n Time taken to play: %.4f seconds" %(end-start))
