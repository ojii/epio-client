import sys
import getpass
from epio.commands import AppNameCommand, CommandError
from epio.commands.run_command import Command as RunCommand

class Command(AppNameCommand):
    help = 'Run various Django commands.\n\nAvailable commands: syncdb, migrate, createsuperuser,' \
           'loaddata, dumpdata'

    def handle_app_name(self, app_name, command=None, *args, **options):

        # Work out the commandline and stdin we need to provide
        if command is None:
            raise CommandError("You must supply a command to run, e.g. syncdb.")
        args = ["django-admin.py", command] + list(args)

        # Dispatch that to the run_command module
        RunCommand().handle_app_name(app_name, *args)


