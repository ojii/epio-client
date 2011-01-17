from epio.commands import AppCommand, CommandError

class Command(AppCommand):
    help = 'Delete an app from ep.io.'

    def handle_app(self, app, **options):
        client = self.get_client(options)
        
        response, content = client.post(
            'app/%s/delete/' % app,
            {},
        )
        if response.status in (200, 204):
            print "Deleted http://%s.ep.io" % self.app_name
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


