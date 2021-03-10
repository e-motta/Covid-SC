#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 15:11:43 2021

@author: EduardoWork
"""
import csv
import re
import unicodedata
from datetime import datetime

import pandas as pd


def parse_info(nome_do_arquivo):
    """Extrai do arquivo csv: data, cidade e número (de casos ou mortes).

    Notes
    -----
    Arquivo .csv no formato: 'data, dados'
        data (str): ex.: '2021-02-15T17:30:10-03:00'
        dados (str): 'Abdon Batista - 187Abelardo Luz - 817Agrolândia...'

    Parameters
    ----------
    nome_do_arquivo : str
        Nome do arquivo csv com os dados.

    Returns #FIXME
    -------
    Pandas DataFrame
        Formato: [{'data': datetime, 'dados':{cid:núm,...}},{...},...]
        data (datetime): YYYY-MM-DD
        cidade (str): nome da cidade sem acentos
        número (int): número de casos ou mortes

    """
    with open(nome_do_arquivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        final_data = []  # [{'data':datetime, 'dados':{cid:núm,...}},{...},...]

        for row in csv_reader:

            # Passa linhas sem dados
            try:
                assert len(row[1])
            except:
                continue

            cid_num_dict = {}  # {cidade:número}
            date_cidnum_dict = {}  # {'data': datetime, 'dados':{cidade:número}}

            # Adiciona data em formato datetime
            date_cidnum_dict['date'] = datetime.fromisoformat(row[0])

            # Extrai cidades, sem acento
            output = unicodedata.normalize('NFD', row[1]).encode('ascii', 'ignore')
            cidades = re.findall(r"[a-zA-Z'\- ]{3,}", str(output))
            # Limpa caracteres supérfluos ao final
            cidades_clean = [cidade[:-3] for cidade in cidades]

            # Extrai números
            numeros = re.findall(r'\d+', row[1])

            # Verifica se as últimas cidades possuem números correpondentes
            # (Em alguns casos o último item está em branco)
            # Adiciona 0 se não tiver
            if len(cidades_clean) > len(numeros):
                for i in range(len(cidades_clean) - len(numeros)):
                    numeros.append(0)

            # Adiciona cidades e números a dicionário
            for cidade, num in zip(cidades_clean, numeros):
                cid_num_dict[cidade] = int(num)

            # Adiciona dicionário a outro dicionário que contem a data
            date_cidnum_dict['dados'] = cid_num_dict

            # Adiciona dicionário a lista
            final_data.append(date_cidnum_dict)

    # Adiciona o TOTAL por data
    for i in final_data:
        i['dados']['TOTAL'] = sum((i['dados'].values()))

    # Retorna um DataFrame com a lista
    return pd.DataFrame(final_data)


def unpack(df, column):
    """Unpacks a dictionary from within a Pandas DataFrame.

    Parameters
    ----------
    df (Pandas Dataframe): [{key1:value1, key2: {nested_key:nested_value}},...]
    column (str): name of column with nested dictionary (key2)

    Returns
    -------
    Pandas DataFrame: [{key1:value1, nested_key:nested_value},...] #FIXME
    """
    ret = pd.concat(
        [df, pd.DataFrame(
            (d for idx, d in df[column].iteritems())
            )], axis=1)
    del ret[column]

    ret_sorted = ret.sort_values('date')

    return ret_sorted
