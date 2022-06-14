import timeit
import numpy as np


class User:
    def __init__(self, uid: int, elem: set):
        self.uid = uid
        self.elem = elem


def read_items(input_path: str):
    list_items = []
    with open(input_path, 'r') as input_file:
        for line in input_file:
            item_id = int(line.strip())
            list_items.append(item_id)
    return list_items


def read_users(input_path: str):
    list_users = []
    with open(input_path, 'r') as input_file:
        for line in input_file:
            tokens = line.strip().split(':')
            user_id = int(tokens[0].strip())
            elem = set()
            items = tokens[1].strip().split(' ')
            for item in items:
                elem.add(int(item.strip()))
            list_users.append(User(user_id, elem))
    return list_users


def greedy_mc(items, users, k: int):
    start = timeit.default_timer()
    sol = set()
    cov = set()
    for it in range(k):
        gains = np.zeros(len(items))
        for ii in range(len(items)):
            for jj in range(len(users)):
                if jj in cov:
                    continue
                if items[ii] not in sol and items[ii] in users[jj].elem:
                    gains[ii] += 1
        max_id = np.argmax(gains)
        sol.add(items[max_id])
        for jj in range(len(users)):
            if items[max_id] in users[jj].elem:
                cov.add(jj)
    stop = timeit.default_timer()
    return sol, cov, (stop - start)
