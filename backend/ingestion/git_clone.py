import tempfile

from git import Repo

def clone_repo(git_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(git_url, temp_dir)
    return temp_dir