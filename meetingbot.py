# Backward compatibility
from errbot.version import VERSION
from errbot.utils import version2array
if version2array(VERSION) >= [1, 6, 0]:
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
    meetings = self['meetings']

    if date_today in meetings:
      return "There is already meeting data for today. Do you want to delete it, append to it or create a new meeting for today?"
    else:
      meetings[date_today] = {time_now: 'internal'}
      self['meetings'] = meetings
      return "Meeting started!"

  @botcmd
  def meeting_end(self, mess, args):
    """ Ends a meeting
    Example: !meeting end
    """
    date_today = self.current_date()
    time_now = self.current_time()

    meetings = self['meetings']
    meetings[date_today][time_now] = "END OF MEETING"
    self['meetings'] = meetings

  @botcmd
  def meeting_reset(self, mess, args):
    """ Delete data from a meeting
    Example: !meeting reset
    """
    date_today = self.current_date()
    meetings = self['meetings']

    try:
      del meetings[date_today]
      self['meetings'] = meetings
      return "Meeting data for day " + date_today + " successfully reset"
    except KeyError:
      return "No meetings today"

  @botcmd
  def meeting_project(self, mess, args):
    date_today = self.current_date()
    time_now = self.current_time()
    project = args.strip().title()

    meetings = self['meetings']

    if project in self['aliases']:
      project = self['aliases'][project]

    yield "Now we started talking about " + project
    meetings[date_today][time_now] = project
    self['meetings'] = meetings

  @botcmd
  def meeting_times(self, mess, args):
    date_today = self.current_date()
    meeting = sorted(self['meetings'][date_today].items())
    prev_time = None
    times = {}
    for time, project in meeting:
      if prev_time == None: #first pass, nothing to compare to
        prev_time = time
        prev_project = project
      else:
        time_used = time - prev_time #not the first pass, so we can compare time now to time before
        try:
          times[prev_project] = times[prev_project] + time_used #adding the time to the project
        except KeyError:
          times[prev_project] = time_used
        prev_time = time
        prev_project = project
    if prev_project != "END OF MEETING":
      yield "WARNING: The meeting was not finalized with \"!meeting end\" command. You may want to end it now."
    for project_meeting, time_meeting in times.items():
      yield "Client " + project_meeting + " used " + str((time_meeting.seconds - time_meeting.seconds % 60) / 60 + (time_meeting.seconds % 60 > 0)) + " minutes"
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

  @botcmd
  def meeting_del(self, mess, args):
    """ Delete a meeting
    Example: !meeting delete 2015-7-15
    """
    date = args.strip().title()
    meetings = self['meetings']
    try:
      del meetings[date]
      self['meetings'] = meetings
      return "Meeting " + date + " deleted successfully"
    except KeyError:
      raise "There's no meeting for " + date + " in the database"

  @botcmd(split_args_with=None)
  def meeting_aliasadd(self, mess, args):
    """ Assigns an alias to a project name
    Example: !meeting addalias Project ProjectAlias
    """
    if len(args) <= 1:
      yield "You need a project AND an alias"
      return "Example: !meeting addalias Project Mega-Cool-Project"
    aliases = self['aliases']
    #projects = self['projects']
    project = args[0].strip().title()
    alias = " ".join(args[1:]).strip().title()

    yield "Project " + project + " and alias " + alias

    if alias in aliases:
      yield "Warning: Alias " + alias + " was already there with value " + aliases[alias] + ". Overwriting..."
    aliases[alias] = project
    self['aliases'] = aliases

  @botcmd
  def meeting_aliaslist(self, mess, args):
    """ Lists all available nicknames
    Example: !meeting aliaslist
    """
    return self['aliases']

  @botcmd
  def meeting_aliasdel(self, mess, args):
    """ Deletes a project alias
    Example: !meeting aliasdel ProjectAlias
    """
    alias = args.strip().title()
    aliases = self['aliases']
    try:
      del aliases[alias]
    except KeyError:
      raise "There's no alias " + alias + " in the database"

    self['aliases'] = aliases
    return "Project alias " + alias + " deleted successfully"


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

#  @botcmd
#  def meeting_init(self, mess, args):
#    self['meetings'] = {}

#  @botcmd
#  def meeting_aliasinit(self, mess, args):
#    self['aliases'] = {}
