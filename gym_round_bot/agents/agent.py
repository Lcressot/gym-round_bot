class Agent(object):
    """Agent's interface"""
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done):
        raise Exception("not implemented error")


class RandomAgent(Agent):
    """The world's simplest agent!"""
    def __init__(self, action_space):
        super(RandomAgent,self).__init__(action_space)

    def act(self, observation, reward, done):
        return self.action_space.sample()

class GreedyAgent(Agent):
    """The world's simplest agent!"""
    def __init__(self, action_space):
        super(GreedyAgent,self).__init__(action_space)

    def act(self, observation, reward, done,Q):
	
        return self.action_space.sample()
	
	
def make(action_space,policy='RandomAgent',info={}):
    if policy=='RandomAgent':
	return RandomAgent(action_space)
    elif policy=='GreedyAgent':
	return GreedyAgent(action_space)
    else:
	raise Exception("Unknown policy in agent.make: " +policy)
