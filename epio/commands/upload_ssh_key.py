import os
import subprocess
from epio.commands import AppCommand, CommandError

class Command(AppCommand):
    help = 'Uploads your public SSH key to ep.io (creating one in the process if required)'

    def get_public_key(self):
        "Gets the public key for the current user."
        proc = subprocess.Popen(
            ["ssh-keygen", "-y", "-f", os.path.expanduser("~/.ssh/id_rsa")],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )
        stdout, stderr = proc.communicate("")
        if proc.returncode:
            return None
        else:
            return stdout

    def make_key(self):
        "Creates a new SSH key"
        returncode = subprocess.call(
            ["ssh-keygen", "-t", "rsa", "-f", os.path.expanduser("~/.ssh/id_rsa"), "-N", ""],
            stdout = subprocess.PIPE,
        )
        if returncode:
            raise CommandError("Cannot create new SSH key; do you have the SSH client installed?")

    def handle(self, **options):
        client = self.get_client(options)

        # First, see if we have an ssh public key
        public_key = self.get_public_key()
        if not public_key:
            self.make_key()
            public_key = self.get_public_key()
            if not public_key:
                raise CommandError("Unknown error making SSH key.")
        
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


