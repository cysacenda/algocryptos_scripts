import requests
import logging
from config.config import Config

class CoinMarketCap:
    conf = None
    URL_PRICE_LIST = None

    def __init__(self):
        self.conf = Config()

        # API urls
        self.URL_PRICE_LIST = self.conf.get_config('cmc_params', 'url_prices')

    # region Get prices

    def get_price_list(self, format=False):
        response = self.query_coinmarketcap(self.URL_PRICE_LIST, False)
        if format:
            return list(response.keys())
        else:
            return response

    # endregion

    # region Utils

    def query_coinmarketcap(self, url,errorCheck=True):
        try:
            response = requests.get(url).json()
        except Exception as e:
            logging.error("Error getting prices information from CMC. " + str(e))
            return None
        if errorCheck and 'Response' in response.keys():
            logging.error("[ERROR] " + response['Message'])
            return None
        return response

    def format_parameter(self, parameter):
        if isinstance(parameter, list):
            return ','.join(parameter)
        else:
            return parameter

    # endregion
