from dpsm.handler import Handler, get_args_dict

# nohup python -u run.py >> log/tmp/tmp5.out 2>&1


def get_dataset_info(args):
    if args["dataset"] == "DBLP":
        args["items_path"] = "data/DBLP/venue.pkl"
        args["users_path"] = "data/DBLP/graph.pkl"
        args["utility_func"] = "MC"
    elif args["dataset"] == "foursquare":
        args["items_path"] = "data/foursquare/tky-items.pkl"
        args["users_path"] = "data/foursquare/tky-users_1e5.pkl"
        args["radius_multiplier"] = 20
        args["radius"] = 956.9665572
        args["utility_func"] = "FL"
    elif args["dataset"] == "uber":
        args["items_path"] = "data/uber/items.pkl"
        args["users_path"] = "data/uber/users.pkl"
        args["utility_func"] = "FL"
        args["radius_multiplier"] = 100
        args["radius"] = 1256.426663
    elif args["dataset"] == "flickr":
        args["items_path"] = "data/flickr/items.pkl"
        args["users_path"] = "data/flickr/users.pkl"
        args["utility_func"] = "MC"
    elif args["dataset"] == "gen":
        args["items_path"] = "data/gen/items_"+str(args["m"])+".pkl"
        args["users_path"] = "data/gen/users_"+str(args["m"])+".pkl"
        args["utility_func"] = "MC"
    else:
        print("ERROR: cannot resolve dataset:{}".format(args["dataset"]))
        exit(0)
    return


if __name__ == "__main__":
    H = Handler(MaxP=35, save_path="res.csv")

    # parameter tuning
    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        args = get_args_dict(dataset, "Greedy", 10, 20, 1)
        get_dataset_info(args)
        H.start(args)

        for gamma in [1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256, 1/512, 1/1024]:
            for alg in ["CDP", "FDP"]:
                if alg == "CDP":
                    for s_m in ["permutation", "exp_mech"]:
                        for seed in range(1, 11):
                            args = get_args_dict(
                                dataset, alg, 10, 20, gamma, epsilon=0.1, select_method=s_m, seed=seed)
                            get_dataset_info(args)
                            H.start(args)
                if alg == "FDP":
                    for noise in ["gaussian", "laplace"]:
                        for seed in range(1, 11):
                            args = get_args_dict(
                                dataset, alg, 10, 20, gamma, epsilon=2, noise=noise, seed=seed)
                            get_dataset_info(args)
                            H.start(args)
        for noise in ["gaussian", "laplace"]:
            for cut in [1, 4, 16, 64, 256, 1024]:
                for seed in range(1, 11):
                    args = get_args_dict(dataset, "FDP_Lazy", 10, 20,
                                         0.01, epsilon=2, cutoff=cut, noise=noise, seed=seed)
                    get_dataset_info(args)
                    H.start(args)

    # privacy parameter
    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        for seed in range(1, 11):
            for alg in ["CDP", "FDP", "FDP_Lazy"]:
                if alg == "CDP":
                    for gamma in [0.01, 1]:
                        for eps in [0.0001, 0.001, 0.01, 0.1, 1, 10]:
                            args = get_args_dict(
                                dataset, alg, 10, 20, gamma, epsilon=eps, select_method="permutation", seed=seed)
                            get_dataset_info(args)
                            H.start(args)
                if alg == "FDP":
                    for eps in [0.1, 0.25, 0.5, 1] + list(range(2, 22, 2)):
                        args = get_args_dict(
                            dataset, alg, 10, 20, 0.01, epsilon=eps, noise="gaussian", seed=seed)
                        get_dataset_info(args)
                        H.start(args)
                if alg == "FDP_Lazy":
                    for eps in [0.1, 0.25, 0.5, 1] + list(range(2, 22, 2)):
                        args = get_args_dict(
                            dataset, alg, 10, 20, 0.01, epsilon=eps, noise="gaussian", seed=seed, cutoff=256)
                        get_dataset_info(args)
                        H.start(args)

    # solution size
    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:

        for k in [1]+list(range(2, 22, 2)):
            args = get_args_dict(dataset, "Greedy", k, 20, 1)
            get_dataset_info(args)
            H.start(args)
            for seed in range(1, 2):
                for alg in ["CDP", "FDP", "FDP_Lazy"]:
                    if alg == "CDP":
                        for gamma in [0.01, 1]:
                            args = get_args_dict(
                                dataset, alg, k, 20, gamma, epsilon=0.1, select_method="permutation", seed=seed)
                            get_dataset_info(args)
                            H.start(args)
                    if alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, k, 20, 0.01, epsilon=2, noise="gaussian", seed=seed)
                        get_dataset_info(args)
                        H.start(args)
                    if alg == "FDP_Lazy":
                        args = get_args_dict(
                            dataset, alg, k, 20, 0.01, epsilon=2, noise="gaussian", seed=seed, cutoff=256)
                        get_dataset_info(args)
                        H.start(args)

    # client number
    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        for l in [1, 4, 16, 64, 256, 1024]:
            args = get_args_dict(dataset, "Greedy", 10, l, 1)
            get_dataset_info(args)
            H.start(args)
            for seed in range(1, 11):
                for alg in ["FDP", "FDP_Lazy"]:
                    if alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, 10, l, 0.01, epsilon=2, noise="gaussian", seed=seed)
                        get_dataset_info(args)
                        H.start(args)
                    if alg == "FDP_Lazy":
                        args = get_args_dict(
                            dataset, alg, 10, l, 0.01, epsilon=2, noise="gaussian", seed=seed, cutoff=256)
                        get_dataset_info(args)
                        H.start(args)

    # user number
    max_size = dict()
    max_size["DBLP"] = 704738
    max_size["flickr"] = 242364
    max_size["uber"] = 564516
    max_size["foursquare"] = 100000
    max_size["gen"] = 500000
    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:

        nn = 1024
        while True:
            if nn > max_size[dataset]:
                nn = max_size[dataset]
            g = min(1, max_size[dataset]/nn*0.01)
            args = get_args_dict(dataset, "Greedy", 10, 20, 1, n=nn)
            get_dataset_info(args)
            H.start(args)
            for seed in range(1, 11):
                for alg in ["FDP", "FDP_Lazy"]:
                    if alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, 10, 20, 0.01, n=nn, epsilon=2, noise="gaussian", seed=seed)
                        get_dataset_info(args)
                        H.start(args)
                    if alg == "FDP_Lazy":
                        args = get_args_dict(
                            dataset, alg, 10, 20, 0.01, n=nn, epsilon=2, noise="gaussian", seed=seed, cutoff=256)
                        get_dataset_info(args)
                        H.start(args)

            if nn == max_size[dataset]:
                break
            nn *= 2

    H.wait()
