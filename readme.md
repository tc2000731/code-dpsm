# Federated Submodular Maximization with Differential Privacy

This is for releasing the source code of the paper "Federated Submodular Maximization with Differential Privacy".

## Requirements

* Python==3.8
* numpy==1.22.3

## Link
..

## How to use
To reproduce the experiments, do:

### 1. download dataset
You can download dataset in [here](https://drive.google.com/drive/folders/1NjNinuntFgrKwIkva5U6Yp6nqiIhxQAj), and put it in the same folder as run.py

### 2. run

Run the script run.py:

```
$ python3 run.py
```
Before you run the script, you can make some modifications to it.

Such as in line 38:
```python
H = Handler(MaxP=35, save_path="res.csv")
```
`MaxP=35` means the maximum number of parallel computing processes

`save_path="res.csv"` means experiment results will be saved in `res.csv` 



---

To run the algorithm with other dataset/parameters, do:

### 1. 
...


