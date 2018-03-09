import random

from plugins.cross_team_lunch.state import User


def get_group_list(users, slack_user_id_to_team, users_per_group):
    num_groups = (len(users) + users_per_group - 1) / users_per_group

    # randomly shuffle users and then sort by team
    users = users[:]
    random.shuffle(users)
    users.sort(key=lambda user: slack_user_id_to_team[user.slack_user_id])

    # assign users to groups based on the new ordering, will spread out people on the same team
    group_mapping = {}
    for i, user in enumerate(users):
        group_mapping[user.slack_user_id] = i % num_groups

    group_list = [[] for _ in xrange(num_groups)]
    for user in users:
        group_list[group_mapping[user.slack_user_id]].append(user)

    return group_list


if __name__ == '__main__':
    users = [User(chr(ord('a') + i), '') for i in xrange(25)]
    slack_user_id_to_team = {chr(ord('a') + i): str(i % 3) for i in xrange(25)}
    users_per_group = 5
    group_list = get_group_list(users, slack_user_id_to_team, users_per_group)
    for i, group in enumerate(group_list):
        print 'GROUP %s' % i
        for user in group:
            print user.slack_user_id, slack_user_id_to_team[user.slack_user_id]
