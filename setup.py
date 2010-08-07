from setuptools import setup

VERSION = '0.1'
PACKAGE = 'notificationoptout'

setup(
	name = 'NotificationOptOutPlugin',
	version = VERSION,
	description = "Allow users to opt-out from notifications.",
	author = 'Mitar',
	author_email = 'mitar.trac@tnode.com',
	url = 'http://mitar.tnode.com/',
	keywords = 'trac plugin',
	license = "GPLv3",
	packages = [PACKAGE],
    include_package_data = True,
    zip_safe = False,
	entry_points={
		'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE),
	},
)
