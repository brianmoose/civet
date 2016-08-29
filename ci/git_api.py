import abc

class GitException(Exception):
  pass

class GitAPI(object):
  __metaclass__ = abc.ABCMeta
  _api_url = None
  _github_url = None
  PENDING = 0
  ERROR = 1
  SUCCESS = 2
  FAILURE = 3
  RUNNING = 4
  CANCELED = 5

  @abc.abstractmethod
  def sign_in_url(self):
    """
    Gets the URL to allow the user to sign in.
    Return:
      str: URL
    """

  @abc.abstractmethod
  def git_url(self, owner, repo):
    """
    Git path to the repository. Ex, git@github.com/idaholab/civet
    Input:
      owner: str: Owner of the repository
      repo: str: Name of the repository
    """

  @abc.abstractmethod
  def repo_url(self, owner, repo):
    """
    Gets the repository UR.
    Input:
      owner: str: owner of the repository
      repo: str: name of the repository
    Return:
      str: URL to the repository
    """

  @abc.abstractmethod
  def get_all_repos(self, auth_session, owner):
    """
    Get a list of repositories the user has access to
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user with a token
      owner: str: user to check against
    Return:
      list of str: Each entry is "<owner>/<repo name>"
    """

  @abc.abstractmethod
  def get_repos(self, auth_session, session):
    """
    Get a list of repositories that the signed in user has access to.
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      session: HttpRequest.session: session of the request
    Return:
      list of str: Each entry is "<owner>/<repo name>"
    """

  @abc.abstractmethod
  def get_branches(self, auth_session, owner, repo):
    """
    Get a list of branches for a repository
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      owner: str: owner of the repository
      repo: str: name of the repository
    Return:
      list of str: Each entry is the name of a branch
    """

  @abc.abstractmethod
  def update_pr_status(self, oauth_session, base, head, state, event_url, description, context):
    """
    Update the PR status.
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      base: models.Commit: Original commit
      head: models.Commit: New commit
      state: int: One of the states defined as class variables above
      event_url: str: URL back to the moosebuild page
      description: str: Description of the update
      context: str: Context for the update
    """

  @abc.abstractmethod
  def is_collaborator(self, oauth_session, user, repo):
    """
    Check to see if the signed in user is a collaborator on a repo
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      user: models.GitUser: User to check against
      repo: models.Repository: Repository to check against
    Return:
      bool: True if user is a collaborator on repo, False otherwise
    """

  @abc.abstractmethod
  def pr_job_status_comment(self, oauth_session, url, msg):
    """
    Leave a comment on a PR to indicate the status of a job
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      url: str: URL to post the message to
      msg: str: Comment
    """

  @abc.abstractmethod
  def pr_review_comment(self, oauth_session, url, sha, filepath, position, msg):
    """
    Leave a review comment on a PR for a specific hash, on a specific position of a file
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      url: str: URL to post the message to
      sha: str: SHA of the PR branch to attach the message to
      filepath: str: Filepath of the file to attach the message to
      position: str: Position in the diff to attach the message to
      msg: str: Comment
    """

  @abc.abstractmethod
  def pr_comment(self, oauth_session, url, msg):
    """
    Leave a comment on a PR
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user
      url: str: URL to post the message to
      msg: str: Comment
    """

  @abc.abstractmethod
  def last_sha(self, oauth_session, owner, repo, branch):
    """
    Get the latest SHA for a branch
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user making the requests
      owner: str: owner of the repository
      repo: str: name of the repository
      branch: str: name of the branch
    Return:
      str: Last SHA of the branch or None if there was a problem
    """

  @abc.abstractmethod
  def install_webhooks(self, request, auth_session, user, repo):
    """
    Updates the webhook for this server on GitHub.
    Input:
      auth_session: requests_oauthlib.OAuth2Session for the user updating the web hooks.
      user: models.GitUser of the user trying to update the web hooks.
      repo: models.Repository of the repository to set the web hook on.
    Raises:
      GitException if there are any errors.
    """

  @abc.abstractmethod
  def pr_html_url(self, owner, repo, pr_num):
    """
    Gets a URL to the pull request.
    Input:
      owner: str: Owner of the repo
      repo: str: Name of the repo
      pr_num: int: Pull request number
    Return:
      str: URL on the gitserver to the PR
    """

  @abc.abstractmethod
  def repo_html_url(self, owner, repo):
    """
    Gets a URL to the repository
    Input:
      owner: str: Owner of the repo
      repo: str: Name of the repo
    Return:
      str: URL on the gitserver to the repo
    """

  @abc.abstractmethod
  def branch_html_url(self, owner, repo, branch):
    """
    Gets a URL to the branch
    Input:
      owner: str: Owner of the repo
      repo: str: Name of the repo
      branch: str: Name of the branch
    Return:
      str: URL on the gitserver to the branch
    """

  @abc.abstractmethod
  def commit_html_url(self, owner, repo, sha):
    """
    Gets a URL to a commit
    Input:
      owner: str: Owner of the repo
      repo: str: Name of the repo
      sha: str: SHA of on the repo
    Return:
      str: URL on the gitserver to the commit
    """
