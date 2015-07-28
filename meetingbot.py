# Backward compatibility
from errbot.version import VERSION
from errbot.utils import version2array
if version2array(VERSION) >= [1,6,0]:
    from errbot import botcmd, BotPlugin
else:
    from errbot.botplugin import BotPlugin
    from errbot.jabberbot import botcmd
import datetime
from pytz import timezone


__author__ = 'Tomas Nunez'

class MeetingBot(BotPlugin):
    @botcmd
    def meeting_start(self, mess, args):
        """ Resets all counters to start a meeting and keep track of time
        Example: !meeting start
        """
        date_today = self.current_date()
        time_now = self.current_time()
        meetings = self.shelf['meetings']

        if date_today in meetings:
            return "There is already meeting data for today. Do you want to reset it, append to it or create a new meeting for today?"
        else:
            meetings[date_today] = {time_now : 'TPGSDINT'}
            self.shelf['meetings'] = meetings
            return "Meeting started!"

    @botcmd
    def meeting_end(self, mess, args):
        """ Ends a meeting
        Example: !meeting end
        """
        date_today = self.current_date()
        time_now = self.current_time()

        meetings = self.shelf['meetings']
        meetings[date_today][time_now] = "END OF MEETING"
        self.shelf['meetings'] = meetings


    @botcmd
    def meeting_reset(self, mess, args):
        """ Delete data from a meeting
        Example: !meeting reset
        """
        date_today = self.current_date()
        meetings = self.shelf['meetings']

        try:
            del meetings[date_today]
            self.shelf['meetings'] = meetings
            return "Meeting data for day "+date_today+" successfully reset"
        except KeyError:
            return "No meetings today"

    @botcmd
    def meeting_client(self, mess, args):
        date_today = self.current_date()
        time_now = self.current_time()
        client = args.strip()

        meetings = self.shelf['meetings']
        meetings[date_today][time_now] = client
        self.shelf['meetings'] = meetings

    @botcmd
    def meeting_times(self, mess, args):
        date_today = self.current_date()
        meeting = sorted(self.shelf['meetings'][date_today].items())
        prev_time = None
        times = {}
        for time, client in meeting:
            if prev_time == None:
                prev_time = time
                prev_client = client
            else:
                time_used = time - prev_time
#                yield "Client " + prev_client + " used " + str(time_used) + " time"
                try:
                    times[prev_client] = times[prev_client] + time_used
                except KeyError:
                    times[prev_client] = time_used

                prev_time = time
                prev_client = client
        if prev_client != "END OF MEETING":
            yield "WARNING: The meeting was not finalized with \"!meeting end\" command. You may want to end it now."
        for client_meeting, time_meeting in times.items():
            rest_seconds=time_meeting.seconds%60
            yield "Client " + client_meeting + " used " + str((time_meeting.seconds-rest_seconds)/60) + " minutes " + str(rest_seconds) + " seconds"
        return


    @botcmd
    def meeting_summary(self, mess, args):
        """ Shows a summary of the time spent on the meeting
        Example: !meeting summary 2015-7-16
        """
        date_today = self.current_date()
        try:
            meeting = sorted(self['meetings'][date_today].items())
        except KeyError:
            return "No meetings today"

        for time_meeting, client in meeting:
            yield str(time_meeting.strftime('%H:%M:%S')) + ": " + client


    @botcmd
    def meeting_list(self, mess, args):
        """ Lists all available meetings
        Example: !meeting list
        """
        return self['meetings'].keys()

    @staticmethod
    def current_date():
        date_format = "%Y-%m-%d"
        return datetime.date.today().strftime(date_format)

    @staticmethod
    def current_time():
        return datetime.datetime.now(timezone('UTC'))

    @botcmd
    def time_now(self, mess, args):
        time_format = "%H:%M:%S %Z%z"
        return self.current_time().strftime(time_format)

    @botcmd
    def date_today(self, mess, args):
        return self.current_date()

    @botcmd
    def meeting_init(self, mess, args):
        self['meetings'] = {}
