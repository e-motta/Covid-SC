#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 17:15:42 2021

@author: EduardoWork
"""

import csv
import requests
from bs4 import BeautifulSoup as bs


def get_elements_from_news_page(link):
    """Salva os links de acesso às notícias com os dados.

    1) Acessa o link com módulo requests, cria um objeto com módulo soup;
    2) Encontra os títulos que contenham 'Coronavírus em SC' e 'casos',
       extrai o link da notícia;
    3) Com o link da notícia, executa a função extract_cov_data. #FIXME

    Parameters
    ----------
    link (str): link do site de notícia do Gov de SC ref. Covid

    Returns
    -------
    results (list): *** #FIXME
    """
    site = requests.get(link, headers={'User-Agent': 'Custom'})

    soup = bs(site.content, features="lxml")

    results = []

    for a_tag in soup.find_all('a'):
        if ('Coronavírus em SC:' in a_tag.get_text() and
            'casos' in a_tag.get_text()):
            # append to results
            results.append(a_tag.get('href'))

    return results


def extract_cov_data(link):
    """Extrai números de casos confirmados + mortes.

    Parameters
    ----------
    link (str): link da notícia com o boletim de casos

    Returns
    -------
    casos_confirmados (list of int)
    mortes (list of int)
    """
    article = requests.get('http://www.sc.gov.br'+link,
                           headers={'User-Agent': 'Custom'})
   # print('###test### http://www.sc.gov.br'+link)

    article_soup = bs(article.content, features="lxml")

    casos_confirmados = []  # Lista para números de casos confirmados
    mortes = []  # Lista para números de mortes

    # Adiciona a data antes do restante dos dados
    date = article_soup.time['datetime']
    casos_confirmados.append(date)
    mortes.append(date)

    # Variável que garante que a página era a correta.
    # Será True quando as informações forem extraídas
    pag_correta = False

    # Encontraar 'casos confirmados' + 'óbitos'
    for h2_tag in article_soup.find_all('h2'):  # loop de todas as tags h2

        # Casos confirmados
        if 'casos confirmados' in h2_tag.get_text():
            try:

                # Se 'Florianópolis' está na próxima tag,
                # trata-se da tag com os casos
                if 'Florianópolis' in h2_tag.nextSibling.get_text():
                    casos_confirmados.append(h2_tag.nextSibling.get_text())
                    pag_correta = True

                # Se 'Florianópolis' está na segunda tag após,
                # trata-se da tag com os casos
                elif 'Florianópolis' in h2_tag.nextSibling.nextSibling.get_text():
                    casos_confirmados.append(
                        h2_tag.nextSibling.nextSibling.get_text()
                        )
                    pag_correta = True
            # Se as tags após forem '\n'
            except AttributeError:
                try:
                    casos_confirmados.append(
                        h2_tag.nextSibling.nextSibling.get_text()
                        )
                    pag_correta = True
                # Se a página não tem números de casos
                except AttributeError:
                    break

        # Mortes
        if 'óbito' in h2_tag.get_text():
            try:
                if 'Florianópolis' in h2_tag.nextSibling.get_text():
                    mortes.append(
                        h2_tag.nextSibling.get_text()
                        )
                    pag_correta = True
                elif 'Florianópolis' in h2_tag.nextSibling.nextSibling.get_text():
                    mortes.append(
                        h2_tag.nextSibling.nextSibling.get_text()
                        )
                    pag_correta = True
            except AttributeError:
                try:
                    mortes.append(
                        h2_tag.nextSibling.nextSibling.get_text()
                        )
                    pag_correta = True
                except AttributeError:
                    break

    if pag_correta:
        return casos_confirmados, mortes


def save_info(casos, mortes):
    """Salva as informações extraídas em csv.

    Em arquivos separados para casos e mortes.
    Modo 'append'.

    Parameters
    ----------
    casos (list): with 1 str element ???
    mortes (list): with 1 str element ???

    Returns
    -------
    None
    """
    with open('covid_sc_casos.csv', 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(casos)

    with open('covid_sc_mortes.csv', 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(mortes)
