import numpy as np
import pandas as pd

from ml.preproc_load import PreprocLoad
from ml.utils_ml import remove_outliers
from ml.preproc_feature_engineering import PreprocFeatureEngineering
from ml.utils_ml import load_obj

from commons.config import Config

pd.options.mode.chained_assignment = None  # default='warn'


# Prepare data from raw data
class PreprocPrepare:

    @staticmethod
    def get_columns_to_be_cleaned():
        return ['close_price', 'open_price', 'low_price', 'high_price', 'volume_aggregated_1h']

    @staticmethod
    def do_timestamp_tasks(df_ts):
        df_ts = df_ts[~df_ts.timestamp.duplicated(keep='first')]
        df_ts['timestamp'] = pd.to_datetime(df_ts.timestamp, utc=True)
        return df_ts.set_index('timestamp')

    # TODO : To be coded to avoir loosing info from december 2017 !
    @staticmethod
    def add_ohlcv_missing_infos(connection, df_ohlcv_p, id_cryptocompare, str_older_date):
        # TODO V2 : Perf : do only one call to these two lines (cf. get_ohlcv_1h_plus_missing_infos)
        df_ohlcv_old_1d = PreprocLoad.get_dataset_ohlcv_old(connection, id_cryptocompare, df_ohlcv_p.index.min(), str_older_date)

        # resample to 1h
        # df_ohlcv_1h = df_ohlcv_p.resample("1H").agg({'open_price': 'first', 'high_price': 'max', 'low_price': 'min',
        #                                             'close_price': 'last', 'volume_aggregated_1h': 'sum'})

        df_final = df_ohlcv_p

        # # Only when datafarme contains rows
        # if len(df_ohlcv_old_1d.index) > 0:
        #     df_ohlcv_old_1d = PreprocPrepare.clean_dataset_ohlcv_std(df_ohlcv_old_1d, PreprocPrepare.get_columns_to_be_cleaned(),
        #                                                        resample='1D')
        #
        #     # resample to 1h
        #     df_ohlcv_old_1h = df_ohlcv_old_1d.resample("1H").agg({'open_price': 'first', 'high_price': 'max', 'low_price': 'min',
        #                                                     'close_price': 'last', 'volume_aggregated_1h': 'sum'}).interpolate()
        #
        #     # quick & dirty way to have coherents volumes between both dataset
        #     mean_vol_old = df_ohlcv_old.tail(5).volume_aggregated_1h.mean()
        #     mean_vol_1d = df_ohlcv_1d.head(5).volume_aggregated_1h.mean()
        #     df_ohlcv_old.volume_aggregated_1h = df_ohlcv_old.volume_aggregated_1h / (mean_vol_old / mean_vol_1d)
        #     df_final = pd.concat([df_ohlcv_old, df_ohlcv_1d])
        #
        #     df_final = df_final[~df_final.index.duplicated()]
        #
        # # TODO : Check that !
        # # trick to allow to have data for indicators on last rows
        # df_last_row = df_ohlcv_p.tail(1).copy()
        # df_last_row.index = [pd.to_datetime(df_final.tail(1).index.values[0] + np.timedelta64(1, 'D'), utc=True)]
        #
        # # extrapolate 24h vol from mean of last 6 hours
        # df_last_row.volume_aggregated_1h = df_ohlcv_p.tail(6).volume_aggregated_1h.mean() * 4
        #
        # df_final = df_final.append(df_last_row)
        return df_final

    @staticmethod
    def get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv_p, id_cryptocompare, str_older_date):
        # get data older than 12/2017
        df_ohlcv_old = PreprocLoad.get_dataset_ohlcv_old(connection, id_cryptocompare, df_ohlcv_p.index.min(), str_older_date)

        df_final = df_ohlcv_p

        # Only when datafarme contains rows
        if len(df_ohlcv_old.index) > 0:
            df_ohlcv_old = PreprocPrepare.clean_dataset_ohlcv_std(df_ohlcv_old, PreprocPrepare.get_columns_to_be_cleaned(), resample='1D')

            # resample to 1h
            df_ohlcv_old = df_ohlcv_old.resample("1H").interpolate()
            df_ohlcv_old.volume_aggregated_1h = df_ohlcv_old.volume_aggregated_1h / 24

            # quick & dirty way to have coherents volumes between both dataset
            mean_vol_old = df_ohlcv_old.tail(5).volume_aggregated_1h.mean()
            mean_vol_ohlcv = df_ohlcv_p.head(5).volume_aggregated_1h.mean()
            df_ohlcv_old.volume_aggregated_1h = df_ohlcv_old.volume_aggregated_1h / (mean_vol_old / mean_vol_ohlcv)
            df_final = pd.concat([df_ohlcv_old, df_ohlcv_p])

        df_final = df_final[~df_final.index.duplicated()]
        return df_final

    @staticmethod
    def merge_google_trend_data(df_google_trend_crypto_1m_p, df_google_trend_crypto_5y_p):
        # put data on the same scale
        first_row_1m = df_google_trend_crypto_1m_p.head(1)
        equiv_row_5y = df_google_trend_crypto_5y_p.loc[first_row_1m.index.values[0]]

        ratio_standalone = first_row_1m.value_standalone[0] / equiv_row_5y.value_standalone
        ratio_compared_to_standard = first_row_1m.value_compared_to_standard[0] / equiv_row_5y.value_compared_to_standard

        df_google_trend_crypto_1m_p.value_standalone = df_google_trend_crypto_1m_p.value_standalone / ratio_standalone
        df_google_trend_crypto_1m_p.value_compared_to_standard = df_google_trend_crypto_1m_p.value_compared_to_standard / ratio_compared_to_standard

        # replace data from 5y with more precise data from 1m
        start_remove = df_google_trend_crypto_1m_p.head(1).index.values[0]
        end_remove = df_google_trend_crypto_1m_p.tail(1).index.values[0]

        df_google_trend_crypto_5y_p = df_google_trend_crypto_5y_p.loc[
            (df_google_trend_crypto_5y_p.index.values < start_remove) | (
                        df_google_trend_crypto_5y_p.index.values > end_remove)]
        df_google_trend_crypto_5y_p = pd.concat([df_google_trend_crypto_5y_p, df_google_trend_crypto_1m_p])

        return df_google_trend_crypto_5y_p

    @staticmethod
    def clean_dataset_google_trend(df_google_trend_p):
        df_google_trend_p = PreprocPrepare.do_timestamp_tasks(df_google_trend_p)
        df_google_trend_p = df_google_trend_p.resample('1H').interpolate()
        df_google_trend_p['value_standalone'] = df_google_trend_p['value_standalone'].astype(int)
        df_google_trend_p['value_compared_to_standard'] = df_google_trend_p['value_compared_to_standard'].astype(int)

        # avoid infinity values (bias not big)
        df_google_trend_p.value_standalone = df_google_trend_p.value_standalone.replace(0, 1)
        df_google_trend_p.value_compared_to_standard = df_google_trend_p.value_compared_to_standard.replace(0, 1)
        return df_google_trend_p

    @staticmethod
    def clean_dataset_ohlcv_spe(df_ohlcv_p):
        # drop rows with missing values (OHLCV)
        df_ohlcv_p = df_ohlcv_p.loc[
            (df_ohlcv_p.open_price != 0.0) & (df_ohlcv_p.high_price != 0.0) & (df_ohlcv_p.low_price != 0.0) & (
                        df_ohlcv_p.close_price != 0.0) & (df_ohlcv_p.volume_aggregated_1h != 0.0)]
        return PreprocPrepare.clean_dataset_ohlcv_std(df_ohlcv_p, PreprocPrepare.get_columns_to_be_cleaned())

    @staticmethod
    def clean_dataset_ohlcv_std(df_ohlcv_p, columns_name, do_ts_tasks=True, resample='1H'):
        # perform different tasks on df
        if do_ts_tasks:
            df_ohlcv_p = PreprocPrepare.do_timestamp_tasks(df_ohlcv_p)
        df_ohlcv_p = remove_outliers(df_ohlcv_p, columns_name)

        # no scale change (regarding calls done in code)
        df_ohlcv_p = df_ohlcv_p.resample(resample).interpolate()
        return df_ohlcv_p

    @staticmethod
    # str_older_date_to_retrieve : default (learning), everything is retrieved. Perf improvement for inference
    def get_global_dataset_for_crypto(connection, id_cryptocompare_crypto, older_date=None):
        # ------------------ PRE-PROCESSING : Retrieve data and prepare ------------------ #
        id_cryptocompare_crypto = str(id_cryptocompare_crypto)

        conf = Config()
        id_cryptocompare_tether = str(conf.get_config('cryptocompare_params', 'id_cryptocompare_tether'))
        id_cryptocompare_bitcoin = str(conf.get_config('cryptocompare_params', 'id_cryptocompare_bitcoin'))

        if older_date is None:
            older_date = str(conf.get_config('data_params', 'older_date_to_retrieve'))

        # --------------------------------
        # OHLCV
        # --------------------------------
        df_ohlcv = PreprocLoad.get_dataset_ohlcv(connection, id_cryptocompare_crypto, older_date)
        df_ohlcv = PreprocPrepare.clean_dataset_ohlcv_spe(df_ohlcv)
        min_date = df_ohlcv.index.min()

        df_ohlcv = PreprocPrepare.get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv, id_cryptocompare_crypto, older_date)

        df_ohlcv_tether = PreprocLoad.get_dataset_ohlcv(connection, id_cryptocompare_tether, older_date)
        df_ohlcv_tether = PreprocPrepare.clean_dataset_ohlcv_spe(df_ohlcv_tether)
        df_ohlcv_tether = PreprocPrepare.get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv_tether, id_cryptocompare_tether, older_date)

        df_ohlcv_bitcoin = PreprocLoad.get_dataset_ohlcv(connection, id_cryptocompare_bitcoin, older_date)
        df_ohlcv_bitcoin = PreprocPrepare.clean_dataset_ohlcv_spe(df_ohlcv_bitcoin)
        df_ohlcv_bitcoin = PreprocPrepare.get_ohlcv_1h_plus_missing_infos(connection, df_ohlcv_bitcoin, id_cryptocompare_bitcoin, older_date)

        #df_ohlcv = PreprocPrepare.add_ohlcv_missing_infos(connection, df_ohlcv, id_cryptocompare_crypto, older_date)

        # --------------------------------
        # REDDIT SUBSCRIBERS
        # --------------------------------
        df_reddit = PreprocLoad.get_dataset_reddit(connection, id_cryptocompare_crypto, older_date)
        df_reddit = df_reddit[df_reddit.reddit_subscribers.notnull()]
        df_reddit = PreprocPrepare.do_timestamp_tasks(df_reddit)
        df_reddit = df_reddit.resample('1H').interpolate()
        df_reddit['reddit_subscribers'] = df_reddit['reddit_subscribers'].astype(int)

        # --------------------------------
        # ALL CRYPTOS
        # --------------------------------
        df_all_cryptos = PreprocLoad.get_dataset_all_cryptos(connection, older_date)
        df_all_cryptos = PreprocPrepare.clean_dataset_ohlcv_std(df_all_cryptos,
                                                 columns_name=['global_volume_usd_1h', 'global_market_cap_usd'])

        # --------------------------------
        # GOOGLE TREND
        # --------------------------------
        # crypto - last month => Need to import and keep old data
        df_google_trend_crypto_1m = PreprocLoad.get_dataset_google_trend(connection, id_cryptocompare_crypto, '_1m', older_date)
        df_google_trend_crypto_1m = PreprocPrepare.clean_dataset_google_trend(df_google_trend_crypto_1m)

        # crypto - 5 years
        df_google_trend_crypto_5y = PreprocLoad.get_dataset_google_trend(connection, id_cryptocompare_crypto, '', older_date)
        df_google_trend_crypto_5y = PreprocPrepare.clean_dataset_google_trend(df_google_trend_crypto_5y)

        # bitcoin - last month
        df_google_trend_bitcoin_1m = PreprocLoad.get_dataset_google_trend(connection, id_cryptocompare_bitcoin, '_1m', older_date)
        df_google_trend_bitcoin_1m = PreprocPrepare.clean_dataset_google_trend(df_google_trend_bitcoin_1m)

        # bitcoin - 5 years
        df_google_trend_bitcoin_5y = PreprocLoad.get_dataset_google_trend(connection, id_cryptocompare_bitcoin, '', older_date)
        df_google_trend_bitcoin_5y = PreprocPrepare.clean_dataset_google_trend(df_google_trend_bitcoin_5y)

        # merge data
        df_google_trend_crypto_5y = PreprocPrepare.merge_google_trend_data(df_google_trend_crypto_1m, df_google_trend_crypto_5y)
        df_google_trend_bitcoin_5y = PreprocPrepare.merge_google_trend_data(df_google_trend_bitcoin_1m, df_google_trend_bitcoin_5y)

        # ------------------ PRE-PROCESSING : Feature engineering ------------------ #
        df_reddit = PreprocFeatureEngineering.feature_engineering_reddit(df_reddit)
        df_ohlcv_fe = PreprocFeatureEngineering.feature_engineering_ohlcv(df_ohlcv)
        df_ohlcv_tether_fe = PreprocFeatureEngineering.feature_engineering_ohlcv(df_ohlcv_tether)
        df_ohlcv_bitcoin_fe = PreprocFeatureEngineering.feature_engineering_ohlcv(df_ohlcv_bitcoin)
        df_technical_analysis = PreprocFeatureEngineering.feature_engineering_technical_analysis(df_ohlcv)
        df_all_cryptos = PreprocFeatureEngineering.feature_engineering_ohlcv_all_cryptos(df_all_cryptos)
        df_google_trend_crypto_5y = PreprocFeatureEngineering.feature_engineering_google_trend(df_google_trend_crypto_5y, 'y')
        df_google_trend_bitcoin_5y = PreprocFeatureEngineering.feature_engineering_google_trend(df_google_trend_bitcoin_5y, 'y')

        # Join dfs
        df_ohlcv_fe = df_ohlcv_fe.join(df_ohlcv_tether_fe, rsuffix='_tether')
        df_ohlcv_fe = df_ohlcv_fe.join(df_ohlcv_bitcoin_fe, rsuffix='_bitcoin')
        df_global = df_ohlcv_fe.join(df_technical_analysis)
        df_global = df_global.join(df_reddit)
        df_global = df_global.join(df_all_cryptos)
        df_global = df_global.join(df_google_trend_crypto_5y, rsuffix='_crypto_5y')
        df_global = df_global.join(df_google_trend_bitcoin_5y, rsuffix='_bitcoin_5y')
        df_global.resample('1H').interpolate()
        df_global.reddit_subscribers = df_global.reddit_subscribers.interpolate(method='linear', limit_area='outside')

        # remove data added only to be able to calcul indicators, etc. => we don't want to take it into account
        df_global = df_global[min_date:df_global.index.max()]

        # remove 24 first hours (some things can't be extrapolated well)
        df_global = df_global.iloc[24:]
        df_global = df_global.interpolate(method='nearest', axis=0).ffill()

        # drop na if exist
        df_final = df_global.dropna(axis='rows')
        diff = df_global.shape[0] - df_final.shape[0]
        if diff > 0:
            print(str(diff) + ' rows containing Nan dropped')

        # index with id_crypto + date
        df_final['id_cryptocompare'] = id_cryptocompare_crypto
        df_final.reset_index(drop=False, inplace=True)
        df_final.set_index(['timestamp', 'id_cryptocompare'], inplace=True)

        return df_final

    @staticmethod
    def get_preprocessed_data_inference(df_one_crypto, do_scale=True, do_pca=True, useless_features=None):
        if useless_features is None:
            useless_features = []

        old_indexes = df_one_crypto.index
        X_close_prices = df_one_crypto.close_price

        # delete useless columns if needed
        if len(useless_features) > 0:
            df_one_crypto = df_one_crypto.drop(useless_features, axis=1)

        df_one_crypto = df_one_crypto.values

        # Scaling Data - reuse scaler from learning
        if do_scale:
            scaler = load_obj('scaler_learning')
            df_one_crypto = scaler.transform(df_one_crypto)

        # PCA to reduce dimensionality - reuse pca from learning
        if do_pca:
            pca = load_obj('pca_learning')
            df_one_crypto = pca.transform(df_one_crypto)

        # re-index
        df_one_crypto = pd.DataFrame(df_one_crypto)
        df_one_crypto.index = old_indexes

        return df_one_crypto, X_close_prices
