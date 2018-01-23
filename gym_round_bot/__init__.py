from gym.envs.registration import register

register(
    id='round_bot-V0',
    entry_point='gym_round_bot.envs:Round_botEnv',
)
