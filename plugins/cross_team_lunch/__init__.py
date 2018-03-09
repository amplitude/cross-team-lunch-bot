from __future__ import unicode_literals
from concurrent import futures
import datetime
import logging
import string
import time

import pytz
from plugins.cross_team_lunch import teams, groups, restaurants
from plugins.cross_team_lunch.slack import SlackHelpers
from plugins.cross_team_lunch.state import CrossTeamLunchDB, User, UserState
from rtmbot.core import Plugin, Job


TIMEZONE = pytz.timezone('US/Pacific')


def current_week():
    now = datetime.datetime.now(tz=TIMEZONE)
    start = now - datetime.timedelta(days=now.weekday())
    return start.strftime('%Y-%m-%d')


class CrossTeamLunchPlugin(Plugin, SlackHelpers):

    BOT_USER_ID = 'U66J4ATEK'

    YES_RESPONSES = ['ya', 'yea', 'yeah', 'yep', 'yes', 'yup', 'sure', 'ok', 'absolutely', 'absolutely', 'sureies', 'right', 'course', 'thumbsup', 'okay']
    NO_RESPONSES = ['no', 'nope', 'cant', 'can\'t', 'busy', 'sorry', 'wfh', 'ooo']

    CONFIRM_ATTENDANCE = '''Great to hear! :thumbsup: I'll be reaching out Friday morning with your group.'''
    ASK_REASON = '''That's unfortunate. :disappointed: Could you let me know why you can't make it?'''
    CLARIFY_ATTENDANCE = '''Sorry, I'm not sure what you're saying. :confused: Please answer "yes" or "no".'''
    CONFIRM_REASON = '''Got it, you can't attend the cross team lunch this week because "{reason}". I hope you can make it next week! :wave:'''
    NO_CONVERSATION = '''It doesn't look we we have an active conversation. If you're bored, perhaps check out the blog? https://amplitude.com/blog/'''

    def __init__(self, slack_client=None, plugin_config=None):
        super(CrossTeamLunchPlugin, self).__init__(
            name='CrossTeamLunch', slack_client=slack_client, plugin_config=plugin_config
        )
        self.db = CrossTeamLunchDB()

    def register_jobs(self):
        logging.info('Registering jobs for CrossTeamLunchPlugin')
        # self.jobs = [TestJob(self.db)]
        self.jobs = [AttendanceJob(self.db, self.debug), MakeGroupsJob(self.db, self.debug)]

    def process_message(self, data):
        # logging.info('Received: %s', data)
        channel_id = data['channel']
        week = current_week()
        if channel_id.startswith('D'):
            slack_user_id = data.get('user')
            if not slack_user_id or slack_user_id == self.BOT_USER_ID:
                return

            user_state = self.db.get_user_state(slack_user_id)
            logging.info('Received IM from user %s in state %s', slack_user_id, user_state)
            if user_state == UserState.WAITING_ATTENDANCE:
                text = data.get('text')
                if text:
                    self._check_attendance_response(week, channel_id, slack_user_id, text)
            elif user_state == UserState.WAITING_REASON:
                text = data.get('text')
                if text:
                    self._check_reason_response(week, channel_id, slack_user_id, text)
            else:
                text = data.get('text')
                if text:
                    logging.info('No expected conversation for user %s', slack_user_id)
                    self._send_message(
                        self.slack_client, channel_id, self.NO_CONVERSATION, unfurl_links=False
                    )

    def _check_attendance_response(self, week, channel_id, slack_user_id, text):
        is_yes = self._is_yes(text)
        is_no = self._is_no(text)
        if is_yes and not is_no:
            logging.info('Confirmed attendance for user %s', slack_user_id)
            self._send_message(self.slack_client, channel_id, self.CONFIRM_ATTENDANCE)
            self.db.record_response(week, slack_user_id, 1)
            self.db.set_user_state(slack_user_id, UserState.NONE)
        elif is_no and not is_yes:
            logging.info('Confirmed absence for user %s', slack_user_id)
            self._send_message(self.slack_client, channel_id, self.ASK_REASON)
            self.db.record_response(week, slack_user_id, 0)
            self.db.set_user_state(slack_user_id, UserState.WAITING_REASON)
        else:
            logging.info('Clarifying attendance for user %s', slack_user_id)
            self._send_message(self.slack_client, channel_id, self.CLARIFY_ATTENDANCE)

    def _is_yes(self, text):
        return any(w in self.YES_RESPONSES for w in self._get_words(text))

    def _is_no(self, text):
        return any(w in self.NO_RESPONSES for w in self._get_words(text))

    def _get_words(self, text):
        return ''.join(c.lower() for c in text if c not in string.punctuation).split(' ')

    def _check_reason_response(self, week, channel_id, slack_user_id, text):
        logging.info('Recorded reason "%s" for user %s', text, slack_user_id)
        self.outputs.append([channel_id, self.CONFIRM_REASON.format(reason=text)])
        self.db.record_reason(week, slack_user_id, text)
        self.db.set_user_state(slack_user_id, UserState.NONE)


class TestJob(Job, SlackHelpers):

    INTERVAL = 60 * 10

    def __init__(self, db):
        super(TestJob, self).__init__(self.INTERVAL)
        self.db = db

    def run(self, slack_client):
        im_channels = self._get_im_channels_by_user(slack_client)
        self._send_message(
            slack_client, im_channels[u'U035N6MAK'], text='<https://google.com|Google>',
            unfurl_links=False
        )


class AttendanceJob(Job, SlackHelpers):

    INTERVAL = 60 * 30
    TYPE = 'attendance'
    TARGET_MINUTE = (3, 15, 0)  # Thursday, 3pm PST

    FIRST_MESSAGE = '''Hello! I'm the datamonster, and I'm here to make sure Amplitude is awesome.'''
    QUESTION = '''There's a cross-team lunch happening tomorrow! :knife_fork_plate: Will you be attending?'''

    def __init__(self, db, debug):
        super(AttendanceJob, self).__init__(self.INTERVAL)
        self.db = db
        self.debug = debug
        self.executor = futures.ThreadPoolExecutor(max_workers=1)

    def run(self, slack_client):
        try:
            now = datetime.datetime.now(tz=TIMEZONE)
            if (now.weekday(), now.hour, now.minute) >= self.TARGET_MINUTE:
                week = current_week()
                if not self.db.check_job(week, self.TYPE):
                    logging.info('Running AttendanceJob')
                    def do_attendance():
                        try:
                            self._ask_user_attendance(slack_client, week)
                            self.db.mark_job(week, self.TYPE)
                        except:
                            logging.exception('Failed to ask user attendance')
                    self.executor.submit(do_attendance)
        except:
            logging.exception('Failed running AttendanceJob')
        return []

    def _ask_user_attendance(self, slack_client, week):
        users = self._get_all_sf_users_with_team(slack_client, debug=self.debug)
        im_channels = self._get_im_channels_by_user(slack_client)
        for user, _ in users:
            if user.slack_user_id not in im_channels:
                logging.info('Opening IM channel for user %s', user)
                channel_id = self._open_im_channel(slack_client, user.slack_user_id)
                self._send_message(slack_client, channel_id, self.FIRST_MESSAGE)
                im_channels[user.slack_user_id] = channel_id

        for user, _ in users:
            if not self.db.user_has_response(week, user):
                # don't repeat ask the user even if the job runs again
                logging.info('Asking user %s for attendance', user)
                channel_id = im_channels[user.slack_user_id]
                self._send_message(slack_client, channel_id, self.QUESTION)
                self.db.set_user_state(user.slack_user_id, UserState.WAITING_ATTENDANCE)
                self.db.record_empty_response(week, user)


class MakeGroupsJob(Job, SlackHelpers):

    INTERVAL = 60 * 10
    TYPE = 'make_groups'
    TARGET_MINUTE = (4, 11, 0)  # Friday, 11am PST

    USERS_PER_GROUP = 6
    NUM_RESTAURANT_SUGGESTIONS = 4

    GROUP_INTRO = '''Hi all, you've been assigned to the same cross-team lunch group today! Please meet up at 11:50 to go out to lunch.'''
    RESTAURANT_MESSAGE = '''To help you get started, here are a few restaurant suggestions:'''

    def __init__(self, db, debug):
        super(MakeGroupsJob, self).__init__(self.INTERVAL)
        self.db = db
        self.debug = debug

    def run(self, slack_client):
        try:
            now = datetime.datetime.now(tz=TIMEZONE)
            if (now.weekday(), now.hour, now.minute) >= self.TARGET_MINUTE:
                week = current_week()
                if not self.db.check_job(week, self.TYPE):
                    logging.info('Running MakeGroupsJob')
                    self._make_groups(slack_client, week)
                    self.db.mark_job(week, self.TYPE)
        except:
            logging.exception('Failed running MakeGroupsJob')
        return []

    def _make_groups(self, slack_client, week):
        users_with_team = self._get_all_sf_users_with_team(slack_client, debug=self.debug)
        slack_user_id_to_team = {user.slack_user_id: team for user, team in users_with_team}
        accepted_users = self.db.get_users_with_response(week, 1)
        group_list = groups.get_group_list(
            accepted_users, slack_user_id_to_team, self.USERS_PER_GROUP
        )

        logging.info('Made %s groups for %s users', len(group_list), len(accepted_users))
        self._message_groups(slack_client, group_list)
        self.db.save_groups(week, group_list)
        self._reset_user_states(users_with_team)

    def _message_groups(self, slack_client, group_list):
        for group in group_list:
            logging.info('Messaging group %s', group)
            restaurant_list = restaurants.get_random_restaurants(self.NUM_RESTAURANT_SUGGESTIONS)
            slack_user_ids = [user.slack_user_id for user in group]
            channel_id = self._open_mpim_channel(slack_client, slack_user_ids)
            self._send_message(slack_client, channel_id, self.GROUP_INTRO)
            self._send_message(
                slack_client, channel_id, self._get_restaurant_message(restaurant_list),
                unfurl_links=False
            )

    def _get_restaurant_message(self, restaurant_list):
        message = self.RESTAURANT_MESSAGE
        for i, restaurant in enumerate(restaurant_list):
            message += '\n<{yelp_link}|{name}> ({cuisine}, {walk_time} min walk)'.format(
                **restaurant.__dict__
            )
        return message

    def _reset_user_states(self, users_with_team):
        for user, _ in users_with_team:
            self.db.set_user_state(user.slack_user_id, UserState.NONE)
