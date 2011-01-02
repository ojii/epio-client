import os
import sys
from epio.commands import AppNameCommand, CommandError

class Command(AppNameCommand):
    help = 'Create an app.\n\nThe name, if provided, must only contain alphanumeric ' \
           'characters, dashes and underscores.'

    app_name_optional = True

    def handle_app_name(self, app_name, arg_app_name=None, **options):
        client = self.get_client(options)

        # Is there already a file here?
        if os.path.exists(".epio-app"):
            print "This directory is already associated with the app '%s'" % open(".epio-app").read().strip()
            print "Please remove the .epio-app file if you wish to unassociate it."
            sys.exit(1)

        # If there's no app name passed in via an option, try the first argument.
        if app_name is None:
            app_name = arg_app_name
        
        response, content = client.post(
            'app/create/',
            {
                'name': app_name or "<random>",
            },
        )
        if response.status == 201:
            print "Created http://%s.ep.io" % content['app']['names'][0]
            print "Remember to create an epio.ini file!"
            try:
                fh = open(".epio-app", "w")
                fh.write(content['app']['names'][0])
                fh.close()
            except IOError:
                print "Could not write .epio-app file. You'll have to use -a on commands."
        elif response.status == 200:
            if "name" in content['form']['errors']:
                raise CommandError(", ".join(content['form']['errors']['name']))
            else:
                raise CommandError("Unknown error: %s: %s" % (response.status, content))
        elif response.status == 409:
            raise CommandError("An app called '%s' already exists. Try another name" % app_name)
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


