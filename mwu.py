import math

# Multiplicative Weights Update (MWU) algorithm
## Depending on how good our previously chosen action (Call, Raise, Fold),
## our function will penalise accordingly.
action_weights = [1, 1, 1] # Initialise their weights to 1: [Call, Raise, Fold] accordingly
def MWU(action_weights, factor_to_punish, punish_constant, loss): #factor_to_punish should be the previous move made
    punish_rate = math.exp(-punish_constant*loss)
    if factor_to_punish == "Call":
        action_weights = [action_weights[0]*punish_rate, action_weights[1], action_weights[2]]
    elif factor_to_punish == "Raise":
        action_weights = [action_weights[0], action_weights[1]*punish_rate, action_weights[2]]
    elif factor_to_punish == "Fold":
        action_weights = [action_weights[0], action_weights[1], action_weights[2]*punish_rate]
    else:
        pass
    return action_weights
    
