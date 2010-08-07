from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.prefs import web_ui as prefswebui
from trac.ticket import notification as ticketnotification

def get_known_users_optout(env, cnx=None):
	"""
	Generator that yields information about all known users, i.e. users
	that have logged in to this Trac environment and possibly set their name
	and e-mail.

	This function generates one tuple for every user, of the form
	(username, name, email, optout) ordered alpha-numerically by username.

	@param env: environment
	@param cnx: the database connection; if ommitted, a new connection is
				retrieved
	"""

	if not cnx:
		cnx = env.get_db_cnx()
	cursor = cnx.cursor()
	cursor.execute("SELECT DISTINCT s.sid, n.value, e.value, o.value "
					"FROM session AS s "
					" LEFT JOIN session_attribute AS n ON (n.sid=s.sid "
					"  and n.authenticated=1 AND n.name = 'name') "
					" LEFT JOIN session_attribute AS e ON (e.sid=s.sid "
					"  AND e.authenticated=1 AND e.name = 'email') "
					" LEFT JOIN session_attribute AS o ON (o.sid=s.sid "
					"  AND o.authenticated=1 AND o.name = 'ticket-notification-optout') "
					"WHERE s.authenticated=1 ORDER BY s.sid")
	for username,name,email,optout in cursor:
		yield username, name, email, optout

saved_do_save = None
def do_save(self, req):
	"""
	Saves changes to notification preferences.
	"""

	if 'ticket-notification-optout' not in prefswebui.PreferencesModule._form_fields:
		prefswebui.PreferencesModule._form_fields.append('ticket-notification-optout')
	if 'ticket-notification-optout' not in self._form_fields:
		self._form_fields.append('ticket-notification-optout')
	val = req.args.get('ticket-notification-optout')
	if val:
		req.args['ticket-notification-optout'] = '1'
	return saved_do_save(self, req)

saved_get_recipients = None
def get_recipients(self, tktid):
	"""
	Returns a pair of list of not opt-out subscribers to the ticket `tktid`.
	
	First list represents the direct recipients (To:), second list
	represents the recipients in carbon copy (Cc:).
	"""

	(to, cc) = saved_get_recipients(self, tktid)
	self.env.log.debug("NotificationOptOut before optout, to: %s, cc: %s" % (to, cc))
	for username, name, email, optout in get_known_users_optout(self.env):
		if optout:
			to = [addr for addr in to if addr != username and addr != email]
			cc = [addr for addr in cc if addr != username and addr != email]
	self.env.log.debug("NotificationOptOut after optout, to: %s, cc: %s" % (to, cc)) 
	return (to, cc)

class NotificationOptOut(Component):
	"""
	This component adds to Trac e-mail notifications opt-out preference for users.
	"""
	
	implements(IEnvironmentSetupParticipant)

	def __init__(self):
		global saved_do_save
		global saved_get_recipients
		if self.compmgr.enabled[self.__class__]:
			if saved_do_save is None:
				saved_do_save = prefswebui.PreferencesModule._do_save
				prefswebui.PreferencesModule._do_save = do_save
			if saved_get_recipients is None:
				saved_get_recipients = ticketnotification.TicketNotifyEmail.get_recipients
				ticketnotification.TicketNotifyEmail.get_recipients = get_recipients

	def environment_created(self):
		"""
		Called when a new Trac environment is created.
		"""

		pass

	def environment_needs_upgrade(self, db):
		"""
		Called when Trac checks whether the environment needs to be upgraded.
		
		Should return `True` if this participant needs an upgrade to be
		performed, `False` otherwise.
		
		"""

		return False

	def upgrade_environment(self, db):
		"""
		Actually performs an environment upgrade.

		Implementations of this method should not commit any database
		transactions. This is done implicitly after all participants have
		performed the upgrades they need without an error being raised.
		"""

		pass
