import math
import random
import queue
import time
import numpy as np
from dpsm.Client import dist2

def getstrlen(x):
    return len(str(x))

def lap_mech(data, sensitivity, epsilon):
    for item_id in data.keys():
        data[item_id] += np.random.laplace(0, 1 / epsilon)


def gaussian_mech(data, sensitivity, sigma):
    for item_id in data.keys():
        data[item_id] += np.random.normal(0, sigma)


def calc_kernel_radius(items, users):
    radius = 0
    for i in items.values():
        for j in users.values():
            radius += dist2(i, j)
    radius /= (len(items) * len(users))
    return 1 / radius  # 1 / 5 / 10

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
    raise ValueError("Error: cant find any sol.")

def FDP(items, args, clients):
    start_time = time.process_time_ns()
    comm_cost=0
    for c in clients:
        comm_cost += getstrlen(c.items)
    sol = set()
    for it in range(args["k"]):
        gains = dict((item_id, 0) for item_id in items.keys())

        for client in clients:
            tmp = client.calc_u()
            #  print(tmp)
            if args["noise"] == "laplace":
                lap_mech(tmp, 0, args["epsilon_0"])
            elif args["noise"] == "gaussian":
                gaussian_mech(tmp, 0, args["sigma"])
            #   print(tmp)
            # after added noise, 'tmp' is sent to server
            comm_cost+=getstrlen(tmp)
            for k, v in tmp.items():
                gains[k] += v

        max_id = -1
        max_value = -1
        for k, v in gains.items():
            if k in sol:
                continue
            if v > max_value:
                max_id = k
                max_value = v

        sol.add(max_id)
        for client in clients:
            client.update_benefits(max_id)
            comm_cost += getstrlen(max_id)

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9,comm_cost


def FDP_Lazy(items, args, clients):
    start_time = time.process_time_ns()
    comm_cost=0
    for c in clients:
        comm_cost += getstrlen(c.items)
    sol = set()
    gains = dict((item_id, 0) for item_id in items.keys())
    last_update = dict((item_id, -1) for item_id in items.keys())
    pq = queue.PriorityQueue()
    for it in range(args["k"]):

        for c in clients:
            c.possionSample()
        if it == 0:
            for item_id in items.keys():
                val = 0
                for c in clients:
                    tmp = c.query(item_id)
                    if args["noise"] == "laplace":
                        tmp += np.random.laplace(0, 1/args["epsilon_0"])
                    elif args["noise"] == "gaussian":
                        tmp += np.random.normal(0, args["sigma"])
                    else:
                        raise ValueError("ERROR: Cannot resolve parameter: noise.")
                    comm_cost += getstrlen(item_id)+getstrlen(tmp)
                    val += tmp
                pq.put((-val, item_id))
                gains[item_id] = val
                last_update[item_id] = it
        max_id = None
        for _ in range(args["cutoff"]):
            if last_update[pq.queue[0][1]] != it:
                item_id = pq.queue[0][1]
                val = 0
                for c in clients:  # re-calc marginal gain
                    c.possionSample()
                    tmp = c.query(item_id)
                    if args["noise"] == "laplace":
                        tmp += np.random.laplace(0, 1/args["epsilon_0"])
                    elif args["noise"] == "gaussian":
                        tmp += np.random.normal(0, args["sigma"])
                    comm_cost += getstrlen(item_id)+getstrlen(tmp)
                    val += tmp
                pq.get()
                pq.put((-val, item_id))  # update priority_queue
                gains[item_id] = val
                last_update[item_id] = it
                if max_id is None or gains[max_id] < val:  # update max_id
                    max_id = item_id
            else:
                break

        if last_update[pq.queue[0][1]] == it:  # best item so far
            item_id = pq.queue[0][1]
            if max_id is None or gains[max_id] < gains[item_id]:
                max_id = item_id

        sol.add(max_id)

        for client in clients:
            client.update_benefits(max_id)
            comm_cost += getstrlen(max_id)

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9,comm_cost


def FDP_PF(items, args, clients):
    start_time = time.process_time_ns()
    comm_cost=0
    for c in clients:
        comm_cost += getstrlen(c.items)
    sol = set()
    for it in range(args["k"]):
        gains = dict((item_id, 0) for item_id in items.keys())

       
            
        for client in clients:
            sol_j = sol.copy()
            for _ in range(args["cutoff"]):
                tmp = client.calc_u()
                output = permutation_flip(tmp, args["epsilon_1"], sol_j)
                ttmp=dict()
                ttmp[output]=tmp[output]
                lap_mech(ttmp,0,args["epsilon_2"])
                gains[output]+=ttmp[output]
                comm_cost+= getstrlen(output)+getstrlen(gains[output])
                sol_j.add(output)
                
        max_id = -1
        max_value = -1
        for k, v in gains.items():
            if k in sol:
                continue
            if v > max_value:
                max_id = k
                max_value = v

        sol.add(max_id)
        for client in clients:
            client.update_benefits(max_id)
            comm_cost+= getstrlen(max_id)

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9,comm_cost