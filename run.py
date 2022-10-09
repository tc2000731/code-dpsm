
from dpsm.handler import Handler, get_args_dict

# nohup python -u run.py >> logs/tmp.out 2>&1


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
    H = Handler(MaxP=31, save_path="res_eps.csv")

    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        gm = 0.01
        for eps in [0.05, 0.1, 0.25, 0.5, 1, 2]+list(range(4, 22, 4)):
            for alg in ["FDP_Lazy"]:
                for sd in range(1, 11):
                    if alg == "CDP":
                        args = get_args_dict(
                            dataset, alg, 10, 20, gm, epsilon=eps, select_method="permutation", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, 10, 20, gm, epsilon=eps, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP_Lazy":
                        args = get_args_dict(dataset, "FDP_Lazy", 10, 20,
                                             gm, epsilon=eps, cutoff=256, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        if args["utility_func"] == "MC":
                            args["cutoff"] = 16
                        H.start(args)
                    elif alg == "FDP_PF":
                        args = get_args_dict(
                            dataset, alg, 10, 20, gm, epsilon=eps, cutoff=2, e0_ratio=4/5, seed=sd)
                        get_dataset_info(args)
                        H.start(args)

    H.wait()

    H = Handler(MaxP=31, save_path="res_k.csv")

    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        gm = 0.01
        eps = 2
        for k in [1]+list(range(2, 22, 2)):
            # for alg in ["CDP","FDP","FDP_Lazy","FDP_PF"]:
            for alg in ["FDP_Lazy"]:
                for sd in range(1, 11):
                    if alg == "CDP":
                        args = get_args_dict(
                            dataset, alg, k, 20, gm, epsilon=eps, select_method="permutation", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, k, 20, gm, epsilon=eps, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP_Lazy":
                        args = get_args_dict(dataset, "FDP_Lazy", k, 20,
                                             gm, epsilon=eps, cutoff=256, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        if args["utility_func"] == "MC":
                            args["cutoff"] = 16
                        H.start(args)
                    elif alg == "FDP_PF":
                        args = get_args_dict(
                            dataset, alg, k, 20, gm, epsilon=eps, cutoff=2, e0_ratio=4/5, seed=sd)
                        get_dataset_info(args)
                        H.start(args)

    H.wait()  # wait for all the other processes to finish

    H = Handler(MaxP=31, save_path="res_l.csv")

    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        gm = 0.01
        eps = 2
        k = 10
        for l in [1, 4, 16, 64, 256, 1024]:
            for alg in ["FDP_Lazy"]:
                for sd in range(1, 11):
                    if alg == "CDP":
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, select_method="permutation", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP_Lazy":
                        args = get_args_dict(dataset, "FDP_Lazy", k, l,
                                             gm, epsilon=eps, cutoff=256, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        if args["utility_func"] == "MC":
                            args["cutoff"] = 16
                        H.start(args)
                    elif alg == "FDP_PF":
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, cutoff=2, e0_ratio=4/5, seed=sd)
                        get_dataset_info(args)
                        H.start(args)

    H.wait()
    H = Handler(MaxP=31, save_path="res_gamma.csv")

    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:

        eps = 2
        k = 10
        l = 20
        for gm in [1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256, 1/512, 1/1024]:
            for alg in ["CDP", "FDP"]:
                for sd in range(1, 11):
                    if alg == "CDP":
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, select_method="permutation", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP":
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                    elif alg == "FDP_Lazy":
                        args = get_args_dict(dataset, "FDP_Lazy", k, l,
                                             gm, epsilon=eps, cutoff=256, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        if args["utility_func"] == "MC":
                            args["cutoff"] = 16
                        H.start(args)
                    elif alg == "FDP_PF":
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, cutoff=2, e0_ratio=4/5, seed=sd)
                        get_dataset_info(args)
                        H.start(args)

    H.wait()

    H = Handler(MaxP=31, save_path="res_c.csv")

    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        gm = 0.01
        eps = 2
        k = 10
        l = 20
        for alg in ["FDP_Lazy"]:
            for sd in range(1, 11):
                if alg == "CDP":
                    args = get_args_dict(
                        dataset, alg, k, l, gm, epsilon=eps, select_method="permutation", seed=sd)
                    get_dataset_info(args)
                    H.start(args)
                elif alg == "FDP":
                    args = get_args_dict(
                        dataset, alg, k, l, gm, epsilon=eps, noise="laplace", seed=sd)
                    get_dataset_info(args)
                    H.start(args)
                elif alg == "FDP_Lazy":
                    for c in [1, 4, 16, 64, 256, 1024]:
                        args = get_args_dict(dataset, "FDP_Lazy", k, l,
                                             gm, epsilon=eps, cutoff=c, noise="laplace", seed=sd)
                        get_dataset_info(args)
                        H.start(args)
                elif alg == "FDP_PF":
                    for c in [1, 2, 4, 8, 16, 32]:
                        args = get_args_dict(
                            dataset, alg, k, l, gm, epsilon=eps, cutoff=c, e0_ratio=4/5, seed=sd)
                        get_dataset_info(args)
                        H.start(args)

    H.wait()

    H = Handler(MaxP=31, save_path="res_er.csv")

    for dataset in ["DBLP", "flickr", "uber", "foursquare"]:
        gm = 0.01
        eps = 2
        k = 10
        l = 20
        for alg in ["FDP_PF"]:
            for sd in range(1, 11):
                for er in [1/17, 1/9, 1/5, 1/3, 1/2, 2/3, 4/5, 8/9, 16/17]:
                    args = get_args_dict(
                        dataset, alg, k, l, gm, epsilon=eps, cutoff=2, e0_ratio=er, seed=sd)
                    get_dataset_info(args)
                    H.start(args)

    H.wait()
