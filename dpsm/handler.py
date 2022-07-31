import os
from pydoc import cli
import random
import math
import numpy as np
import csv
import pickle
import time as tm
import multiprocessing as mp
from dpsm.Client import Client, dotProduct, Fast_Client
from dpsm.FDP_Server import FDP, calc_kernel_radius, FDP_Lazy
from dpsm.CDP_Server import CDP


def read_dict(input_path: str):
    with open(input_path, "rb") as f:
        dic = pickle.load(f)
        return dic


def get_args_dict(dataset, algorithm, k, l, gamma, seed=0, epsilon=1, n=None, m=None, select_method=None, noise=None, cutoff=None, s=None, beta=None, save=True, fast=False):
    dic = dict()
    dic["dataset"] = dataset
    dic["algorithm"] = algorithm
    dic["k"] = k
    dic["epsilon"] = epsilon
    dic["gamma"] = gamma
    dic["save"] = save
    dic["seed"] = seed
    dic["l"] = l
    dic["fast"] = fast
    dic["save"] = save
    if m is not None:
        dic["m"] = m
    if n is not None:
        dic["n"] = n

    if algorithm == "Greedy":
        dic["select_method"] = "greedy"
    if algorithm == "CDP":
        if select_method is None:
            raise ValueError("Error: Missing parameter: select_method.")
        dic["select_method"] = select_method
    if algorithm == "FDP":
        if noise is None:
            raise ValueError("Error: Missing parameter: noise.")
        dic["noise"] = noise
    if algorithm == "FDP_Lazy":
        if noise is None:
            raise ValueError("Error: Missing parameter: noise.")
        if cutoff is None:
            raise ValueError("Error: Missing parameter: cutoff.")
        dic["noise"] = noise
        dic["cutoff"] = cutoff
    return dic


class Handler:
    def __init__(self, MaxP=10, save_path="res.csv", res_fields=None, check_fields=None) -> None:
        self.MaxP = MaxP
        self.Pcnt = 0
        self.q = mp.Queue()
        self.save_path = save_path
        self. res_fields = res_fields
        if res_fields is None:
            self.res_fields = ["dataset", "algorithm", "utility_func", "l", "seed", "n", "m", "k", "gamma", "epsilon",
                               "delta","epsilon_0", "delta_0", "sigma", "radius", "select_method", "noise",
                               "cutoff", "sol", "result", "time"]
        self.args = dict()
        self.check_fileds = check_fields
        if check_fields is None:
            self.check_fileds = ["dataset", "algorithm", "l", "seed", "n", "m", "k", "gamma", "epsilon",
                                 "select_method", "noise", "cutoff"]
        self.exist_args = set()

        try:
            with open(self.save_path, 'r', newline='') as csvfile:
                print('file exists')
        # if desired file doesn't exist, create it with the write ('w') or
        # append 'a' mode
        except:
            with open(self.save_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.res_fields)
                writer.writeheader()

        with open(self.save_path) as f:
            d = csv.DictReader(f)
            cnt = 0
            for row in d:
                dd = dict()
                for key in self.check_fileds:
                    if key == "epsilon" or key == "gamma":
                        dd[key] = str(float(row[key]))
                    else:
                        dd[key] = row[key]
                self.exist_args.add(str(dd))

    def start(self, args):
        self.args = args.copy()
        self.start_work()

    def start_work(self):
        # print("nb")
        if "epsilon" not in self.args:
            self.args["epsilon"] = 1
        if self.args["algorithm"] == "FDP_SVT":
            self.get_start_value()
        if self.existed(self.args):
            print("ARGS EXISTED. STOP RUNNING.")
            return

        self.exist_args.add(str(self.args))
        mp.Process(target=self.work, args=(self.args, self.q)).start()
        self.Pcnt += 1
        self.wait(self.MaxP)

    def existed(self, args):
        nargs = dict()
        # print("nb")
        for key in self.check_fileds:
            nargs[key] = '' if key not in args else str(args[key])
            if key == "epsilon" or key == "gamma":
                nargs[key] = str(float(nargs[key]))
        print(str(nargs))
        return str(nargs) in self.exist_args

    def wait(self, minp=0):

        while self.Pcnt >= minp:
            a = self.q.get()
            if "Exist" in a:
                self.Pcnt -= 1
                continue
            if a["save"]:
                with open(self.save_path, "a", newline='') as f:
                    fileds = ["dataset", "algorithm", "utility_func", "l", "seed", "n", "m", "k", "gamma", "epsilon", "delta",
                              "epsilon_0", "delta_0", "sigma", "radius", "select_method", "noise", "cutoff", "s", "beta",
                              "start_value", "ignore_value", "radius_multiplier", "eta", "sol", "result", "time"]
                    w = csv.DictWriter(
                        f, extrasaction="ignore", fieldnames=fileds)
                    w.writerow(a)
            self.Pcnt -= 1

    def work(self, args, q):
        random.seed(1)
        np.random.seed(1)

        random.seed(args["seed"])
        np.random.seed(args["seed"])

        items = read_dict(args["items_path"])
        users = read_dict(args["users_path"])

        if "n" not in args:
            args["n"] = len(users)
        args["m"] = len(items)

        args["delta"] = 1/(args["n"]**1.5)

        partition = [i % args["l"] for i in range(args["n"])]
        selected_user = [(1 if i < args["n"] else 0)
                         for i in range(len(users))]

        # shuffle and partition data
        random.shuffle(partition)
        #
        random.shuffle(selected_user)
        cnt = 0
        num = -1
        users_data = [dict() for i in range(args["l"])]
        for key in users.keys():
            num += 1
            if selected_user[num] == 0:
                continue
            users_data[partition[cnt]][key] = users[key]
            cnt += 1

        # create client
        clients = []
        for i in range(args["l"]):
            if args["fast"] is True:
                clients.append(Fast_Client(users_data[i], items, args))
            else:
                clients.append(Client(users_data[i], items, args))
        if self.args["algorithm"] != "Greedy":
            self.calc_e0(args)

        func = None
        if args["algorithm"] == "Greedy":
            func = CDP
        elif args["algorithm"] == "FDP":
            func = FDP
        elif args["algorithm"] == "CDP":
            func = CDP
        elif args["algorithm"] == "FDP_Lazy":
            func = FDP_Lazy
        elif args["algorithm"] == "FDP_SVT":
            func = FDP_SVT
        print(args)
        if self.existed(args):
            args["Exist"] = True
            print("ARGS ALREADY EXIST. STOP RUNNING.")
            q.put(args)
            return
        sol, time = func(items, args, clients)
        benefits = 0
        if args["fast"] is False:
            for client in clients:
                benefits += sum(client.user_benefits.values())
        else:
            for client in clients:
                benefits += client.user_benefits
        args["sol"] = sol
        args["result"] = benefits
        args["time"] = time
        print("done:", args)
        q.put(args)

    def F(self, t, a, b, c):
        return (t*a)/(b-(c/(t-1)))

    def logjc(self, n):
        s = 0
        for i in range(n):
            s += math.log(i+1)
        return s

    def calc_e0(self, args):

        e = args["epsilon"]
        if args["algorithm"] == "CDP":
            k = args["k"]
        elif args["algorithm"] == "FDP":
            k = args["k"]*args["m"]
        elif args["algorithm"] == "FDP_SVT":
            k = args["k"]*args["s"]
        elif args["algorithm"] == "FDP_Lazy":
            k = args["m"]+(args["k"]-1)*args["cutoff"]

        d = args["delta"]
        gamma = args["gamma"]

        basic_e = e/k
        basic_d = d/k

        adv_d = d/2
        a = k/2
        b = math.sqrt(2*k*math.log(1/adv_d))
        c = -e
        delta = b*b-4*a*c

        adv_e = (-b+math.sqrt(delta))/(a+a)
        print("basic_e:", basic_e, "basic_d:", basic_d)
        print("adv_e:", adv_e, "adv_d:", adv_d)

        if basic_e > adv_e:
            args["epsilon_0"] = basic_e
            args["delta_0"] = basic_d
        else:
            args["epsilon_0"] = adv_e
            args["delta_0"] = adv_d/k

        args["delta_0"] /= gamma
        args["epsilon_0"] = math.log(
            1 + (math.exp(args["epsilon_0"]) - 1) / gamma)
        if args["algorithm"] == "FDP" or args["algorithm"] == "FDP_Lazy":
            a = k*args["gamma"]*args["gamma"]
            b = args["epsilon"]
            c = math.log(1/args["delta"])
            # print(a,b,c)
            d = 1+c/b
            sigma = math.sqrt(a/b*(2*math.sqrt(d*d-d)+2*d-1)/2)
            args["sigma"] = sigma
            print("sigma:", sigma)
        elif args["algorithm"] == "FDP_SVT":

            m = args["m"]
            cut = args["cutoff"]
            a = (cut+1)/2
            b = math.sqrt(
                (1+cut)*(math.log(1/args["delta_0"])+math.log(cut)+self.logjc(m)-self.logjc(cut)-self.logjc(m-cut)))
            c = -args["epsilon_0"]
            delta = b*b-4*a*c

            sigma = (-b+math.sqrt(delta))/(a+a)
            sigma = 1/(sigma)
            args["sigma"] = sigma
            print("sigma", sigma)
