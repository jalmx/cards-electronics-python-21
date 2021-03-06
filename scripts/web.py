# -*- coding: utf-8 -*-
import os
import shutil
import unicodedata
from pathlib import Path

import nbformat as nbf
from bs4 import BeautifulSoup
from nbconvert.exporters import HTMLExporter
from traitlets.config import Config

from change_name import change_name

def convert_nb_html(path_name_file: str, name_file: str):
    """ Convert files notebooks in html"""
    c = Config()

    c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
    c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)

    path_save = '../web'
    # regresa una lista en la posicion 0 viene el html
    result = HTMLExporter(Config=c).from_file(path_name_file)

    with open(f'{path_save}/{name_file.lower()}.html', mode='w',
            encoding='utf-8') as html:
        html.write(result[0])


def generate_files_html(path_file: [str], name_file: [str], ignore: [str] =[]):
    """Logic to iterate all notebooks to html"""
    for count in range(len(path_file)):
        if name_file[count] not in ignore:
            convert_nb_html(path_file[count], name_file[count])


def build_index(html: BeautifulSoup):
    """build de file index.html and save in location"""
    html = html.prettify()

    path = "../web/index.html"
    with open(path, mode='w', encoding='utf-8') as index:
        index.write(html)


def copy_imgs():
    """copy all imgs from src to folder web/img"""
    img_paths = []
    img_regex_list = ['png', 'jpeg', 'jpg', 'svg',"webp",'hex']

    for regex in img_regex_list:
        for img_path in Path("../book").rglob(f'**/*.{regex}'):
            img_paths.append(str(os.path.abspath(img_path)))

    for src in img_paths:
        path = os.path.abspath('../web/imgs')
        dist = f'{path}/{src.split("/")[-1]}'
        shutil.copyfile(src, dist)


def build_cap(title: str, name_items: [str], url_base: str,
            html: BeautifulSoup) -> BeautifulSoup:
    """Build all html for each cap with the list"""
    title = build_tag('h1', title)
    list_ul = build_tag('ul', '')
    for item in name_items:
        list_item = build_tag('li', '')
        subtitle = build_tag('h2', f'{item.replace(".html","").replace("_", " ").lower()} ->')
        link = build_tag('a', f'{subtitle.h2}',
                        href=f"{url_base}/{item}", target="_black")
        list_item.li.append(link.a)
        list_ul.ul.append(list_item.li)

    html.body.append(title.h1)
    html.body.append(list_ul.ul)


def build_tag(tag: str, content: str, **kwargs) -> BeautifulSoup:
    """build any tag html"""
    new_tag = BeautifulSoup(f'<{tag}>{content}</{tag}>', 'html.parser')

    for attr in kwargs:
        new_tag.contents[0][attr] = kwargs[attr]

    return new_tag


def search_files_nb():
    path_book = '../book'
    ipynb = '.ipynb_checkpoints'
    list_path = {'path_file': [], 'name_file': []}
    # Con la funcion rglob busca todos los archivos con la extension .ipynb
    for element in Path(path_book).rglob('**/*.ipynb'):
        # se brinca todos los archivos que estan carpertas "checkpoints"
        if not str(element).find(ipynb) > 0:
            path_name_file = os.path.abspath(element)
            name_file_split = str(element).split('/')[-1].split('.')[:-1]
            # junto a lista para definir el nombre del archivo html
            name_file = ''.join(name_file_split)
            name_file = unicodedata.normalize("NFKD", name_file).encode(
                "ascii", "ignore").decode("ascii")  # limpio de acentos
            list_path['path_file'].append(path_name_file)
            list_path['name_file'].append(name_file)

    return list_path


def change_path_img_in_html():
    for path_file_html in get_list_html().get("full_path"):  # get path from html
        with open(path_file_html) as html:
            html = BeautifulSoup(html, 'html.parser')
            for img in html.body.find_all('img'):
                name = img.get('src').split("/")[-1]
                html.find('img', src=img.get('src'))['src'] = f"./imgs/{name}"

            with open(path_file_html, mode='w', encoding='utf-8') as file_html_new:
                file_html_new.write(html.prettify())


def get_list_html() -> dict:
    """Read all files in folder, then generate a list with it

    Returns:
        dict: [List of files html in folder]
    """
    path = '../web'
    list_paths = {"name": [], "full_path": []}
    for file in Path(path).rglob('*.html'):
        list_paths["name"].append(str(file).split("/")[-1])
        list_paths["full_path"].append(os.path.abspath(file))

    return list_paths


def generate_list_cap(list_files: []) -> dict:
    list_complet = {}

    for file_html in list_files:
        init = file_html.split("_")[0]
        number = 0
        if init.isnumeric():
            number = int(init)
            number = int(str(number)[0])

        if list_complet.get(number) is None:
            list_complet[number] = [file_html]
        else:
            list_complet.get(number).append(file_html)

    for key in list_complet:
        list_complet[key] = sorted(list_complet.get(key))
        #list_complet.get(key).sort()

    return list_complet


def build_body_html(html: BeautifulSoup) -> BeautifulSoup:
    """Logic to generate body for html index

    Args:
        html (BeautifulSoup): all content html

    Returns:
        BeautifulSoup: all new content html
    """
    # traer el listado de htmls
    list_html = get_list_html().get("name")
    # separar y generar un array por capitulo
    all_caps = generate_list_cap(list_html)

    # crear la logica para crear el cap html html
    url_base = '.'
    for i in range(len(all_caps)):
        cap = i
        if i == 0: cap = "Extra"

        build_cap(f'Capítulo {cap}', all_caps.get(i), url_base, html)
    # regresar todo el html

    return html


def get_html_template() -> BeautifulSoup:
    # path_web = '../web'
    path_template_html = './template.html'

    template_html = open(path_template_html)
    html_raw = template_html.read()
    template_html.close()
    return BeautifulSoup(html_raw, 'html.parser')

def clean_directory_html():
    path="../web"
    for file in Path(path).rglob("*.html"):
        os.remove(os.path.abspath(file))

if __name__ == "__main__":
    files_name_ignore= ["Notas","Template","Test","test","template"]
    print("Fix names files ipynb")
    change_name()
    print("cleaning directory")
    clean_directory_html()
    print("Searching files...")
    files = search_files_nb()
    print("Conveting to html...")
    generate_files_html(files['path_file'], files['name_file'],files_name_ignore)
    print("copying imgs")
    copy_imgs()
    print("Generate index.html")
    html = get_html_template()
    html = build_body_html(html)
    build_index(html)
    print("Fix tag img")
    change_path_img_in_html()
    print("Done... xD")

#create a function than copy assets
