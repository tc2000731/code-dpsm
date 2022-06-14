import math
import timeit

import numpy as np


def read_items(input_path: str):
    list_items = []
    with open(input_path, 'r') as input_file:
        line_no = 0
        for line in input_file:
            tokens = line.strip().split(' ')
            if line_no == 0:
                n = int(tokens[0])
                for i in range(n):
                    list_items.append(list())
            else:
                item_id = int(tokens[0])
                for i in range(1, len(tokens)):
                    list_items[item_id].append(float(tokens[i]))
            line_no += 1
    return list_items


def read_users(input_path: str):
    list_users = []
    with open(input_path, 'r') as input_file:
        line_no = 0
        for line in input_file:
            tokens = line.strip().split(' ')
            if line_no == 0:
                m = int(tokens[0])
                for i in range(m):
                    list_users.append(list())
            else:
                user_id = int(tokens[0])
                for i in range(1, len(tokens)):
                    list_users[user_id].append(float(tokens[i]))
            line_no += 1
    return list_users


def dist2(a: list, b: list):
    if len(a) != len(b):
        print("Error: dimension not match")
    distance2 = 0
    for i in range(len(a)):
        distance2 += (a[i] - b[i]) * (a[i] - b[i])
    return distance2


def calc_kernel_radius(list_items: list, list_users: list):
    radius = 0
    for i in range(len(list_items)):
        for j in range(len(list_users)):
            radius += dist2(list_items[i], list_users[j])
    radius /= (len(list_items) * len(list_users))
    return 10.0 / radius


def greedy_fl(items, users, k: int, radius: float):
    start = timeit.default_timer()

    sol = set()
    user_benefits = np.zeros(len(users))

    for it in range(k):
        gains = np.zeros(len(items))
        for ii in range(len(items)):
            for jj in range(len(users)):
                benefit = math.exp(- radius * dist2(items[ii], users[jj]))
                gains[ii] += max(0.0, benefit - user_benefits[jj])
        max_id = np.argmax(gains)
        sol.add(max_id)
        for jj in range(len(users)):
            user_benefits[jj] = max(user_benefits[jj], math.exp(- radius * dist2(items[max_id], users[jj])))
    stop = timeit.default_timer()
    return sol, user_benefits, (stop - start)
