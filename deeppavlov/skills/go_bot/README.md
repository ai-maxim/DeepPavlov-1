[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](/LICENSE.txt)
![Python 3.6](https://img.shields.io/badge/python-3.6-green.svg)
![tensorflow 1.4](https://img.shields.io/badge/tensorflow-1.4-green.svg)

# Dialogue Bot for goal-oriented task 
The dialogue bot is based on [[1]](#references) which introduces Hybrid Code Networks (HCNs) that combine an RNN with domain-specific knowledge and system action templates.

![alt text](diagram.png "Goal-oriented bot diagram")
**Diagram 1.** Dotted lines correspond to unrequired (optional) modules, black squares to trained models, trapezes are modules that depend on a dataset and must be provided by software developer.

Here is a simple example of interaction with a trained dialogue bot (can be downloaded with [`deeppavlov/download.py`](../../download.py)):

```
:: 
>> Hello, welcome to the Phystech restaurant system. You can ask for restaurants by area, price range or food type. How may I help you?
:: hi, i want some food
>> What part of town do you have in mind?
:: north of Dolgoprudny
>> Would you like something in the cheap, moderate, or expensive price range?
:: something chep, please
>> "Time to eat" is a nice place in the north of town and the prices are cheap.
:: what kind of food does it serve? 
>> "Time to eat" serves russian food.
:: i like that! give me their address then
>> Sure, "Time to eat" is on Sobina Square, 1/4.
:: and phone number. In case i wanted anything for delivery.
>> The phone number of "Time to eat" is +7(965)173-37-33.
:: I won't need that, but give me their post code too.
>> The post code of "Time to eat" is 141700.
:: nice, thanks!
>> "Time to eat" is a nice place in the centre of town serving tasty creative food.
:: good bye
>> You are welcome!
:: exit
```

## Usage

#### Requirements

To use a go_bot model you should have:
1. (_optional, but recommended_) pretrained named entity recognition model (NER) 
   * config [`deeppavlov/models/ner/config.json`](../../models/ner/config.json) is recommended
2. (_optional, but recommended_) pretrained intents classifier model 
   * config [`deeppavlov/models/classifiers/intents/config_dstc2.json`](../../models/classifiers/intents/config_dstc2.json) is recommended
3. (_optional_) downloaded english fasttext embeddings trained on wiki ([https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki.en.zip](https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki.en.zip))
   * you can use any english embeddings of your choice, but edit go_bot config accordingly
4. pretrained goal-oriented bot model itself 
   * config [`deeppavlov/skills/go_bot/config.json`](config.json) is recommended
   * `slot_filler` section of go_bot's config should match NER's configuration
   * `intent_classifier` section of go_bot's config should match classifier's configuration
   * double-check that corresponding `load_path`s point to NER and intent classifier model files

#### Config parameters:
* `name` always equals to `"go_bot"`
* `train_now` — `true` or `false`(default) depending on whether you are training or using a model _(optional)_
* `num_epochs` — maximum number of epochs during training _(optional)_
* `val_patience` — stop training after `val_patience` epochs without improvement of turn accuracy on validation dialogs _(optional)_
* `template_path` — map from actions to text templates for response generation
* `use_action_mask` — in case of true, action mask is applied to network output
* `vocabs` — vocabs used in model
   * `word_vocab` — vocabulary of tokens from context utterances
      * `train_now` — whether to train it on the current dataset, or use pretrained
      * `name` — `"default_vocab"` (for vocabulary's implementation see [`deeppavlov.core.data.vocab`](../../core/data/vocab.py))
      * `inputs` — `[ "x" ]`,
      * `level` — `"token"`,
      * `tokenize` — `true`,
      * `save_path` — `"../download/vocabs/token.dict"`
      * `load_path` — `"../download/vocabs/token.dict"`
* `tokenizer` — one of tokenizers from [`deeppavlov.models.tokenizers`](../../models/tokenizers) module
   * `name` — tokenizer name
   * other arguments specific to your tokenizer
* `bow_encoder` — one of bag-of-words encoders from [`deeppavlov.models.encoders.bow`](../../models/encoders/bow) module
   * `name` — encoder name
   * other arguments specific to your encoder
* `embedder` — one of embedders from [`deeppavlov.models.embedders`](../../models/embedders) module
   * `name` — embedder name (`"fasttext"` recommended, see [`deeppavlov.models.embedders.fasttext_embedder`](../../models/embedders/fasttext_embedder.py))
   * `mean` — must be set to `true`
   * other arguments specific to your embedder
* `tracker` — dialogue state tracker from [`deeppavlov.models.trackers`](../../models/trackers)
   * `name` — tracker name (`"default_tracker"` or `"featurized_tracker"` recommended)
   * `slot_vals` — list of slots that should be tracked
* `network` — reccurent network that handles dialogue policy management
   * `name` — `"go_bot_rnn"`,
   * `train_now` — `true` or `false`(default) depending on whether you are training or using a model _(optional)_
   * `save_path` — name of the file that the model will be saved to
   * `load_path` — name of the file that the model will be loaded from
   * `learning_rate` — learning rate during training
   * `hidden_dim` — hidden state dimension
   * `obs_size` — input observation size (must be set to number of `bow_embedder` features, `embedder` features, `intent_classifier` features, context features(=2) plus `tracker` state size plus action size)
   * `action_size` — output action size
* `slot_filler` — model that predicts slot values for a given utterance
   * `name` — slot filler name (`"dstc_slotfilling"` recommended, for implementation see [`deeppavlov.models.ner`](../../models/ner))
   * other slot filler arguments
* `intent_classifier` — model that outputs intents probability distribution for a given utterance
   * `name` — intent classifier name (`"intent_model"` recommended, for implementation see [`deeppavlov.models.classifiers.intents`](../../models/classifiers/intents))
   * classifier's other arguments
* `debug` — whether to display debug output (defaults to `false`) _(optional)_

For a working exemplary config see [`deeeppavlov/skills/go_bot/config.json`](config.json) (model without embeddings).

A minimal model without `slot_filler`, `intent_classifier` and `embedder` is configured in [`deeeppavlov/skills/go_bot/config_minimal.json`](config_minimal.json).

A full model (with fasttext embeddings) configuration is in [`deeeppavlov/skills/go_bot/config_all.json`](config_all.json)

#### Usage example
* To infer from a pretrained model with config path equal to `path/to/config.json`:
```python
from deeppavlov.core.commands.infer import build_model_from_config
from deeppavlov.core.commands.utils import set_usr_dir
from deeppavlov.core.common.file import read_json

CONFIG_PATH = 'path/to/config.json'

set_usr_dir(CONFIG_PATH)
model = build_model_from_config(read_json(CONFIG_PATH))

utterance = ""
while utterance != 'quit':
    print(">> " + model.infer(utterance))
    utterance = input(':: ')
```

* To interact via command line use [`deeppavlov/deep.py`](../../deep.py) script:
```bash
cd deeppavlov
python3 deep.py interact path/to/config.json
```

## Training

#### Config parameters
To be used for training, your config json file should include parameters:

* `dataset_reader`
   * `name` — `"your_reader_here"` for a custom dataset or `"dstc2_datasetreader"` to use DSTC2 (for implementation see [`deeppavlov.dataset_readers.dstc2_dataset_reader`](../../dataset_readers/dstc2_dataset_reader.py))
   * `data_path` — a path to a dataset file, which in case of `"dstc2_datasetreader"` will be automatically downloaded from 
   internet and placed to `data_path` directory
* `dataset` — it should always be set to `{"name": "dialog_dataset"}` (for implementation see [`deeppavlov.datasets.dialog_dataset.py`](../../datasets/dialog_dataset.py))

Do not forget to set `train_now` parameters to `true` for `vocabs.word_vocab`, `model` and `model.network` sections.

See [`deeeppavlov/skills/go_bot/config.json`](config.json) for details.

#### Train run
The easiest way to run the training is by using [`deeppavlov/deep.py`](../../deep.py) script:

```bash
cd deeppavlov
python3 deep.py train path/to/config.json
```

## Datasets

#### DSTC2
The Hybrid Code Network model was trained and evaluated on a modification of a dataset from Dialogue State Tracking Challenge 2 [[2]](#references). The modifications were as follows:
* **new actions**
    * bot dialog actions were concatenated into one action (example: `{"dialog_acts": ["ask", "request"]}` -> `{"dialog_acts": ["ask_request"]}`)
    * if a slot key was associated with the dialog action, the new act was a concatenation of an act and a slot key (example: `{"dialog_acts": ["ask"], "slot_vals": ["area"]}` -> `{"dialog_acts": ["ask_area"]}`)
* **new train/dev/test split**
    * original dstc2 consisted of three different MDP polices, the original train and dev datasets (consisting of two polices) were merged and randomly split into train/dev/test
* **minor fixes**
    * fixed several dialogs, where actions were wrongly annotated
    * uppercased first letter of bot responses
    * unified punctuation for bot responses'

#### Your data
If your model uses DSTC2 and relies on `dstc2_datasetreader` [`DatasetReader`](../../core/data/dataset_reader.py), all needed files, if not present in the `dataset_reader.data_path` directory, will be downloaded from internet.

If your model needs to be trained on different data, you have several ways of achieving that (sorted by increase in the amount of code):

1. Use `"dialog_dataset"` in dataset config section and `"dstc2_datasetreader"` in dataset reader config section (**the simplest, but not the best way**):
    * set `dataset.data_path` to your data directory;
    * your data files should have the same format as expected in [`deeppavlov.dataset_readers.dstc2_dataset_reader:DSTC2DatasetReader.read()`](../../dataset_readers/dstc2_dataset_reader.py) function.

2. Use `"dialog_dataset"` in dataset config section and `"your_dataset_reader"` in dataset reader config section (**recommended**): 
    * clone [`deeppavlov.dataset_readers.dstc2_dataset_reader:DSTC2DatasetReader`](../../dataset_readers/dstc2_dataset_reader.py) to `YourDatasetReader`;
    * register as `"your_dataset_reader"`;
    * rewrite so that it implements the same interface as the origin. Particularly, `YourDatasetReader.read()` must have the same output as `DSTC2DatasetReader.read()`:
      * `train` — training dialog turns consisting of tuples:
         * first tuple element contains first user's utterance info
            * `text` — utterance string
            * `intents` — list of string intents, associated with user's utterance
            * `db_result` — a database response _(optional)_
            * `episode_done` — set to `true`, if current utterance is the start of a new dialog, and `false` (or skipped) otherwise _(optional)_
         * second tuple element contains second user's response info
            * `text` — utterance string
            * `act` — an act, associated with the user's utterance
      * `valid` — validation dialog turns in the same format
      * `test` — test dialog turns in the same format
      
#TODO: change str `act` to a list of `acts`

3. Use your own dataset and dataset reader (**if 2. doesn't work for you**):
    * your `YourDataset.iter()` class method output should match the input format for [`HybridCodeNetworkBot.train()`](go_bot.py).

## Comparison
As far as our dataset is a modified version of official DSTC2-dataset [[2]](#references), resulting metrics can't be compared with evaluations on the original dataset.

But comparisons for bot model modifications trained on out DSTC2-dataset are presented:

|                   Model                      | Config      |  Test action accuracy   |  Test turn accuracy  |
|----------------------------------------------|-------------|-------------------------|----------------------|
|basic bot			                               | [`config_minimal.json`](config_minimal.json) | 0.5271             |     0.4853           |
|bot with slot filler & fasttext embeddings    |        |      0.5305             |     0.5147           |
|bot with slot filler & intents                | [`config.json`](config.json)                 |   **0.5436**         |     **0.5261**       |
|bot with slot filler & intents & embeddings   | [`config_all.json`](config_all.json)         |      0.5307             |     0.5145           |

#TODO: add dialog accuracies

# References
[1] [Jason D. Williams, Kavosh Asadi, Geoffrey Zweig, Hybrid Code Networks: practical and efficient end-to-end dialog control with supervised and reinforcement learning – 2017](https://arxiv.org/abs/1702.03274)

[2] [Dialog State Tracking Challenge 2 dataset](http://camdial.org/~mh521/dstc/)
