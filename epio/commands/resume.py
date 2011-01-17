from epio.commands import AppCommand, CommandError

class Command(AppCommand):
    help = 'Resumes an app on ep.io'

    def handle_app(self, app, **options):
        client = self.get_client(options)
        
        response, content = client.post(
            'app/%s/resume/' % app,
            {},
        )
        if response.status in (200, 204):
            print "Resumed http://%s.ep.io" % self.app_name
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


