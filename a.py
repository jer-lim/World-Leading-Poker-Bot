from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from callbot import CallBot
from scaramucci import BootStrapBot

#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=10)



config.register_player(name="f1", algorithm=CallBot())
config.register_player(name="FT2", algorithm=BootStrapBot())


game_result = start_poker(config, verbose=0)
print("Reference bot:" + str(game_result['players'][0]['stack']))
print("New bot:" + str(game_result['players'][1]['stack']))