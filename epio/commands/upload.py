import os
import subprocess
from epio.commands import AppNameCommand, CommandError

class Command(AppNameCommand):
    help = 'Uploads the current directory as an app.'
    
    def handle_app_name(self, app, **options):
        # Make sure they have git
        try:
            subprocess.call(["git"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            raise CommandError("You must install git before you can use epio upload.")
        
        print "Uploading %s as app %s" % (os.path.abspath("."), app)
        # Make a temporary git repo, commit the current directory to it, and push
        if os.path.exists(".epio-git"):
            subprocess.call(["rm", "-rf", ".epio-git"])
        env = dict(os.environ)
        env.update({"GIT_DIR": ".epio-git", "GIT_WORK_TREE": "."})
        subprocess.Popen(
            ["git", "init"],
            env=env,
            stdout=subprocess.PIPE,
        ).communicate()
        fh = open(".epio-git/info/exclude", "w")
        fh.write(".git\n.hg\n.svn\n.epio-git")
        fh.close()
        subprocess.Popen(
            ["git", "add", "."],
            env=env,
            stdout=subprocess.PIPE,
        ).communicate()
        subprocess.Popen(
            ["git", "commit", "-a", "-m", "Auto-commit."],
            env=env,
            stdout=subprocess.PIPE,
        ).communicate()
        subprocess.call(
            ["git", "push", "vcs@%s:%s" % (
                os.environ.get('EPIO_HOST', 'upload.ep.io').split(":")[0],
                app,
            ), "master"],
            env=env,
        )
        subprocess.call(["rm", "-rf", ".epio-git"])


