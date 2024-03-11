---
license: other
library_name: peft
tags:
- llama-factory
- lora
- generated_from_trainer
base_model: /public/home/xiefj/llama_hf
model-index:
- name: hier_1
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# hier_1

This model is a fine-tuned version of [/public/home/xiefj/llama_hf](https://huggingface.co//public/home/xiefj/llama_hf) on the llama_train_hier dataset.

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 5e-05
- train_batch_size: 4
- eval_batch_size: 8
- seed: 42
- distributed_type: multi-GPU
- num_devices: 4
- gradient_accumulation_steps: 4
- total_train_batch_size: 64
- total_eval_batch_size: 32
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: cosine
- num_epochs: 8.0

### Training results



### Framework versions

- PEFT 0.7.1
- Transformers 4.36.2
- Pytorch 2.0.0+cu117
- Datasets 2.16.1
- Tokenizers 0.15.1