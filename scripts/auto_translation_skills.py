# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
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

import os
import shutil
from os.path import join, exists, dirname
from pathlib import Path
import re
from ovos_utils.bracket_expansion import expand_template
from ovos_translate_plugin_deepl import DeepLTranslator

"""
Usage:

export TARGET_LANG=uk-ua
export SKILL_DIRECTORY=/home/$USER/skill-directory
python3 translate.py
"""

API_KEY = os.getenv("DEEPL_API_KEY")
if not API_KEY:
    raise ValueError("API Key is not specified")

tx = DeepLTranslator({"api_key": API_KEY})

single_lang = os.getenv("TARGET_LANG")
target_langs = (single_lang,) if single_lang else (
    "de-de", "ca-es", "cs-cz", "da-dk", "es-es", "fr-fr", "hu-hu",
    "it-it", "nl-nl", "pl-pl", "pt-pt", "ru-ru", "sv-fi", "sv-se",
    "uk-ua"
)

base_folder = os.getenv("SKILL_DIRECTORY")
print(f"Translating files in: {base_folder}")
res_folder = join(base_folder, "locale")

old_voc_folder = join(base_folder, "vocab")
old_dialog_folder = join(base_folder, "dialog")
old_res_folder = [old_voc_folder, old_dialog_folder]

src_lang = "en-us"
src_files = {}
ext = [".voc", ".dialog", ".intent", ".entity", ".rx", ".value", ".word"]
untranslated = [".rx", ".value", ".entity"]

def check_and_create_folder(folder):
    """Check and create a folder if it does not exist"""
    if not exists(folder):
        print(f"Folder does not exist, creating: {folder}")
        os.makedirs(folder, exist_ok=True)

def file_location(f: str, base: str) -> str:
    """Search for a file in a folder"""
    for root, dirs, files in os.walk(base):
        for file in files:
            if f == file:
                return join(root, file)
    return None

def translate(lines: list, target_lang: str) -> list:
    """Translate lines using DeepL"""
    translations = []
    for line in lines:
        replacements = dict()
        for num, var in enumerate(re.findall(r"(?:{{|{)[ a-zA-Z0-9_]*(?:}}|})", line)):
            line = line.replace(var, f'@{num}', 1)
            replacements[f'@{num}'] = var
        try:
            translated = tx.translate(line, target=target_lang, source=src_lang)
        except Exception as e:
            print(f"Error translating line '{line}': {e}")
            continue
        for num, var in replacements.items():
            translated = translated.replace(num, var)
        translations.append(translated)
    return translations

def entities(file: str) -> set:
    """Extract entities from a file"""
    vars = set()
    if not exists(file):
        return vars

    lines = get_lines(file)
    for line in lines:
        for var in re.findall(r"(?:{{|{)[ a-zA-Z0-9_]*(?:}}|})", line):
            vars.add(var)
    return vars

def get_lines(file: str):
    """Read lines from a file"""
    with open(file, "r", encoding="utf-8") as f:
        if file.endswith(".entity"):
            lines = [exp for l in f.read().split("\n") for exp in expand_template(l) if l]
        else:
            lines = [exp for l in f.read().split("\n") for exp in expand_template(l) if l and not l.startswith("#")]
    return lines

def migrate_locale(folder):
    """Move old structure to the new one"""
    for lang in os.listdir(folder):
        path = join(folder, lang)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file_location(file, join(res_folder, lang)) is None:
                    rel_path = root.replace(folder, "").lstrip("/")
                    new_path = join(res_folder, rel_path)
                    os.makedirs(new_path, exist_ok=True)
                    shutil.move(join(root, file), join(new_path, file))
        shutil.rmtree(path)
    shutil.rmtree(folder)

for folder in old_res_folder:
    if not os.path.isdir(folder):
        continue
    migrate_locale(folder)

src_folder = join(res_folder, src_lang)
print(f"Source folder: {src_folder}")
if not exists(src_folder):
    print("Source folder is missing. Check the directory structure.")
else:
    for root, dirs, files in os.walk(src_folder):
        if src_lang not in root:
            continue
        for f in files:
            if any(f.endswith(e) for e in ext):
                file_path = join(root, f)
                rel_path = os.path.relpath(file_path, src_folder)  # correct path adjustment
                src_files[rel_path] = file_path
    print(f"List of source files for translation: {src_files}")

for lang in target_langs:
    print(f"Processing language: {lang}")
    if not tx.get_langcode(lang):
        print(f"Language {lang} is not supported by the translation service.")
        continue

    for rel_path, src in src_files.items():
        filename = Path(rel_path).name
        dst_folder = join(res_folder, lang)
        check_and_create_folder(dst_folder)

        dst = join(dst_folder, rel_path)  # correct path joining

        check_and_create_folder(dirname(dst))  # Create folder for the file

        if entities(src) != entities(dst):
            if exists(dst):
                os.remove(dst)
        elif not exists(dst):
            pass
        else:
            continue

        print(f"Creating translation file for {lang}: {dst}")

        lines = get_lines(src)
        if any(filename.endswith(e) for e in untranslated):
            tx_lines = lines
            is_translated = False
        else:
            tx_lines = translate(lines, lang)
            is_translated = True

        if tx_lines:
            tx_lines = list(set(tx_lines))
            with open(dst, "w", encoding="utf-8") as f:
                if is_translated:
                    f.write(f"# auto translated from {src_lang} to {lang}\n")
                for translated in set(tx_lines):
                    f.write(translated + "\n")
            print(f"Translation file for {lang} successfully created: {dst}")
        else:
            print(f"No translated lines for {filename}")

    print(f"Translation for {lang} completed.")

