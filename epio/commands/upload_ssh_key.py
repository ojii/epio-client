import os, getpass, platform
import subprocess
from epio.commands import AppCommand, CommandError

SSH_IDENT = os.path.expanduser("~/.ssh/id_rsa")
SSH_CONFIG = os.path.expanduser("~/.ssh/config")

class Command(AppCommand):
    help = 'Uploads your public SSH key to ep.io (creating one in the process if required)'

    def get_public_key(self):
        "Gets the public key for the current user."
        proc = subprocess.Popen(
            ["ssh-keygen", "-y", "-f", SSH_IDENT],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )
        stdout, stderr = proc.communicate("")
        if proc.returncode:
            return None
        else:
            return stdout

    def win_setup_ssh(self):
        "Makes sure windows users can use their SSH configs"
        if not 'HOME' in os.environ:
            print "You do not seem to have the HOME environment variable required by git ssh."
            ans = prompt("Create it now? [y] ")
            if ans in (None, '', 'y', 'yes'):
                try:
                    import _winreg
                    key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, 'Environment')
                    _winreg.SetValue(key, "HOME", _winreg.REG_SZ,
                                     os.environ.get('USERPROFILE', None) or os.path.expanduser('~'))
                    _winreg.FlushKey(key)
                except EnvironmentError, e:
                    print "Permission Denied. Please manually set \%HOME\% to %s" % os.path.expanduser('~')

    def make_key(self):
        "Creates a new SSH key"
        returncode = subprocess.call(
            ["ssh-keygen", "-t", "rsa", "-f", SSH_IDENT, "-N",
             '-C', getpass.getuser()+"@"+platform.node(), ""],
            stdout = subprocess.PIPE,
        )
        if returncode:
            raise CommandError("Cannot create new SSH key; do you have the SSH client installed?")

    def win_write_keyinfo(self):
        "writes ssh config file to get around broken windows ssh-agent"
        try:
            with open(SSH_CONFIG, 'r') as file:
                origfile = file.read()
        except:
            origfile = ""
        # Spacing is significant here
        if not "Host epio" in origfile:
            epio_conf = "Host epio\n    Hostname upload.ep.io\n    User vcs\n    IdentityFile %s" % SSH_IDENT
            with open(SSH_CONFIG, 'w') as file:
                file.write(origfile)
                file.write(epioconf)

    def handle(self, **options):
        client = self.get_client(options)

        # First, see if we have an ssh public key
        public_key = self.get_public_key()

        if "Windows" in platform.platform():
            self.win_setup_ssh()
        if not public_key:
            self.make_key()
            public_key = self.get_public_key()
            if not public_key:
                raise CommandError("Unknown error making SSH key.")
            if "Windows" in platform.platform():
                self.win_write_keyinfo()

        response, content = client.post(
            '/account/sshkeys/',
            {
                "key": public_key,
            },
        )
        if response.status in (200, 302):
            if content and "form" in content and "errors" in content["form"]:
                print content['form']['errors']['key'][0]
            else:
                print "Added SSH key."
        else:
            raise CommandError("Unknown error, %s: %s" % (response.status, content))


