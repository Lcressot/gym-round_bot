import round_bot_model
import os

"""
    This file allows to build worlds
"""

def build_rb1_world(model):
    """
    Builds a simple rectangle planar world with walls around
    Return : texture path, world information
    """
    # load texture in current directory
    block_texture_path = os.path.dirname(__file__) + '/texture.png'
    robot_texture_path = os.path.dirname(__file__) + '/robot.png'
    texture_paths = {'brick':block_texture_path, 'robot':robot_texture_path}

    GRASS = round_bot_model.Block.tex_coords((1, 0), (0, 1), (0, 0))
    MUD = round_bot_model.Block.tex_coords((0, 1), (0, 1), (0, 1))
    SAND = round_bot_model.Block.tex_coords((1, 1), (1, 1), (1, 1))
    BRICK = round_bot_model.Block.tex_coords((2, 0), (2, 0), (2, 0))
    STONE = round_bot_model.Block.tex_coords((2, 1), (2, 1), (2, 1))
    BOT = round_bot_model.Block.tex_coords((0, 0), (0, 1), (0, 1))

    n = 20  # 1/2 width and depth of world
    hwalls = 4.5 # heigh of walls
    wwalls = 2*n # width of walls
    dwalls = 2 # # depth of walls

    bot_diameter = 1
    bot_height = 1

    #ground block
    model.add_block( (0, -3, 0, 2*n, 6, 2*n, 0.0, 0.0, 0.0), GRASS)
    #back wall
    model.add_block( (0, hwalls/2, -n, wwalls, hwalls, dwalls, 0.0, 0.0, 0.0), STONE)
    #front wall
    model.add_block( (0, hwalls/2, n, wwalls, hwalls, dwalls, 0.0, 0.0, 0.0), BRICK)
    #left wall
    model.add_block( (-n, hwalls/2, 0, dwalls, hwalls, wwalls, 0.0, 0.0, 0.0), SAND)
    #right wall
    model.add_block( (n, hwalls/2, 0, dwalls, hwalls, wwalls, 0.0, 0.0, 0.0), MUD)

    #robot block, set initial height to bot_heigh/2 + small offset to avoid ground collision
    model.add_block( (0, bot_height/2.0+0.1, 0, 2*bot_diameter, bot_height, 2*bot_diameter, 0.0, 0.0, 0.0), BOT, block_type='robot')

    world_info = {  'width' : 2*n,
                    'depth' : 2*n,
    }

    return texture_paths, world_info
