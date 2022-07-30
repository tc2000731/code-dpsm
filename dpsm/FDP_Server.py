import math
import random
import queue
import time
import numpy as np
from dpsm.Client import dist2


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


def FDP(items, args, clients):
    start_time = time.process_time_ns()

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

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9


def FDP_Lazy(items, args, clients):
    start_time = time.process_time_ns()

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
                    tmp = c.query(item_id)
                    if args["noise"] == "laplace":
                        tmp += np.random.laplace(0, 1/args["epsilon_0"])
                    elif args["noise"] == "gaussian":
                        tmp += np.random.normal(0, args["sigma"])
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

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9


def GSVT(data, queries, sigma, cufoff, threshold):
    t = threshold + np.random.normal(0, sigma)
    s = set()
    cnt = 0
    random.shuffle(queries)
    for item_id in queries:
        if data[item_id]+np.random.normal(0, 2*sigma) >= t:
            s.add(item_id)
            cnt += 1
        if cnt >= cufoff:
            break
    return s


def FDP_SVT(items, args, clients):
    start_time = time.process_time_ns()
    sol = set()
    V = set(items.keys())
    for kk in range(args["k"]):
        q = dict((item_id, 0) for item_id in items.keys())
        for j in clients:
            Vj = V.copy()
            for ss in range(args["s"]):
                data = j.calc_u()
                t = args["start_value"][kk] * \
                    ((1 - args["beta"]) ** ss) * len(j.users)
                S = GSVT(data, list(Vj), args["sigma"],
                         args["cutoff"], t * args["gamma"])
                for v in S:
                    q[v] += t
                    Vj.remove(v)

        max_id = None

        for v in q.keys():
            if v in sol:
                continue
            if max_id is None or q[max_id] < q[v]:
               # print(v)
                max_id = v

        V.remove(max_id)
        sol.add(max_id)
        for client in clients:
            client.update_benefits(max_id)

    stop_time = time.process_time_ns()
    return sol, (stop_time - start_time)/1e9
