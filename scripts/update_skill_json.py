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

import json
import shutil

from sys import argv
from os.path import join, isfile
from pprint import pprint
from parsesetup import parse_setup
from neon_utils.file_utils import parse_skill_readme_file


def _get_setup_py_data(setup_py: str) -> dict:
    setup_meta = parse_setup(setup_py, trusted=True)
    pprint(setup_meta)
    skill_id = list(setup_meta['entry_points'].values())[0].split('=')[0]
    return {"skill_id": skill_id,
            "source": setup_meta.get("url"),
            "package_name": setup_meta['name'],
            "license": setup_meta.get("license"),
            "author": setup_meta.get("author"),
            "description": setup_meta.get("description")}


def build_skill_spec(skill_dir: str) -> dict:
    readme_file = join(skill_dir, "README.md")
    setup_py = join(skill_dir, "setup.py")
    if isfile(setup_py):
        skill_data = _get_setup_py_data(setup_py)
    readme_data = parse_skill_readme_file(readme_file)
    skill_data["description"] = readme_data.get("summary") or skill_data["description"]
    skill_data["name"] = readme_data.get("title")
    skill_data["examples"] = readme_data.get("examples") or []
    skill_data["tags"] = readme_data.get("categories",
                                         []) + readme_data.get("tags", [])
    skill_data["icon"] = readme_data.get("icon")
    return skill_data


def write_skill_json(skill_dir: str, default_lang="en-us"):

    old_skill_json = join(skill_dir, "skill.json")
    setup_py = join(skill_dir, "setup.py")
    pkg_dir = list(parse_setup(setup_py,
                               trusted=True)['package_dir'].values())[0]
    skill_json = join(skill_dir, pkg_dir, "locale", default_lang, "skill.json")
    print(f"skill_dir={skill_dir}|skill.json={skill_json}")

    if isfile(old_skill_json):
        shutil.move(old_skill_json, skill_json)

    skill_spec = build_skill_spec(skill_dir)
    pprint(skill_spec)
    try:
        with open(skill_json) as f:
            current = json.load(f)
    except Exception as e:
        print(e)
        current = None
    if current:
        skill_spec["extra_plugins"] = current.get("extra_plugins") or dict()
    if current != skill_spec:
        print("Skill Updated. Writing skill.json")
        with open(skill_json, 'w+') as f:
            json.dump(skill_spec, f, indent=4)
    else:
        print("No changes to skill.json")


if __name__ == "__main__":
    write_skill_json(argv[1])
