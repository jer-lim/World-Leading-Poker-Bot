import sys
sys.path.insert(0, './pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import multiprocessing
from multiprocessing import Process, Queue

from httplib import HTTPSConnection
import json
import copy

""" =========== *Remember to import your agent!!! =========== """
from random_player import RandomPlayer
from scaramucci import BootStrapBot
from our_player import OurPlayer
from our_player_no_mwu import OurPlayerNoMwu
""" ========================================================= """

host = "therake.is-under.dev"

min_game = 10
max_round = 100
initial_stack = 10000
smallblind_amount = 20
config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)
# Register players
config.register_player(name="agent1", algorithm=OurPlayerNoMwu())
config.register_player(name="agent2", algorithm=BootStrapBot())


def main():
	
	current_iteration = -1
	current_weight = -1
	test = get_test()
	test_count = 0
	while True:
		if test['iteration'] > current_iteration or test['weight'] > current_weight:
			weights = get_weights()
			current_iteration = test['iteration']
			current_weight = test['weight']
		performance = do_test(weights, test)
		print(performance)
		test['result'] = performance
		test_count += 1
		if test_count % 100 == 0:
			print(str(test_count) + " bitcoins mined so far.")
		test = post_result(test)


def get_weights():
	conn = HTTPSConnection(host)
	conn.request("GET", "/weights");
	response = conn.getresponse()
	weights = json.loads(response.read(9999))
	conn.close()
	print("Fetched weights from server: " + str(weights))
	return weights

def get_test():
	conn = HTTPSConnection(host)
	conn.request("GET", "/test");
	response = conn.getresponse()
	test = json.loads(response.read(9999))
	conn.close()
	print("Test iteration " + str(test['iteration']) + " w" + str(test['weight']) + " value " + str(test['testValue']) + ": ")
	return test

def post_result(result):
	conn = HTTPSConnection(host)
	conn.request("POST", "/submit", json.dumps(result))
	response = conn.getresponse()
	test = json.loads(response.read(9999))
	conn.close()
	sys.stdout.write("Test iteration " + str(test['iteration']) + " w" + str(test['weight']) + " value " + str(test['testValue']) + ": ")
	return test

def do_test(weights, test):

	weights = copy.deepcopy(weights)
	weight = test['weight']
	value = test['testValue']
	weights[weight] = value

	# Configuring other weights
	config.players_info[0]['algorithm'].w = weights

	# Start playing num_game games
	agent1_pot = 0
	agent2_pot = 0

	# init count of games and threads
	return_queue = Queue()
	num_threads = multiprocessing.cpu_count() - 1
	games = min_game + num_threads - (min_game % num_threads)
	while games > 0:
		# start a thread for each remaining game up to threadcount limit
		threads = []
		game_runners = []
		for i in range(0, num_threads):
			if games > 0:
				games -= 1
				game_runners += [GameRunner(config, return_queue)]
				threads += [Process(target = game_runners[i].start_game)]
				threads[i].start()

		# join all threads
		for i in range(0, len(threads)):
			threads[i].join()

		# process returned data
		while not return_queue.empty():
			result = return_queue.get()
			agent1_pot = agent1_pot + result[0]
			agent2_pot = agent2_pot + result[1]

	performance = agent1_pot - agent2_pot
	return performance

class GameRunner(object):
    def __init__(self, config, return_queue):
        self.config = config
        self.return_queue = return_queue

    def start_game(self):
        game_result = start_poker(self.config, verbose=0)
        result = (game_result[0]['players'][0]['stack'], game_result[0]['players'][1]['stack'])
        self.return_queue.put(result)

main()