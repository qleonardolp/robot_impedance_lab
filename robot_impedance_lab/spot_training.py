# Copyright 2026 qleonardolp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spot_env import SpotROS2Env

from stable_baselines3 import SAC
from stable_baselines3.common.env_checker import check_env

env = SpotROS2Env()
# check custom environment and output additional warnings if needed
check_env(env)


model = SAC('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=1_000_000, log_interval=4)
model.save('sac_spot_walking')

obs, info = env.reset()
while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()
