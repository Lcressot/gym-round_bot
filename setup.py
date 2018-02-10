import sys, os
from setuptools import setup
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gym_round_bot/envs'))

setup(
    name='round_bot_py',
    version='0.0.1',
    install_requires=['numpy>=1.10.4','pyglet>=1.2.0',],
    #entry_point='gym_round_bot.envs',
    author='Loic Cressot',
    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers, Researchers, Students',
    'Topic :: RL :: environment',

    # Pick your license as you wish (should match "license" above)
     #'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    ],
)

setup(
	name='gym_round_bot',
	version='0.0.1',
	install_requires=['round_bot_py>=0.0.1','numpy>=1.10.4'],
	#entry_point='gym_round_bot.envs',
	author='Loic Cressot',
	classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers, Researchers, Students',
    'Topic :: RL :: environment',

    # Pick your license as you wish (should match "license" above)
     #'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
	],
)