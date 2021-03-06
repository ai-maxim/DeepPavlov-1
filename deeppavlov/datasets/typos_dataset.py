"""
Copyright 2017 Neural Networks and Deep Learning lab, MIPT

Licensed inder the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import random

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.dataset import Dataset


@register('typos_dataset')
class TyposDataset(Dataset):
    def split(self, *args, **kwargs):
        """Split all data into train and test

        Args:
            test_ratio (float): ratio of test data to train, from 0. to 1. Defaults to 0.15
        """
        self.train += self.valid + self.test

        test_ratio = args[0] if args else kwargs.get('test_ratio', 0)

        split = int(len(self.train) * test_ratio)

        rs = random.getstate()
        random.setstate(self.random_state)
        random.shuffle(self.train)
        self.random_state = random.getstate()
        random.setstate(rs)

        self.test = self.train[:split]
        self.train = self.train[split:]
        self.valid = []
