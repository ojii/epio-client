from epio.commands import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Sets the default app'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Usage: epio set_app appname")
        try:
            fh = open(".epio-app", "w")
            fh.write(args[0])
            fh.close()
        except IOError:
            raise CommandError("Could not write .epio-app file. Please check your permissions.")
