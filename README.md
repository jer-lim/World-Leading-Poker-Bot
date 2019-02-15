## Term Project

### Set up environment
using the conda or pyenv

- conda create -n cs3243 python=2.7
- source activate cs3243

replace the cs3243 with whatever name you want
https://conda.io/docs/index.html

pip install PyPokerEngine  
https://ishikota.github.io/PyPokerEngine/



testing installmement:

```
import pypokerengine   
print("hello world")
```



### Create your own player
#### Example player

```

class RaisedPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    #Implement your code
    return action

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass
```
#### Example Game
The example game is in the example.py

#### Information for the game
```valid_actions```: vaild action list


```
[
    { "action" : "fold"  },
    { "action" : "call" },
    { "action" : "raise" }
]
OR 
[
    {"action": "fold"},
    {"action": "call"}
]
```

In the limited version, user only allowed to raise for four time in one round game.    
In addition, in each street (preflop,flop,turn,river),each player only allowed to raise for four times.

Other information is similar to the PyPokerEngine,please check the detail about the parameter [link](https://github.com/ishikota/PyPokerEngine/blob/master/AI_CALLBACK_FORMAT.md)

#### Additional notes for coding player
1. receive_game_start_message is called at the start of the game before preflop, contains details about users, rounds, etc.
2. receive_round_start_message is called before start of round, contains information about `face down cards`.
3. receive_street_start_message is called before each street with current details about game state. i.e. street = flop, turn or river
4. receive_game_start_message is called after *every* move
5. receive_round_result_message called after every end of round i.e. win/lose
