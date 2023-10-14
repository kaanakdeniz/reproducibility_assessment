import html
import os
import re
import sys
from functools import cache, lru_cache

import pandas as pd

repo_file_maps = {
    "neurips": pd.read_csv('./data/paperswithcode/readme/repo_file_map.csv'),
    "acl": pd.read_csv('./data/acl/readme/repo_file_map.csv')
}

html_dirs = {
    "neurips": './data/paperswithcode/readme/html',
    "acl": './data/acl/readme/html'
}


def write_text_to_file(text, target_dir, filename):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    open(target_dir + filename,
         "w", encoding="utf-8").write(text)


def to_valid_file_name(file_name):
    return re.sub(r'[/\\?%*:|\"<>\x7F\x00-\x1F]', '', file_name)


def read_all_csv_files(dir):
    dataframes = {}
    for file in os.listdir(dir):
        if file.endswith(".csv"):
            df = pd.read_csv(dir + file)
            dataframes[file.replace(".csv", "")] = df
    return dataframes


# @lru_cache(maxsize=400)
def get_readme_with_repo_name(map, repo):
    repo_file_map = repo_file_maps[map]
    html_dir = html_dirs[map]

    files = repo_file_map[repo_file_map["repo"]
                          == repo]["filename"].values.tolist()
    if len(files) == 0:
        return None
    file = files[0]
    readme_path = os.path.join(html_dir, f"{file}.html")
    return open(readme_path, 'r', encoding="utf-8", errors="ignore").read()
