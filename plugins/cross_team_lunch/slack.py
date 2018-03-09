import logging
import time

from plugins.cross_team_lunch import teams
from plugins.cross_team_lunch.state import User


class SlackError(RuntimeError):
    pass


class SlackHelpers(object):

    SLEEP = 1

    def _get_all_sf_users_with_team(self, slack_client, debug=True):
        time.sleep(self.SLEEP)
        response = self._slack_api_call_with_retry(slack_client, 'users.list')

        users = []
        for member in response['members']:
            if member['deleted']:
                continue

            user = User(member['id'], member['name'])

            if 'email' not in member['profile']:
                continue

            email = member['profile']['email']
            if teams.EMAIL_DOMAIN not in email:
                continue

            team_office = teams.get_team_office(email)
            if team_office is None:
                continue

            if team_office[1] == 'SF':
                users.append((user, team_office[0]))
        return users

    def _get_im_channels_by_user(self, slack_client):
        time.sleep(self.SLEEP)
        response = self._slack_api_call_with_retry(slack_client, 'im.list')

        im_channels = {}
        for im in response['ims']:
            im_channels[im['user']] = im['id']
        return im_channels

    def _open_im_channel(self, slack_client, slack_user_id):
        time.sleep(self.SLEEP)
        response = self._slack_api_call_with_retry(slack_client, 'im.open', user=slack_user_id)
        return response['channel']['id']

    def _close_im_channel(self, slack_client, channel_id):
        time.sleep(self.SLEEP)
        self._slack_api_call_with_retry(slack_client, 'im.close', channel=channel_id)

    def _open_mpim_channel(self, slack_client, slack_user_ids):
        time.sleep(self.SLEEP)
        response = self._slack_api_call_with_retry(
            slack_client, 'mpim.open', users=','.join(slack_user_ids)
        )
        return response['group']['id']

    def _send_message(self, slack_client, channel_id, text, **kwargs):
        time.sleep(self.SLEEP)
        self._slack_api_call_with_retry(
            slack_client, 'chat.postMessage', channel=channel_id, as_user=True, text=text, **kwargs
        )

    def _slack_api_call_with_retry(self, slack_client, *args, **kwargs):
        tries = 5
        while True:
            try:
                response = slack_client.api_call(*args, **kwargs)
                if not response['ok']:
                    raise SlackError(response['error'])
                return response
            except:
                tries -= 1
                if tries == 0:
                    raise
                else:
                    logging.warn('Error making slack api call, %s tries left...', tries)
