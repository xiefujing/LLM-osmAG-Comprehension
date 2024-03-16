## Empowering Robotics with Large Language Models: osmAG Map Comprehension with LLMs
### Introduction
This is the open source repository for the paper "Empowering Robotics with Large Language Models: osmAG Map Comprehension with LLMs" by Fujing Xie and Sören Schwertfeger ([Paper link](https://arxiv.org/pdf/2403.08228.pdf)).This repository contains dataset, dataset generation code, fine-tuned LoRA adapters used in the paper, as well as instructions for how to use the code.



### Dataset Generation
The osmAG template we used in the paper is also provided in the `osmAG_template` folder. You could visualize the template or create your own osmAG template using JOSM(https://josm.openstreetmap.de/).

We provide our dataset used in the paper, you could also generate your own dataset by following the instructions below. 



The code is written in Python 3.10. To install the required packages, run the following command:
```bash
conda env create -f osmAG_comprehension.yaml
conda activate osmAG_comprehension
git https://github.com/xiefujing/LLM-osmAG-Comprehension.git
cd LLM-osmAG-Comprehension
# to generate topological code
python generate_topological_dataset.py
# to generate hierarchical code
python generate_hierarchical_dataset.py
```
### LlAMA Adapters Usage
We provide the fine-tuned LoRA adapters used in the paper. You could use the adapters and the LlAMA2 models to check its performance. How to use the adapters please refer to https://github.com/hiyouga/LLaMA-Factory

### Citation
```
@misc{xie2024Empowering,
      title={Empowering Robotics with Large Language Models: osmAG Map Comprehension with LLMs}, 
      author={Fujing Xie, Sören Schwertfeger},
      year={2024},
      eprint={2403.08228},
      archivePrefix={arXiv},
      primaryClass={cs.RO}
}
```