EMAIL_DOMAIN = 'amplitude.com'

# users are looked up in slack by name@domain
USERS_BY_TEAM = {
    'SF': {
        'Engineering': [
            'eng1',
            'eng2',
            'eng3',
            'eng4',
            'eng5',
        ],
        'Product/Design': [
            'pd1',
            'pd2',
            'pd3',
        ],
        'Success': [
            'success1',
            'success2',
            'success3',
            'success4',
        ],
        'Marketing': [
            'mark1',
            'mark2',
        ],
        'Sales': [
            'sales1',
            'sales2',
            'sales3',
            'sales4',
            'sales5',
            'sales6',
        ],
        'G&A': [
            'ga1',
            'ga2',
        ],
    },
    # other offices can go here
}


EMAIL_TO_TEAM_OFFICE = {
    user + '@' + EMAIL_DOMAIN: (team, office)
    for office, office_users in USERS_BY_TEAM.iteritems()
    for team, team_users in office_users.iteritems()
    for user in team_users
}


def get_team_office(email):
    return EMAIL_TO_TEAM_OFFICE.get(email)
