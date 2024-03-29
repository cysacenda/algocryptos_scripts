from ratelimit import rate_limited
from commons.config import Config
from commons.utils import utils
import logging
import time
import pandas.io.sql as psql
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
import pandas.io.sql as psql
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from pytrends.request import TrendReq
from random import randint

@rate_limited(5, 1)
def get_info_google_trend(pytrends, df_to_db, standard, coin_row, pytrend_period):

    #Lower case everything
    coin_id = coin_row['id_cryptocompare']  # Exemple : 7605
    project = coin_row['coin_name'].lower()  # Exemple : ethereum
    symbol = coin_row['symbol'].lower()  # Exemple : eth

    logging.warning("__get_info_google_trend start for coin " + project)

    # Compare symbol and project name
    # wait a random amount of time to avoid bot detection
    time.sleep(randint(3, 8))
    #pytrends.build_payload([project, symbol], cat=0, timeframe='today 1-m', geo='', gprop='')

    # Modif CSA pour ML
    pytrends.build_payload([project, symbol], cat=0, timeframe=pytrend_period, geo='', gprop='')

    # Keep the most significant
    df_extract_trend = pytrends.interest_over_time()
    max_project = df_extract_trend[project].max()
    max_symbol = df_extract_trend[symbol].max()

    significant = ''

    # If the two results are at 100, take the oldest
    if max_project == max_symbol:
        date_project = df_extract_trend[project].idxmax()
        date_symbol = df_extract_trend[symbol].idxmax()
        significant = project if date_project > date_symbol else symbol
    else:
        significant = project if max_project > max_symbol else symbol

    # Result for stand alone
    df_result_coin = df_extract_trend[[significant]]
    df_result_coin.columns = ['value_standalone']

    # Result vs Standard
    # wait a random amount of time to avoid bot detection
    time.sleep(randint(8, 13))
    pytrends.build_payload([significant, standard], cat=0, timeframe=pytrend_period, geo='', gprop='')
    df_google_trend_compared = pytrends.interest_over_time()
    df_google_trend_compared = df_google_trend_compared[[significant]]
    df_google_trend_compared.columns = ['value_compared_to_standard']

    df_result_coin = df_result_coin.join(df_google_trend_compared)
    df_result_coin['id_cryptocompare'] = coin_id

    df_result_coin.reset_index(inplace=True)
    df_result_coin.rename(columns={'date': 'timestamp'}, inplace=True)

    # append aggregated result coin to one specific dataframe
    if df_to_db is None:
        df_to_db = df_result_coin
    else:
        # df_to_db = df_to_db.append(df_result_coin, ignore_index=True)
        df_to_db = pd.concat([df_to_db, df_result_coin])

    logging.warning("__get_info_google_trend end  for coin " + project)
    return df_to_db

