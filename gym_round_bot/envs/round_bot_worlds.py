#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018

    This file allows to build worlds
    TODO : replace this file by a .json loader and code worlds in .json
""" 

# WARNING : don't (from round_bot_py import round_bot_model) here to avoid mutual imports !

import os

def _texture_path(texture_bricks_name):
    """
    Parameter
    ---------
    texture_bricks_name : str
        name of the world main texture 

    Return
    ------
    texture_path: (str) path corresponding to the texture_bricks_name

    Raises
    ------
    ValueError : raised if texture_bricks_name is unkwnonw
    """
    if texture_bricks_name == 'minecraft':
        return '/textures/texture_minecraft.png'
    elif texture_bricks_name == 'minecraft+':
        return '/textures/texture_minecraft+.png'
    elif texture_bricks_name == 'colours':
        return '/textures/texture_colours.png'
    else :
        raise ValueError('Unknown texture name '+ texture_bricks_name + ' in loading world')


def _build_rb1_default_world(model, texture_bricks_name, width=20, hwalls=4, dwalls=1,                    
                            texture_robot='/textures/robot.png',
                            texture_visualisation='/textures/visualisation.png',
                            wall_reward=-1,
                            ):
    """
    Builds a simple rectangle planar world with walls around

    Parameters
    ----------
    - model : (round_bot_model.Model) model to load world in
    - texture_bricks_name : (str) name of the texture for the bricks
    - width : (int) width of the world
    - hwalls : (int) heigh of walls    
    - dwalls: (int) depth of walls
    - texture_bricks, texture_robot, texture_visualisation : (string)
        paths for texture image of bricks, robot and visualisation
    - wall_reward : (float) reward for wall collision

    Returns
    -------
    world information
    """
    texture_bricks = _texture_path(texture_bricks_name)
    
    # TODO : better import would be global and without "from" but doesn't work for the moment
    from gym_round_bot.envs import round_bot_model 
    # create textures coordinates
    GRASS = round_bot_model.Block.tex_coords((1, 0), (0, 1), (0, 0))
    MUD = round_bot_model.Block.tex_coords((0, 1), (0, 1), (0, 1))
    SAND = round_bot_model.Block.tex_coords((1, 1), (1, 1), (1, 1))
    BRICK = round_bot_model.Block.tex_coords((2, 0), (2, 0), (2, 0))
    STONE = round_bot_model.Block.tex_coords((2, 1), (2, 1), (2, 1))

    # wwalls = width of walls
    wwalls = width
    n = width/2.0  # 1/2 width and depth of this (squarred) world
    wr = width/3.0 # wr width of reward area

    # get texture paths in current directory
    brick_texture_path = os.path.dirname(__file__) + texture_bricks
    robot_texture_path = os.path.dirname(__file__) + texture_robot
    visualisation_texture_path = os.path.dirname(__file__) + texture_visualisation
    texture_paths = {'brick':brick_texture_path,
                     'robot':robot_texture_path,
                     'visualisation':visualisation_texture_path }   

    # Build gound block
    model.add_block( (0, -3, 0, 2*n, 6, 2*n, 0.0, 0.0, 0.0), GRASS)

    # Build wall blocks with negative reward on collision
    #back wall
    model.add_block( (0, hwalls/2, -n, wwalls, hwalls, dwalls, 0.0, 0.0, 0.0), STONE, collision_reward = wall_reward)
    #front wall
    model.add_block( (0, hwalls/2, n, wwalls, hwalls, dwalls, 0.0, 0.0, 0.0), BRICK, collision_reward = wall_reward)
    #left wall
    model.add_block( (-n, hwalls/2, 0, dwalls, hwalls, wwalls, 0.0, 0.0, 0.0), SAND, collision_reward = wall_reward)
    #right wall
    model.add_block( (n, hwalls/2, 0, dwalls, hwalls, wwalls, 0.0, 0.0, 0.0), MUD, collision_reward = wall_reward)    

    world_info = {  'width' : 2*n,
                    'depth' : 2*n,
    }

    return texture_paths, world_info



def build_rb1_world(model, texture, width=20, hwalls=4, dwalls=1, wall_reward=-1, goal_reward=10):
    """
    Builds the rb1 world
    """    
    ## first build default world
    texture_paths, world_info = _build_rb1_default_world(model, texture, width=width, hwalls=hwalls, dwalls=dwalls, wall_reward=wall_reward)

    ## then add specs
    from gym_round_bot.envs import round_bot_model
    BOT = round_bot_model.Block.tex_coords((0, 0), (0, 1), (0, 1))
    START = round_bot_model.Block.tex_coords((0, 0), (0, 0), (0, 0))
    REWARD = round_bot_model.Block.tex_coords((0, 1), (0, 1), (0, 1))

    n = width/2.0  # 1/2 width and depth of world
    wwalls = 2*n # width of walls
    wr = width/4.0 # wr width of reward area
   
    # set robot specifications
    bot_diameter = 1
    bot_height = 1

    # Build reward block in the corner
    model.add_block( (n-(wr/2+dwalls/2), bot_height/2.0, -n+(wr/2+dwalls/2), wr, bot_height/3.0, wr, 0.0, 0.0, 0.0), REWARD, block_type='reward', collision_reward = goal_reward)
    # Build robot block, set initial height to bot_heigh/2 + small offset to avoid ground collision
    model.add_block( (0, bot_height/2.0+0.1, 0, 2*bot_diameter, bot_height, 2*bot_diameter, 0.0, 0.0, 0.0), BOT, block_type='robot')
    # add starting areas (the height=0 of block does not matter here, only area of (hwalls-2*dwalls)^2)
    model.add_block( (0, bot_height/2.0+0.1, 0, wwalls-2*dwalls, 0.1, wwalls-2*dwalls, 0.0, 0.0, 0.0), START, block_type='start')

    return texture_paths, world_info



def build_rb1_1wall_world(model, texture, width=20, hwalls=2, dwalls=2, wall_reward=-1, goal_reward=10):
    """
    Builds a simple rectangle planar world with walls around, and 1 wall in the middle
    """
    ## first build default world
    texture_paths, world_info = _build_rb1_default_world(model, texture, width=width, hwalls=hwalls, dwalls=dwalls, wall_reward=wall_reward)

    ## then add specs
    from gym_round_bot.envs import round_bot_model
    BOT = round_bot_model.Block.tex_coords((0, 0), (0, 1), (0, 1))
    START = round_bot_model.Block.tex_coords((0, 0), (0, 0), (0, 0))
    REWARD = round_bot_model.Block.tex_coords((0, 1), (0, 1), (0, 1))
    SAND = round_bot_model.Block.tex_coords((1, 1), (1, 1), (1, 1))

    n = width/2.0  # 1/2 width and depth of world
    wwalls = 2*n # width of walls
    wr = width/4.0 # wr width of reward area
 
    # set robot specifications
    bot_diameter = 1
    bot_height = 1
    
    # middle wall
    model.add_block( (n/2, hwalls/2, -n/4, wwalls/2, hwalls, dwalls, 0.0, 0.0, 0.0), SAND, collision_reward = -1)

    # Build reward block in the corner
    model.add_block( (n-(wr/2+dwalls/2), bot_height/2.0, -n+(wr/2+dwalls/2), wr, bot_height/3.0, wr, 0.0, 0.0, 0.0), REWARD, block_type='reward', collision_reward = 1)
    # Build robot block, set initial height to bot_heigh/2 + small offset to avoid ground collision
    model.add_block( (0, bot_height/2.0+0.1, 0, 2*bot_diameter, bot_height, 2*bot_diameter, 0.0, 0.0, 0.0), BOT, block_type='robot')
    # add starting areas (the height=0 of block does not matter here, only area of (hwalls-2*dwalls)^2)
    model.add_block( (0, bot_height/2.0+0.1, (wwalls-2*dwalls)/4, wwalls-2*dwalls, 0.1, (wwalls-2*dwalls)/2, 0.0, 0.0, 0.0), START, block_type='start')
    model.add_block( ( -(wwalls-2*dwalls)/4, bot_height/2.0+0.1, -(wwalls-2*dwalls)/4, (wwalls-2*dwalls)/2, 0.1, (wwalls-2*dwalls)/2, 0.0, 0.0, 0.0), START, block_type='start')


    return texture_paths, world_info

