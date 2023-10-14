import datetime
import time
from typing import Tuple, Union
from urllib.parse import urlparse

import requests
from github import Github, Repository

from config import GITHUB_API_TOKEN

md_probs = {
    "real": "{0}/master/README.md",
    "main": "{0}/main/README.md",
    "real_min": "{0}/master/readme.md",
    "main_min": "{0}/main/readme.md",
}

inner_md_props = {
    "inner": "{0}/README.md",
    "inner_min": "{0}/readme.md"
}

base_url = "https://raw.githubusercontent.com/"


github = Github(GITHUB_API_TOKEN)


def get_changed_url(repo_name) -> str:
    """
    Get the changed url of a repository
    :param repo_name: The name of the repository
    :return: The changed url of the repository
    """
    url = requests.get(f"https://github.com/{repo_name}").url
    url = url.replace("https://github.com/", "")
    return url


def get_repo(repo_name) -> Union[Repository.Repository, None]:
    """
    Get the repository
    :param repo_name: The name of the repository
    :return: The repository
    """
    try:
        try:
            return github.get_repo(repo_name)
        except Exception:
            new_url = get_changed_url(repo_name)
            return github.get_repo(new_url)
    except Exception:
        return None


def get_inner_readme(repo_name) -> Union[str, None]:
    """
    Get the inner readme file of a repository
    :param repo_name: The name of the repository
    :return: The inner readme file of the repository
    """
    try:
        dir_list = repo_name.split("/")
        del dir_list[2]
        del dir_list[2]
        repo = get_repo("/".join(dir_list[: 2]))
        if repo is None:
            return None

        contents = repo.get_contents("/".join(dir_list[2:]))
        if type(contents) == list:
            readme = [c for c in contents if c.name.lower() == "readme.md"]
            readme = next(iter(readme)) if readme else None
        else:
            readme = contents if contents.name.lower() == "readme.md" else None
        return readme
    except Exception:
        return None


def is_inner_readme(repo_name) -> bool:
    """
    Check if the repository has an inner readme file
    :param repo_name: The name of the repository
    :return: True if the repository has an inner readme file, False otherwise
    """
    return len(repo_name.split("/")) > 2


def get_inner_readme_dir(repo_name) -> str:
    """
    Get the directory of the readme file of a repository
    :param repo_name: The name of the repository
    :return: The directory of the readme file
    """
    dir_list = repo_name.split("/")
    dir_list.pop(2)
    return "/".join(dir_list)


def get_potential_urls(repo_name) -> list[str]:
    """
    Get the potential urls of the readme file of a repository
    :param repo_name: The name of the repository
    :return: The potential urls of the readme file
    """
    if is_inner_readme(repo_name):
        return [value.format(get_inner_readme_dir(repo_name)) for _, value in inner_md_props.items()]
    return [value.format(repo_name) for _, value in md_probs.items()]


def get_readme_with_github_api(repo_name) -> Tuple[Union[str, None], Union[str, None]]:
    """
    Get the readme file of a repository using the github api
    :param repo_name: The name of the repository
    :return: The readme file content of the repository and path of raw url
    """
    readme = None
    readme_path = None
    try:
        readme = get_repo(repo_name).get_readme()
    except Exception:
        if is_inner_readme(repo_name):
            readme = get_inner_readme(repo_name)
    if readme:
        readme_path = urlparse(readme.download_url).path
        readme = readme.decoded_content.decode("utf-8")

    return readme, readme_path


def get_readme_with_raw_url(repo_name) -> Tuple[Union[str, None], Union[str, None]]:
    """
    Get the readme file of a repository using the raw url
    :param repo_name: The name of the repository
    :return: The readme file content of the repository and path of raw url
    """

    readme = None
    readme_path = None
    urls = get_potential_urls(repo_name)
    for url in urls:
        url = f"{base_url}{url}"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                readme = response.content.strip().decode("utf-8")
            except UnicodeDecodeError as e:
                readme = response.content.strip().decode("unicode_escape", errors="ignore")
            readme_path = urlparse(url).path
            break
    return readme, readme_path


def get_rate_limit_and_wait_time() -> Tuple[int, int]:
    # sourcery skip: aware-datetime-for-utc
    """
    Get rate limit and wait time
    """
    rate_limit = github.get_rate_limit().core
    return rate_limit.remaining, (rate_limit.reset - datetime.datetime.utcnow()).seconds + 1


def get_readme(repo_name) -> Tuple[Union[str, None], Union[str, None]]:
    """
    Get the readme file of a repository, first try with raw url, if not found, try with github api
    :param repo_name: The name of the repository
    :return: The readme file content of the repository and path of raw url
    """
    readme, readme_path = get_readme_with_raw_url(repo_name)
    if readme is None:
        readme, readme_path = get_readme_with_github_api(repo_name)
    return readme, readme_path


def get_starcount(repo_name) -> int:
    """
    Get the star count of a repository
    :param repo_name: The name of the repository
    :return: The star count of the repository
    """
    repo = get_repo(repo_name)
    return 0 if repo is None else repo.stargazers_count
