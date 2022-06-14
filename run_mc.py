from max_cover.algo_mc import greedy_mc, read_items, read_users

items = read_items('data/wikibooks/items-jp.csv')
users = read_users('data/wikibooks/users-jp.csv')

ks = range(1, 11, 3)

for k in ks:
    sol, cov, time = greedy_mc(items, users, k)
    print(sol, len(cov), time)
