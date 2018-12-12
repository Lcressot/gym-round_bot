import sys, os
from setuptools import setup

setup(
	name='gym_round_bot',
	version='0.0.1',    
	install_requires=['numpy>=1.10.4','pyglet>=1.2.0','scipy', 'pillow' ],
	entry_point='gym_round_bot.envs',
	author='Loic Cressot',
    author_email="Lcressot@gmail.com",
    description="OpenAI gym environment for robotic simulation. Simple round bot driving in a 3D maze-type world with walls. Compatible with both Python 2 and 3.",
    url="https://github.com/Lcressot/gym-round_bot",
    license='MIT',
	classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Developers, Researchers, Students',
    'Topic :: RL :: environment',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
	],
)
