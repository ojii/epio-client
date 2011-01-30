import os
from epio.commands import AppNameCommand

class Command(AppNameCommand):
    help = 'Run an arbitary command.'

    def handle_app_name(self, app_name, *args, **options):
        # We just use SSH.
        os.execvp("ssh", [
            "ssh",
            "-t",
            "vcs@%s" % os.environ.get('EPIO_HOST', 'upload.ep.io').split(":")[0],
            "epio_command",
            app_name,
        ] + list(args))
