## Empowering Robotics with Large Language Models: osmAG Map Comprehension with LLMs
### Introduction
This is the open source repository for the paper "Empowering Robotics with Large Language Models: osmAG Map Comprehension with LLMs" by Fujing Xie and Sören Schwertfeger ([Paper link](https://arxiv.org/pdf/2403.08228.pdf)).
The paper address the problem of enabling LLMs to comprehend Area Graph, a text-based map representation, in order to enhance their applicability in the field of mobile robotics. osmAG (Area Graph in OpensStreetMap format) is stored in a XML textual format naturally readable by LLMs. This map representation is comprehensible by LLMs, traditional robotic algorithms and humans. 
Our experiments show that with a proper map representation, LLMs possess the capability to understand maps and answer queries based on that understanding. Following simple fine-tuning of LLaMA2 models, it surpassed ChatGPT-3.5 in tasks involving topology and hierarchy understanding.
This repository contains dataset, dataset generation code, fine-tuned LoRA adapters used in the paper, as well as instructions for how to use the code.
 - The fine-tuned LLaMA2 adapters are in ```Adapters``` folder, you could use the adapters to check the performance of LLaMA2 on osmAG map comprehension (Topological task and Hierarchical task). Please refer to [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) for how to use the adapters.
  - The dataset used in the paper is in ```Dataset``` folder in alpaca format, besides training and testing, we also provide dataset with prompt unseen during training. You could also generate your own dataset by following the instructions below.
  - The ```code``` folder contains the code and osmAG templates for generating the dataset used in the paper. The code is written in Python 3.10. 


### Dataset Generation (optional)
The osmAG template we used in the paper is also provided in the `osmAG_template` folder. You could visualize the template or create your own osmAG template using [JOSM](https://josm.openstreetmap.de/).

We provide our dataset used in the paper, you could also generate your own dataset by following the instructions below. 



The code is written in Python 3.10. To install the required packages, run the following command:
```bash

git https://github.com/xiefujing/LLM-osmAG-Comprehension.git
cd LLM-osmAG-Comprehension
conda env create -f osmAG_comprehension.yaml
conda activate osmAG_comprehension
cd code
# to generate topological data
python generate_topological_dataset.py
# to generate hierarchical data
python generate_hierarchical_dataset.py
```
### LLaMA Adapters Usage
We provide the fine-tuned LoRA adapters used in the paper. You could use the adapters and the LLaMA2 models to check its performance. How to use the adapters please refer to https://github.com/hiyouga/LLaMA-Factory

### Citation
If you find this work useful, please consider citing the paper:
```
@article{xie2024empowering,
  title={Empowering Robotics with Large Language Models: osmAG Map Comprehension with LLMs},
  author={Xie, Fujing and Schwertfeger, S{\"o}ren},
  journal={arXiv preprint arXiv:2403.08228},
  year={2024}
}
```