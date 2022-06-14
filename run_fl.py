from facility_loc.algo_fl import greedy_fl, read_items, read_users, calc_kernel_radius

items = read_items('data/foursquare/tky-items.csv')
users = read_users('data/foursquare/tky-users.csv')

ks = range(1, 11, 3)

for k in ks:
    radius = calc_kernel_radius(items, users)
    print(radius)

    sol, benefits, time = greedy_fl(items, users, k, radius)
    print(sol, sum(benefits), time)
