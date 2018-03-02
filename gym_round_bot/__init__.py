from gym.envs.registration import register

register(
	id='RoundBot-v0',
	entry_point='gym_round_bot.envs:RoundBotEnv',
	max_episode_steps=100,
	reward_threshold=25.0,
)
