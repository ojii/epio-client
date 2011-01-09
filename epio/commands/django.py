import sys
from epio.commands import AppCommand, CommandError

class Command(AppCommand):
    help = 'Run various Django commands.\n\nAvailable commands: syncdb, migrate, createsuperuser,' \
           'loaddata, dumpdata'

    def handle_app(self, app, command=None, *args, **options):
        client = self.get_client(options)

        stdin = ""
        # Work out the commandline and stdin we need to provide
        if command is None:
            raise CommandError("You must supply a command to run, e.g. syncdb.")
        elif command == "syncdb":
            cmdline = "django-admin.py syncdb --noinput %s" % " ".join(args)
        elif command == "migrate":
            cmdline = "django-admin.py migrate --noinput %s" % " ".join(args)
        elif command == "createsuperuser":
            username = raw_input("Username: ")
            email = raw_input("Email: ")
            password = raw_input("Password (will be echoed): ")
            stdin = "%(username)s\n%(email)s\n%(password)s\n%(password)s\n" % locals() 
            cmdline = "django-admin.py createsuperuser"
        else:
            cmdline = "django-admin.py %s %s" % (command, " ".join(args))

        # Send the command request
        response, content = client.post("app/%s/run_command/" % app, {
            "cmdline": cmdline,
            "stdin": stdin,
        })

        # What came back?
        if response.status in (200, ):
            print content['output']
            sys.exit(content['returncode'])
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


