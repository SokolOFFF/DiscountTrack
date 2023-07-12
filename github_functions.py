from git import Repo

PATH_OF_GIT_REPO = r'.git'
COMMIT_MESSAGE = 'database changed'


def git_push_data():
    """
    Function pushes 'data.db' and 'login_config.yaml' files to the GitHub repo for further using in streamlit site.
    :return:
    """
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add("data.db", "login_config.yaml", update=True)
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print('Some error occurred while pushing the code')
        print(e)
