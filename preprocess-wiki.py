import csv

items = set()
users = dict()

with open('data/wikibooks-jp.csv', 'r') as input_file:
    csvreader = csv.reader(input_file, delimiter='\t')
    for row in csvreader:
        item_id = int(row[0])
        user_id = int(row[1])
        items.add(item_id)
        if user_id not in users.keys():
            users[user_id] = set()
            users[user_id].add(item_id)
        else:
            users[user_id].add(item_id)

with open('data/wikibooks/items-jp.csv', 'w', newline='') as output_file:
    csvwriter = csv.writer(output_file, delimiter=' ')
    for item in items:
        csvwriter.writerow([item])

with open('data/wikibooks/users-jp.csv', 'w') as output_file:
    for user in users.keys():
        output_file.write(str(user) + ':')
        for item in users[user]:
            output_file.write(str(item) + ' ')
        output_file.write('\n')
