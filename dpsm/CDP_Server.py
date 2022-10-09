import math
import random
import time
import numpy as np

def getstrlen(x):
    return len(str(x))

def exp_mech(data, epsilon, sol):
    p = {}
    max_v = 0
    for k,v in data.items():
        if k in sol:
            continue
        max_v = max(max_v, v)
        
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


def permutation_flip(data, epsilon, sol):
    mq = 0
    for k,v in data.items():
        if k in sol:
            continue
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
    comm_cost=0
    for c in clients:
        comm_cost += getstrlen(c.items)
    sol = set()
    for it in range(args["k"]):
        gains = dict((item_id, 0) for item_id in items.keys())
        if args["select_method"] != "random_select":
            for client in clients:
                tmp = client.calc_u()
                comm_cost+= getstrlen(tmp)

                for k, v in tmp.items():
                    gains[k] += v
        if args["select_method"] == "permutation":
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
            raise ValueError("ERROR: Cannot resolve parameter: select_method.")

        sol.add(output)

        for client in clients:
            client.update_benefits(output)
            comm_cost+=getstrlen(output)

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9,comm_cost
