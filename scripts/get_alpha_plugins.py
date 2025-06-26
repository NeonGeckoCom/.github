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

import requests

from sys import argv
from subprocess import check_output, DEVNULL, CalledProcessError


def get_pip_versions(pkg: str) -> (str, str):
    stable_out = check_output(["pip", "index", "versions", pkg],
                              stderr=DEVNULL).decode()
    alpha_out = check_output(["pip", "index", "versions", "--pre", pkg],
                             stderr=DEVNULL).decode()
    stable = stable_out.split('(', 1)[1].split(')', 1)[0]
    alpha = alpha_out.split('(', 1)[1].split(')', 1)[0]
    return alpha, stable


def get_plugin_repos(org: str, kind: str, token: str):
    url = f"https://api.github.com/users/{org}/repos"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    repos = response.json()
    while response.links.get('next'):
        response = requests.get(response.links['next']['url'], headers=headers)
        repos = repos + response.json()
    return [repo["name"] for repo in repos if f"{kind}-" in repo["name"]
            and not repo["archived"]]


if __name__ == "__main__":
    org = argv[1]
    substr = argv[2]  # "skill" or "plugin"
    token = argv[3]
    repositories = get_plugin_repos(org, substr, token)
    # print(len(repositories))
    no_pypi = []
    has_alpha = []
    up_to_date = []
    for repository in repositories:
        try:
            pypi_name = f"neon-{repository}" if substr == "skill" else repository
            alpha, stable = get_pip_versions(pypi_name)
            if alpha == stable:
                up_to_date.append(repository)
            else:
                has_alpha.append(repository)
        except CalledProcessError:
            no_pypi.append(repository)
    print(f"Alpha: {has_alpha}")
    print(f"Stable: {up_to_date}")
    print(f"Error: {no_pypi}")
