from optparse import make_option, OptionParser
import re
import epio
from epio.client import EpioClient
import sys

class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.

    """
    pass


class BaseCommand(object):
    option_list = (
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2', '3'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'
        ),
        make_option('-e', '--email', 
            help='Your email registered with ep.io. Required if you are not '
                 'already logged in'
        ),
        make_option('-p', '--password',
            help='Your ep.io password. If not given, you will be prompted'
        ),
        make_option('-t', '--token-file',
            help='File to store login token',
            default='~/.epio/access_token',
        ),
        make_option('-a', '--app',
            help='App to perform action against',
        ),
    )
    help = ''
    args = ''
    
    def usage(self, subcommand):
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.

        """
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage
    
    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            version=epio.__version__,
                            option_list=self.option_list)

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.

        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()
    
    def run_from_argv(self, argv):
        """
        Given arguments, run this command.
        """
        parser = self.create_parser(argv[0], argv[1])
        options, args = parser.parse_args(argv[2:])
        try:
            self.handle(*args, **options.__dict__)
        except CommandError, e:
            sys.stderr.write('%s\n' % e)
            sys.exit(1)
    
    def get_client(self, options):
        """
        Return a epio client with options passed as arguments.
        """
        return EpioClient(
            token_file=options['token_file'],
            email=options['email'],
            password=options['password'],
        )

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.

        """
        raise NotImplementedError()
    

class AppNameCommand(BaseCommand):
    """
    A command that takes a valid app name, but doesn't resolve it to an ID.
    """

    app_name_optional = False
    args = '[app name]'

    def handle(self, *args, **options):
        # Was an app passed in?
        app_name = options['app']
        del options['app']
        if not app_name:
            # Try reading app name from a dotfile
            try:
                app_name = open(".epio-app").read().strip()
            except IOError:
                if self.app_name_optional:
                    app_name = None
                else:
                    raise CommandError("Please provide an app name using -a.")
        # Make sure the name is valid
        if app_name is not None and not re.match(r'^[a-z0-9-_]+$', app_name):
            raise CommandError(
                "Name must only contain alphanumeric characters, "
                "dashes and underscores."
            )
        return self.handle_app_name(app_name, *args, **options)

    def handle_app_name(self, app, **options):
        raise NotImplementedError()


class AppCommand(AppNameCommand):
    """
    A command that takes a valid app name, and resolves it to an ID.
    """

    def handle_app_name(self, app_name, *args, **options):
        # Look up the app's ID
        client = self.get_client(options)
        response, content = client.get("app/name/%s/" % app_name)
        if response.status == 404:
            raise CommandError("There is no app with the name '%s'." % app_name)
        elif response.status == 200:
            app = content['app']['id']
        else:
            raise CommandError("Unknown error in resolving app name (%s)" % response.status)
        self.app_name = app_name
        return self.handle_app(app, *args, **options)

    def handle_app(self, app, **options):
        raise NotImplementedError()



