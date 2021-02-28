#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 15:03:06 2021

@author: EduardoWork
"""

import datetime
import requests
from bs4 import BeautifulSoup as bs

from scrape_sc_cov import extract_cov_data
from scrape_sc_cov import get_elements_from_news_page
from scrape_sc_cov import save_info
from parse_sc_cov import parse_info


def check_new():
    """Verifica se o database está atualizado.

    Returns
    -------
    new_elements (list): lista com os links dos novos dados
    """
    parsed = parse_info('covid_sc_casos.csv')  # list of dicts, in Pandas DataFrame
    last_date = parsed.max()  # date in datetime, in Pandas DataFrame

    updated = False
    new_elements = []
    i = 0

    while not updated:

        # element: link com dados a serem extraídos
        elements = get_elements_from_news_page(
            'https://www.sc.gov.br/noticias/temas/coronavirus?start=' +
            str(i) + str(0)
        )

        for element in elements:

            # Pegar data
            site = requests.get('https://www.sc.gov.br' + element,
                                headers={'User-Agent': 'Custom'})
            soup = bs(site.content, features="lxml")
            # Data em str
            current_date_str = soup.time['datetime']
            # Data em datetime
            current_date = datetime.datetime.strptime(
                current_date_str.split('T')[0], '%Y-%m-%d'
            )
            # Se é mais novo, adicionar. Caso contrário, updated = True
            if (current_date > last_date).bool():
                new_elements.append(element)
            else:
                updated = True

        i += 1

    return new_elements


def update():
    """Verifica se o database está atualizado. Se não estiver, atualiza."""
    new = check_new()
    if len(new) == 0:
        print('Database is already updated')
    else:
        for element in new:
            casos, mortes = extract_cov_data(element)
            save_info(casos, mortes)
        print('Datebase was updated')


if __name__ == '__main__':
    update()
