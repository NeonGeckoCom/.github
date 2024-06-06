# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from sys import argv

import requests

from pprint import pprint


def add_label(repo: str, label: str, description: str, color: str, token: str):
    url = f"https://api.github.com/repos/{repo}/labels"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": label, "color": color, "description": description}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Created label {label} in repository {repo}")
    else:
        print(f"Failed to create label {label} in repository {repo}: {response.json().get('errors')}")


def get_all_repos(org: str, token: str):
    url = f"https://api.github.com/users/{org}/repos"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    repos = response.json()
    while response.links.get('next'):
        response = requests.get(response.links['next']['url'], headers=headers)
        repos = repos + response.json()
    return [repo["name"] for repo in repos]


if __name__ == "__main__":
    org = argv[1]
    token = argv[2]
    label_name = argv[3]
    label_description = argv[4]
    label_color = argv[5]
    repositories = get_all_repos(org, token)
    # print(len(repositories))
    for repository in repositories:
        add_label(f"{org}/{repository}", label_name, label_description, label_color, token)
