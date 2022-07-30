import math
import random
import time
import numpy as np


def exp_mech(data, epsilon, sol):
    p = {}
    max_v = max(data.values())
    total = 0
    for item_id in data.keys():
        p[item_id] = 0 if item_id in sol else math.exp(
            (data[item_id]-max_v) * epsilon / 2)
        total += p[item_id]

    rnd = random.random() * total
    for item_id in p.keys():
        if rnd < p[item_id]:
            return item_id
        else:
            rnd -= p[item_id]


def report_noisy_max(data, epsilon, sol):
    max_id = None
    max_val = 0
    for item_id in data.keys():
        if item_id in sol:
            continue
        tmp = data[item_id] + np.random.laplace(0, 1 / epsilon)
        if max_id is None or max_val < tmp:
            max_id = item_id
            max_val = tmp
    return max_id


def permutation_flip(data, epsilon, sol):
    mq = 0
    for v in data.values():
        mq = max(mq, v)

    pi = list(data.keys())
    random.shuffle(pi)
    for item_id in pi:
        if item_id in sol:
            continue
        p = math.exp(epsilon / 2 * (data[item_id] - mq))
        if random.random() < p:
            return item_id


def random_select(data, epsilon, sol):
    size = len(data)-len(sol)
    rv = random.randint(1, size)-1
    for item_id in data.keys():
        if item_id in sol:
            continue
        if rv == 0:
            return item_id
        rv -= 1


def CDP(items, args, clients):
    start_time = time.process_time_ns()

    sol = set()
    for it in range(args["k"]):
        gains = dict((item_id, 0) for item_id in items.keys())
        if args["select_method"] != "random_select":
            for client in clients:
                tmp = client.calc_u()

                for k, v in tmp.items():
                    gains[k] += v
        # print("gains['911']",gains['911'])
        if args["select_method"] == "noisy_max":
            output = report_noisy_max(gains, args["epsilon_0"], sol)
        elif args["select_method"] == "permutation":
            output = permutation_flip(gains, args["epsilon_0"], sol)
        elif args["select_method"] == "exp_mech":
            output = exp_mech(gains, args["epsilon_0"], sol)
        elif args["select_method"] == "random_select":
            output = random_select(gains, args["epsilon_0"], sol)
        elif args["select_method"] == "greedy":
            output = None
            for key in gains.keys():
                if key in sol:
                    continue
                if output is None or gains[output] < gains[key]:
                    output = key
        else:
            print("ERROR: select_method set to exp_mech")
            output = exp_mech(gains, args["epsilon_0"], sol)

        sol.add(output)

        for client in clients:
            client.update_benefits(output)

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9
