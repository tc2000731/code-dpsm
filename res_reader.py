import csv
import collections


def filter_0(args):
    if args["dataset"] == "DBLP" and False:
        return 0
    if args["algorithm"] != "FDP" and False:  # True/ False
        return 0
    if args["select_method"] != "noisy_max" and False:
        return 0
    if args["gamma"] != 0 and False:
        return 0
    return 1


def filter_1(args):
    if args["dataset"] != "DBLP":
        return 0
    if args["algorithm"] != "FDP" and True:
        return 0
    if args["gamma"] != "0.015625":
        return 0
    if args["epsilon"] != "10":
        return 0
    return 1


def getkey(row):
    return (row["dataset"], row["algorithm"], row["l"], row["n"], row["m"], row["k"], row["epsilon"],
            row["select_method"], row["noise"], row["cutoff"], row["radius_multiplier"], row["gamma"])


def eq(a, b):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x == y or x == "*" or y == "*":
            continue
        return False
    return True


with open("res.csv", 'r') as f:
    # fields = ["dataset", "algorithm", "utility_func", "l", "seed", "n", "m", "k", "gamma", "epsilon", "delta",
    #           "epsilon_0", "delta_0", "sigma", "radius", "select_method", "noise", "cutoff", "s", "beta",
    #           "start_value", "ignore_value", "radius_multiplier", "eta", "sol", "result", "time"]
    # writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    # writer.writeheader()
    r = csv.DictReader(f)
    lines = []
    for row in r:
        if filter_0(row):
            lines.append(row)
            # print(row)
lines = sorted(lines, key=lambda x: (x["dataset"], x["m"], x["algorithm"],
                                     x["select_method"],
                                     x["epsilon"], x["noise"], x["k"], x["gamma"],
                                     int(0 if x["cutoff"] == '' else x["cutoff"])))
last_appear = dict()
total = collections.defaultdict(float)
total_time = collections.defaultdict(float)
cnt = collections.defaultdict(int)
variance = collections.defaultdict(float)
max_result = collections.defaultdict(float)
min_result = dict((getkey(row), 1e9) for row in lines)


for row in lines:
    total[getkey(row)] += float(row["result"])
    total_time[getkey(row)] += float(row["time"])
    cnt[getkey(row)] += 1
    # if filter_1(row):
    #     print(row)

for row in lines:
    key = getkey(row)
    variance[key] += (float(row["result"])-(total[key]/cnt[key]))**2
    max_result[key] = max(max_result[key], float(row["result"]))
    min_result[key] = min(min_result[key], float(row["result"]))
    last_appear[key] = row

for key in total.keys():
    print(key, "cnt:", cnt[key], "average:", total[key]/cnt[key],
          "time:", total_time[key]/cnt[key])

# for row in lines:
#     key = getkey(row)
#     if eq(key, ('ml1m', 'FDP', '*', '*', '*', '*', '*', '*', '*', '*')):
#         print(key, row["result"], row["sol"], row["sigma"])
dic_list = []
for key in total.keys():
    dic = dict()
    tmp = ["dataset", "algorithm", "utility_func", "l", "n", "m", "k", "gamma", "epsilon", "delta",
           "epsilon_0", "delta_0", "sigma", "radius", "radius_multiplier", "select_method", "noise", "cutoff", "s", "beta"]
    for kk in tmp:
        dic[kk] = last_appear[key][kk]
    dic["number of runs"] = cnt[key]
    dic["result"] = total[key]/cnt[key]
    dic["variance"] = variance[key]/cnt[key]
    dic["time"] = total_time[key]/cnt[key]
    dic["max_result"] = max_result[key]
    dic["min_result"] = min_result[key]
    dic_list.append(dic)


with open("out.csv", "w") as f:
    fileds = ["dataset", "algorithm", "utility_func", "l", "n", "m", "k", "gamma", "epsilon", "delta",
              "epsilon_0", "delta_0", "sigma", "radius", "radius_multiplier", "select_method", "noise", "cutoff", "s", "beta", "number of runs",
              "result", "variance", "time", "max_result", "min_result"]
    writer = csv.DictWriter(f, extrasaction="ignore", fieldnames=fileds)
    writer.writeheader()
    for row in dic_list:
        writer.writerow(row)
