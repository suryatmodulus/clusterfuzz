# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generate strategy pool for launcher based on strategy probabilities.

Decides the set strategies to be considered by the launcher. Note
that because of compatability issues, the exact set of strategies
generated here may be modified in the launcher before being launched."""

from bot.fuzzers import engine_common
from bot.fuzzers import strategy


class StrategyPool(object):
  """Object used to keep track of which strategies the launcher should attempt
  to enable."""

  def __init__(self):
    """Empty set representing empty strategy pool."""
    self.strategy_names = set()

  def add_strategy(self, strategy_tuple):
    """Add a strategy into our existing strategy pool."""
    self.strategy_names.add(strategy_tuple.name)

  def do_strategy(self, strategy_tuple):
    """Boolean value representing whether or not a strategy is in our strategy
    pool."""
    return strategy_tuple.name in self.strategy_names


def choose_generator(strategy_pool):
  """Chooses whether to use radamsa, ml rnn, or no generator and updates the
  strategy pool."""

  radamsa_prob = engine_common.get_strategy_probability(
      strategy.CORPUS_MUTATION_RADAMSA_STRATEGY.name,
      default=strategy.CORPUS_MUTATION_RADAMSA_STRATEGY.probability)

  ml_rnn_prob = engine_common.get_strategy_probability(
      strategy.CORPUS_MUTATION_ML_RNN_STRATEGY.name,
      default=strategy.CORPUS_MUTATION_ML_RNN_STRATEGY.probability)

  if engine_common.decide_with_probability(radamsa_prob + ml_rnn_prob):
    if engine_common.decide_with_probability(
        radamsa_prob / (radamsa_prob + ml_rnn_prob)):
      strategy_pool.add_strategy(strategy.CORPUS_MUTATION_RADAMSA_STRATEGY)
    else:
      strategy_pool.add_strategy(strategy.CORPUS_MUTATION_ML_RNN_STRATEGY)


def do_strategy(strategy_tuple):
  """Return whether or not to use a given strategy."""
  return engine_common.decide_with_probability(
      engine_common.get_strategy_probability(strategy_tuple.name,
                                             strategy_tuple.probability))


def generate_strategy_pool():
  """Return a strategy pool representing a random selection of strategies for
  launcher to consider."""
  pool = StrategyPool()

  # Decide whether to include radamsa, ml rnn, or no generator (mutually
  # exclusive).
  choose_generator(pool)

  # Decide whether or not to include remaining strategies.
  if engine_common.do_corpus_subset():
    pool.add_strategy(strategy.CORPUS_SUBSET_STRATEGY)
  if do_strategy(strategy.RANDOM_MAX_LENGTH_STRATEGY):
    pool.add_strategy(strategy.RANDOM_MAX_LENGTH_STRATEGY)
  if do_strategy(strategy.RECOMMENDED_DICTIONARY_STRATEGY):
    pool.add_strategy(strategy.RECOMMENDED_DICTIONARY_STRATEGY)
  if do_strategy(strategy.VALUE_PROFILE_STRATEGY):
    pool.add_strategy(strategy.VALUE_PROFILE_STRATEGY)
  if do_strategy(strategy.FORK_STRATEGY):
    pool.add_strategy(strategy.FORK_STRATEGY)
  if do_strategy(strategy.MUTATOR_PLUGIN_STRATEGY):
    pool.add_strategy(strategy.MUTATOR_PLUGIN_STRATEGY)

  return pool