# Federated Submodular Maximization with Differential Privacy

This is for releasing the source code of the paper "Federated Submodular Maximization with Differential Privacy".

## Requirements

* Python==3.8
* numpy==1.22.3


## How to use
To reproduce the experiments, do:

### 1. download dataset
You can download dataset in [here](https://drive.google.com/drive/folders/1NjNinuntFgrKwIkva5U6Yp6nqiIhxQAj), and put it in the same folder as `run.py`, such as `code-dpsm/data/DBLP`

### 2. run

Run the script run.py:

```
$ python3 run.py
```
Before you run the script, you can make some modifications to it.

Such as in line 38:
```python
H = Handler(MaxP=31, save_path="res.csv")
```
`MaxP=31` means the maximum number of parallel computing processes is 31

`save_path="res.csv"` means experiment results will be saved in `res.csv` 

After the program has finished running, you need to use `res_reader.py` to process the data and the final results will be saved in the corresponding `out_*.csv` file






