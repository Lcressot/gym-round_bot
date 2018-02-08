import sys, os
from setuptools import setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gym_round_bot'))

setup(name='gym_round_bot',
      version='0.0.1',
      install_requires=['numpy>=1.10.4','pyglet>=1.2.0',]
)