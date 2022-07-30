import math
import random


def dist2(a: list, b: list):
    if len(a) != len(b):
        print("Error: dimension not match")
    distance2 = 0
    for i in range(len(a)):
        distance2 += (a[i] - b[i]) * (a[i] - b[i])
    return distance2


def dotProduct(a: list, b: list):
    if len(a) != len(b):
        print("Error: dimension not match")
    ab = 0
    for i in range(len(a)):
        ab += a[i]*b[i]
    return ab


class Client:
    def __init__(self, users, items, args):
        self.users = users
        self.items = items
        self.args = args

        self.user_benefits = dict([(key, 0) for key in self.users])
        self.sample = set()
        self.possionSample()

        if args["utility_func"] == "MC":
            self.utility_func = self.MC_utility_func
        elif args["utility_func"] == "FL":
            self.utility_func = self.FL_utility_func
        elif args["utility_func"] == "SR":
            self.utility_func = self.SR_utility_func

    def possionSample(self):
        self.sample = set()
        for user_id in self.users.keys():
            if random.random() > self.args["gamma"]:
                continue
            self.sample.add(user_id)

    def calc_u(self):
        gains = dict((key, 0) for key in self.items)
        self.possionSample()
        for user_id in self.sample:
            for item_id in self.items.keys():
                gains[item_id] += max(0, self.utility_func(user_id,
                                      item_id)-self.user_benefits[user_id])
        return gains

    def query(self, item_id):
        q = 0
        for user_id in self.sample:
            q += max(0, self.utility_func(user_id, item_id) -
                     self.user_benefits[user_id])
        return q

    def update_benefits(self, max_id):
        for user_id in self.users.keys():
            self.user_benefits[user_id] = max(
                self.user_benefits[user_id], self.utility_func(user_id, max_id))

    def MC_utility_func(self, user_id, item_id):
        if item_id in self.users[user_id]:
            return 1
        return 0

    def FL_utility_func(self, user_id, item_id):
        return math.exp(- self.args["radius"] * dist2(self.items[item_id], self.users[user_id]))

    def SR_utility_func(self, user_id, item_id):
        return self.users[user_id][item_id]


class Fast_Client:
    def __init__(self, users, items, args):
        self.users = users
        self.active_users = users
        self.items = items
        self.args = args

        self.user_benefits = 0
        self.sample = set()
        self.possionSample()

    def possionSample(self):
        self.sample = set()
        for user_id in self.active_users.keys():
            if random.random() > self.args["gamma"]:
                continue
            self.sample.add(user_id)

    def calc_u(self):
        gains = dict((key, 0) for key in self.items)
        self.possionSample()
        for user_id in self.sample:
            for v in self.active_users[user_id]:
                gains[v] += 1
            # for item_id in self.items.keys():
            #     gains[item_id] += max(0, self.utility_func(user_id,
            #                           item_id)-self.user_benefits[user_id])
        return gains

    def query(self, item_id):
        q = 0
        for user_id in self.sample:
            if item_id in self.active_users[user_id]:
                q += 1
        return q

    def update_benefits(self, max_id):
        for user_id in list(self.active_users.keys()):
            if max_id in self.active_users[user_id]:
                self.user_benefits += 1
                del self.active_users[user_id]
