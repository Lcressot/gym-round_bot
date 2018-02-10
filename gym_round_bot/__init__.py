from gym.envs.registration import register

# register(
#      id='RoundBot-v0',
#      entry_point='gym_round_bot.envs:RoundBotEnv',
# )
register(
     id='RoundBot-extrahard-v0',
     entry_point='gym_round_bot.envs:RoundBotExtraHardEnv',
)