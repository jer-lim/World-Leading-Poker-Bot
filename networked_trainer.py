import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import multiprocessing
from multiprocessing import Process, Queue

from httplib import HTTPSConnection
import json
import copy
import socket
import time
import random

""" =========== *Remember to import your agent!!! =========== """
from random_player import RandomPlayer
from scaramucci import BootStrapBot
from our_player import OurPlayer
from our_player_no_mwu import OurPlayerNoMwu
from hand_strength import HandStrengthBot
""" ========================================================= """

host = "therake.is-under.dev"

max_round = 100
initial_stack = 10000
smallblind_amount = 20


def main():
	sleep_time = float(random.randrange(0, 100, 1)) / 10
	print("Waiting for " + str(sleep_time))
	time.sleep(sleep_time)
	while True:
		try:
			current_iteration = -1
			current_weight = -1
			test = get_test()
			test_count = 0
			while True:
				benchmark = get_benchmark()
				if benchmark is not None:
					sys.stdout.write("Benchmarking iteration " + str(benchmark['iteration1']) + " with " + str(benchmark['iteration2']) + ": ")
					weights1 = benchmark['weights1']
					weights2 = benchmark['weights2']
					benchmark_min_game = benchmark['min_games']
					performance = do_benchmark(weights1, weights2, benchmark_min_game)
					print(performance)
					benchmark['result'] = performance
					post_benchmark(benchmark)
					test = get_test()

				if test['iteration'] > current_iteration or test['weight'] > current_weight:
					weights = get_weights()
					current_iteration = test['iteration']
					current_weight = test['weight']
					min_game = test['minGames']
				performance = do_test(weights, test, min_game, current_iteration, current_weight)
				print(performance)
				test['result'] = performance
				test['tester'] = socket.gethostname()
				test_count += 1
				if test_count % 100 == 0:
					print(str(test_count) + " bitcoins mined so far.")
				test = post_result(test)

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Some error occurred, restarting training.")
		


def get_weights():
	conn = HTTPSConnection(host)
	conn.request("GET", "/13/weights");
	response = conn.getresponse()
	weights = json.loads(response.read(9999))
	conn.close()
	print("Fetched weights from server: " + str(weights))
	return weights

def get_test():
	conn = HTTPSConnection(host)
	conn.request("GET", "/13/test");
	response = conn.getresponse()
	test = json.loads(response.read(9999))
	conn.close()
	print_test(test)
	return test

def post_result(result):
	conn = HTTPSConnection(host)
	conn.request("POST", "/13/submit", json.dumps(result))
	response = conn.getresponse()
	test = json.loads(response.read(9999))
	conn.close()
	print_test(test)
	return test

def get_status():
	conn = HTTPSConnection(host)
	conn.request("GET", "/13/status");
	response = conn.getresponse()
	status = json.loads(response.read(9999))
	conn.close()
	return status

def get_benchmark():
	conn = HTTPSConnection(host)
	conn.request("GET", "/13/benchmark/" + socket.gethostname());
	response = conn.getresponse()
	benchmark = json.loads(response.read(9999))
	conn.close()
	return benchmark

def post_benchmark(benchmark):
	conn = HTTPSConnection(host)
	conn.request("POST", "/13/benchmark", json.dumps(benchmark))
	conn.close()

def print_test(test):
	sys.stdout.write("Test iteration " + str(test['iteration']) + " w" + str(test['weight']) + " value " + str(test['testValue']) + " (" + str(test['minGames']) + " games): ")

def do_test(weights, test, min_game, current_iteration, current_weight):

	new_weights = copy.deepcopy(weights)
	weight = test['weight']
	value = test['testValue']
	new_weights[weight] = value

	config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)
	# Register players
	config.register_player(name="agent1", algorithm=OurPlayerNoMwu(new_weights))
	config.register_player(name="agent2", algorithm=OurPlayerNoMwu(weights))

	# Start playing num_game games
	agent1_pot = 0
	agent2_pot = 0

	# init count of games and threads
	return_queue = Queue()
	num_threads = multiprocessing.cpu_count() - 1
	games = min_game + num_threads - (min_game % num_threads)
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
				threads[i].start()

		# join all threads
		for i in range(0, len(threads)):
			threads[i].join()

		# process returned data
		while not return_queue.empty():
			result = return_queue.get()
			agent1_pot = agent1_pot + result[0]
			agent2_pot = agent2_pot + result[1]

		status = get_status()
		if status['iteration'] != current_iteration or status['weight'] != current_weight:
			print("Current iteration/weight changed. Stopping current training.")
			games = 0;

	performance = (agent1_pot - agent2_pot) / num_games_ran
	return performance

def do_benchmark(weights1, weights2, min_game):
	config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)
	# Register players
	config.register_player(name="agent1", algorithm=OurPlayerNoMwu(weights1))
	config.register_player(name="agent2", algorithm=OurPlayerNoMwu(weights2))

	# Start playing num_game games
	agent1_pot = 0
	agent2_pot = 0

	# init count of games and threads
	return_queue = Queue()
	num_threads = multiprocessing.cpu_count() - 1
	games = min_game + num_threads - (min_game % num_threads)
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
				threads[i].start()

		# join all threads
		for i in range(0, len(threads)):
			threads[i].join()

		# process returned data
		while not return_queue.empty():
			result = return_queue.get()
			agent1_pot = agent1_pot + result[0]
			agent2_pot = agent2_pot + result[1]

	performance = (agent1_pot - agent2_pot) / num_games_ran
	return performance

class GameRunner(object):
    def __init__(self, config, return_queue):
        self.config = config
        self.return_queue = return_queue

    def start_game(self):
        game_result = start_poker(self.config, verbose=0)
        result = (game_result['players'][0]['stack'], game_result['players'][1]['stack'])
        self.return_queue.put(result)

main()