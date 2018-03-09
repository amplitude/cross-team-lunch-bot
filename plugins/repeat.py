from rtmbot.core import Plugin


class RepeatPlugin(Plugin):

    def process_message(self, data):
        self.outputs.append([data['channel'], data['text']])
