import os
import sqlite3

from concurrent import futures


class User(object):

    def __init__(self, slack_user_id, slack_handle):
        self.slack_user_id = slack_user_id
        self.slack_handle = slack_handle

    def _key(self):
        return (self.slack_user_id, self.slack_handle)

    def __repr__(self):
        return 'User(%s, %s)' % (repr(self.slack_user_id), repr(self.slack_handle))

    def __str__(self):
        return self.__repr__()


class UserState(object):
    NONE = 'none'
    WAITING_ATTENDANCE = 'waiting_attendance'
    WAITING_REASON = 'waiting_reason'


class CrossTeamLunchDB(object):

    def __init__(self):
        self.db_dir = '/mnt/data/cross_team_lunch'
        try:
            os.makedirs(self.db_dir)
        except:
            pass

        # dedicated thread for running sql queries (db conn must be initialized on the same thread)
        self.executor = futures.ThreadPoolExecutor(max_workers=1)
        self._init()

    def _init(self):
        def run():
            self.db_conn = sqlite3.connect('%s/%s' % (self.db_dir, 'state.db'))
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS user_states (
                    slack_user_id  TEXT,
                    state          TEXT,
                    PRIMARY KEY (slack_user_id)
                )
            ''')
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    week  TEXT,
                    type  TEXT,
                    PRIMARY KEY (week, type)
                )
            ''')
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    week           TEXT,
                    slack_user_id  TEXT,
                    slack_handle   TEXT,
                    accepted       INTEGER,
                    reason         TEXT,
                    PRIMARY KEY (week, slack_user_id)
                )
            ''')
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    week           TEXT,
                    slack_user_id  TEXT,
                    slack_handle   TEXT,
                    group_id       INTEGER,
                    PRIMARY KEY (week, slack_user_id)
                )
            ''')
            self.db_conn.commit()
        self.executor.submit(run).result()

    def get_user_state(self, slack_user_id):
        def run():
            row = self.db_conn.execute('''
                SELECT * FROM user_states
                WHERE slack_user_id = ?
            ''', (slack_user_id,)).fetchone()
            return (row and row[1]) or UserState.NONE
        return self.executor.submit(run).result()

    def set_user_state(self, slack_user_id, state):
        def run():
            self.db_conn.execute('''
                DELETE FROM user_states
                WHERE slack_user_id = ?
            ''', (slack_user_id,))
            self.db_conn.execute('''
                INSERT INTO user_states
                VALUES (?, ?)
            ''', (slack_user_id, state))
            self.db_conn.commit()
        self.executor.submit(run).result()

    def mark_job(self, week, type):
        def run():
            self.db_conn.execute('''
                INSERT INTO jobs
                VALUES (?, ?)
            ''', (week, type))
            self.db_conn.commit()
        self.executor.submit(run).result()

    def check_job(self, week, type):
        def run():
            rows = self.db_conn.execute('''
                SELECT * FROM jobs
                WHERE week = ? AND type = ?
            ''', (week, type))
            return rows.fetchone() is not None
        return self.executor.submit(run).result()

    def record_empty_response(self, week, user):
        def run():
            self.db_conn.execute('''
                DELETE FROM responses
                WHERE week = ? AND slack_user_id = ? AND slack_handle = ?
            ''', (week, user.slack_user_id, user.slack_handle))
            self.db_conn.execute('''
                INSERT INTO responses
                VALUES (?, ?, ?, ?, ?)
            ''', (week, user.slack_user_id, user.slack_handle, -1, None))
            self.db_conn.commit()
        self.executor.submit(run).result()

    def record_response(self, week, slack_user_id, accepted):
        def run():
            self.db_conn.execute('''
                UPDATE responses
                SET accepted = ?
                WHERE week = ? AND slack_user_id = ?
            ''', (accepted, week, slack_user_id))
            self.db_conn.commit()
        self.executor.submit(run).result()

    def record_reason(self, week, slack_user_id, reason):
        def run():
            self.db_conn.execute('''
                UPDATE responses
                SET reason = ?
                WHERE week = ? AND slack_user_id = ?
            ''', (reason, week, slack_user_id))
            self.db_conn.commit()
        self.executor.submit(run).result()

    def get_users_with_response(self, week, response):
        def run():
            rows = self.db_conn.execute('''
                SELECT slack_user_id, slack_handle
                FROM responses
                WHERE week = ? AND accepted = ?
            ''', (week, response))
            return [User(row[0], row[1]) for row in rows]
        return self.executor.submit(run).result()

    def user_has_response(self, week, user):
        def run():
            rows = self.db.conn.execute('''
                SELECT 1
                FROM response
                WHERE week = ? AND slack_user_id = ?
            ''', week, user.slack_user_id)
            return rows.fetchone() is not None

    # groups is a list of lists of users
    def save_groups(self, week, group_list):
        def run():
            users_with_group = [
                (week, user.slack_user_id, user.slack_handle, group_idx)
                for group_idx, users_in_group in enumerate(group_list)
                for user in users_in_group
            ]
            self.db_conn.executemany('''
                INSERT INTO groups
                VALUES (?, ?, ?, ?)
            ''', users_with_group)
            self.db_conn.commit()
        self.executor.submit(run).result()


if __name__ == '__main__':
    db = CrossTeamLunchDB()
    db.record_response('2017-03-03', '1', 1)
    db.record_response('2017-03-03', '2', 0)
    db.record_response('2017-03-03', '3', 1)
    print db.get_users_with_response('2017-03-03', 1)
