import os
import sys
from epio.commands import AppCommand, CommandError

class Command(AppCommand):
    help = 'Shows processes currently running for this app.'

    def handle_app(self, app, **options):
        client = self.get_client(options)

        # Get the current processes
        response, content = client.get('app/%s/processes/' % app)

        if response.status == 200:
            print "%-10s  %-30s  %s" % ("STATE", "LOCATION", "TYPE")
            for type, instances in content['processes'].items():
                for host, port, state in instances:
                    if host.endswith(".ep.io"):
                        host = host[:-6]
                    print "%-10s  %-30s  [%s]" % (
                        state,
                        "%s:%s" % (host, port),
                        type,
                    )
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


