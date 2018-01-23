import round_bot_model as tb_model


"""
    This file allows to build worlds
"""

def build_tb1_world(model):
	"""
	Builds a simple rectangle planar world with walls around
	Return : texture path, world information
	"""

	texture_path = 'texture.png'

	GRASS = tb_model.tex_coords((1, 0), (0, 1), (0, 0))
	MUD = tb_model.tex_coords((0, 1), (0, 1), (0, 1))
	SAND = tb_model.tex_coords((1, 1), (1, 1), (1, 1))
	BRICK = tb_model.tex_coords((2, 0), (2, 0), (2, 0))
	STONE = tb_model.tex_coords((2, 1), (2, 1), (2, 1))

	n = 20  # 1/2 width and depth of world
	hwalls = 4.5 # heigh of walls
	wwalls = 2*n # width of walls
	dwalls = 2 # # depth of walls

	#ground block
	model.add_block( (0, -3, 0, 2*n, 6, 2*n), GRASS, immediate=False)
	#back wall
	model.add_block( (0, hwalls/2, -n, wwalls, hwalls, dwalls), STONE, immediate=False)
	#front wall
	model.add_block( (0, hwalls/2, n, wwalls, hwalls, dwalls), BRICK, immediate=False)
	#left wall
	model.add_block( (-n, hwalls/2, 0, dwalls, hwalls, wwalls), SAND, immediate=False)
	#right wall
	model.add_block( (n, hwalls/2, 0, dwalls, hwalls, wwalls), MUD, immediate=False)

	world_info = {  'width' : 2*n,
					'depth' : 2*n,
	}

	return texture_path, world_info