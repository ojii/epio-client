import os
import subprocess
import tempfile
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
        repo_dir = tempfile.mkdtemp(prefix="epio-upload-")
        try:
            # Copy the files across
            subprocess.Popen(
                ["cp", "-RT", ".", repo_dir],
                stdout=subprocess.PIPE,
                cwd = os.getcwd(),
            ).communicate()
            # Init the git repo
            env = dict(os.environ)
            subprocess.Popen(
                ["git", "init"],
                env=env,
                stdout=subprocess.PIPE,
                cwd=repo_dir,
            ).communicate()
            # Create a local ignore file
            fh = open(os.path.join(repo_dir, ".git/info/exclude"), "w")
            fh.write(".git\n.hg\n.svn\n.epio-git\n")
            if os.path.isfile(".epioignore"):
                fh2 = open(".epioignore")
                fh.write(fh2.read())
                fh2.close()
            fh.close()
            # Remove any gitignore file
            subprocess.Popen(
                ["rm", "-f", ".gitignore"],
                env=env,
                stdout=subprocess.PIPE,
                cwd=repo_dir,
            ).communicate()
            # Set configuration options
            fh = open(os.path.join(repo_dir, ".git/config"), "w")
            fh.write("[core]\nautocrlf = false\n")
            fh.close()
            # Add files into git
            subprocess.Popen(
                ["git", "add", "."],
                env=env,
                stdout=subprocess.PIPE,
                cwd=repo_dir,
            ).communicate()
            # Commit them all
            subprocess.Popen(
                ["git", "commit", "-a", "-m", "Auto-commit."],
                env=env,
                stdout=subprocess.PIPE,
                cwd=repo_dir,
            ).communicate()
            # Push it
            subprocess.call(
                ["git", "push", "vcs@%s:%s" % (
                    os.environ.get('EPIO_HOST', 'upload.ep.io').split(":")[0],
                    app,
                ), "master"],
                env=env,
                cwd=repo_dir,
            )
        finally:
            # Remove the repo
            subprocess.call(["rm", "-rf", repo_dir])


