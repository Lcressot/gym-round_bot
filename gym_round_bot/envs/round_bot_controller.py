
import round_bot_model
import math

"""
    This file defines the Controller class for controlling the robot
"""
	
class Controller(object):
	def __init__(self, model, controllerType):
		self.model = model
		self.controllerType = controllerType # type of actions : ex int for integers, tuple2 for (x,y) tuples, float...
		self.action_meaning = {} # dictionnary to map actions number to their string meaning
		self.actions = {} # dictionnary to map actions number to their code meaning

	def step(self, action):
		"""
		Controls the model's robot to perform the action
		Execute code containded in actions dictionnary
		"""
		exec(self.actions[action])


class Simple_ThetaSpeed_Controller(Controller):
	"""
	This class controls the robot with fixed dtheta rotations and fixed speed forward move
	"""
	def __init__(self, model, dtheta, speed):
		super(Simple_ThetaSpeed_Controller,self).__init__(model,"int")
		self.dtheta = dtheta
		self.model.walking_speed = speed
		self.action_meaning = "\
		0 : MOVEFORWARD\
        1 : STOP\
        2 : ROTATERIGHT\
        3 : ROTATELEFT\
        "
		
		self.actions = {
		0 : "self.model.strafe[0]=-1", #-1 is forward
        1 : "self.model.strafe[0]=0",
        2 : "self.model.change_robot_rotation(self.dtheta,0)",
        3 : "self.model.change_robot_rotation(-self.dtheta,0)",
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
	def __init__(self, model, speed, xzrange):
		super(Simple_XZ_Controller,self).__init__(model,"tuple2")
		self.initial_speed = speed
		self.xzrange = xzrange # how many maximum xz units you can move at once
		self.action_meaning = "[x, z] 2-tuple with x and z between -xzrange and +xzrange"
		self.actions = { (x,z) : "self.model.strafe="+str([x-xzrange,z-xzrange])+"; self.model.walking_speed=self.initial_speed*"+str(math.sqrt((x-xzrange)**2+(z-xzrange)**2)) for x in range(0,2*xzrange+1) for z in range(0,2*xzrange+1) }

	@property
	def speed(self, s):
		self.initial_speed = s

	@property
	def speed(self):
		return self.initial_speed

