
import round_bot_model


"""
    This file defines the Controller class for controlling the robot
"""
	
class Controller(object):
	def __init__(self, model, controllerType):
		self.model = model
		self.controllerType = controllerType
		self.action_meaning = {} # dictionnary to map actions number to their string meaning
		self.actions = {} # dictionnary to map actions number to their code meaning

	def step(self, action):
		"""
		Controls the model's robot to perform the action
		Execute code containded in actions dictionnary
		"""
		exec(self.actions[action])


class Simple_TetaSpeed_Controller(Controller):
	"""
	This class controls the robot with fixed dteta rotations and fixed speed forward move
	"""
	def __init__(self, model, dteta, speed):
		super(Simple_TetaSpeed_Controller,self).__init__(model,"Simple_TetaSpeed")
		self.dteta = dteta
		self.model.walking_speed = speed
		self.action_meaning = {
		0 : "MOVEFORWARD",
        1 : "STOP",
        2 : "ROTATERIGHT",
        3 : "ROTATELEFT", 
		}
		self.actions = {
		0 : "self.model.strafe[0]=-1", #-1 is forward
        1 : "self.model.strafe[0]=0",
        2 : "self.model.change_robot_rotation(self.dteta,0)",
        3 : "self.model.change_robot_rotation(-self.dteta,0)",
		}

	@property
	def speed(self, s):
		self.model.walking_speed = s

	@property
	def speed(self):
		return self.model.walking_speed



class Simple_XZ_Controller(Controller):
	"""
	This class controls the robot to move on (oXZ) plan, always looking in the same direction
	"""
	def __init__(self, model, speed):
		super(Simple_XZ_Controller,self).__init__(model,"Simple_XZ")
		self.model.walking_speed = speed
		self.action_meaning = {
		0 : "MOVE FOWARD",
        1 : "MOVE BACKWARD",
        2 : "MOVE RIGHT",
        3 : "MOVE LEFT", 
		}
		self.actions = {
		0 : "self.model.strafe[1]=0; self.model.strafe[0]=-1", #-1 is forward
        1 : "self.model.strafe[1]=0; self.model.strafe[0]=1",
        2 : "self.model.strafe[0]=0; self.model.strafe[1]=1", 
        3 : "self.model.strafe[0]=0; self.model.strafe[1]=-1",
		}

	@property
	def speed(self, s):
		self.model.walking_speed = s

	@property
	def speed(self):
		return self.model.walking_speed
