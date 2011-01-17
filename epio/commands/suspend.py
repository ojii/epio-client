from epio.commands import AppCommand, CommandError

class Command(AppCommand):
    help = 'Suspends an app on ep.io (it will stop responding to HTTP requests)'

    def handle_app(self, app, **options):
        client = self.get_client(options)
        
        response, content = client.post(
            'app/%s/suspend/' % app,
            {},
        )
        if response.status in (200, 204):
            print "Suspended http://%s.ep.io" % self.app_name
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


