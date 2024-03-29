from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc, \
    precision_recall_curve, average_precision_score
from sklearn.metrics import confusion_matrix
from sklearn.utils.fixes import signature
import pandas as pd
import numpy as np
from scipy import stats
import pickle

from sklearn.metrics import classification_report

pd.options.mode.chained_assignment = None  # default='warn'

def show_nan_count_per_column(df):
    null_columns = df.columns[df.isnull().any()]
    return df[null_columns].isnull().sum()


def get_value_count(y_):
    y_ = pd.Series(y_)
    true_count = 1  # to avoid divide by 0 - approx
    false_count = 0

    count = y_.value_counts()
    if True in count:
        true_count = count[True]
    if False in count:
        false_count = count[False]
    return true_count, false_count


def evaluate_model(model, pX_test, py_test, threshold, do_feat_importances, target=1):
    predicted_proba = model.predict_proba(pX_test)
    probs = predicted_proba[:, target]  # 0 or 1
    predicted = (probs >= threshold)

    confusion = confusion_matrix(py_test, predicted)
    precision = precision_score(py_test, predicted)
    recall = recall_score(py_test, predicted)
    f1 = f1_score(py_test, predicted)

    feat_importances = pd.Series([0, 0, 0])
    if do_feat_importances:
        feat_importances = pd.Series(model.feature_importances_).nlargest(3)

    support_True, support_False = get_value_count(py_test)

    return confusion, precision, recall, f1, support_True, support_False, feat_importances


def evaluate_model_formated(model, pX_test, py_test, threshold, do_feat_importances, target=1):
    confusion, precision, recall, f1, support_True, support_False, feat_importances = evaluate_model(model, pX_test,
                                                                                                     py_test, threshold,
                                                                                                     do_feat_importances,
                                                                                                     target)
    return confusion[0][0], confusion[0][1], confusion[1][0], confusion[1][
        1], precision, recall, f1, support_True, support_False, feat_importances.values[0], \
           feat_importances.values[1], feat_importances.values[2]


def show_model_accuracy(algo_name, model, pX_test, py_test, pX_columns, do_roc_curve=False,
                        do_precision_recall_curve=False, do_features_importance=False,
                        do_precision_recall_vs_treshold=False, threshold=0.5, nb_features_imp=20):
    from matplotlib import pyplot as plt
    predicted_proba = model.predict_proba(pX_test)
    # keep probabilities for the positive outcome only
    probs = predicted_proba[:, 1]
    predicted = (probs >= threshold)  # .astype('int')
    confusion = confusion_matrix(py_test, predicted)

    # Infos
    print('----------------------------------------------------------')
    print('Results for algorithm : ' + algo_name)
    print('----------------------------------------------------------\n')
    print('Confusion Matrix :\n', confusion)
    print('[[TN, FP]')
    print('[FN, TP]]')
    print('Accuracy: {:.2f}'.format(accuracy_score(py_test, predicted)))
    # print('Precision: {:.2f}'.format(precision_score(py_test, predicted)))
    # print('Recall: {:.2f}'.format(recall_score(py_test, predicted)))
    # print('F1: {:.2f}'.format(f1_score(py_test, predicted)))
    # print('AUC: {:.2f}'.format(roc_auc))
    # print('----------------------------------------------------------\n')
    print('\n\nOther Metrics :\n')
    print(classification_report(py_test, predicted, target_names=['False', 'True']))
    print('----------------------------------------------------------\n')

    # Plot ROC curve
    if do_roc_curve:
        # predicted = model.predict(pX_test)
        # fpr, tpr, thresholds = roc_curve(py_test, predicted)
        fpr, tpr, thresholds = roc_curve(py_test, probs)
        roc_auc = auc(fpr, tpr)
        plt.title('Receiver Operating Characteristic (ROC Curve)')
        plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
        plt.legend(loc='lower right')
        plt.plot([0, 1], [0, 1], 'r--')
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.ylabel('True Positive Rate / Sensitivity')
        plt.xlabel('False Positive Rate / 1 - Specificity')
        plt.legend(loc="lower right")
        plt.show()

    # Plot Precision / Recall curve
    if do_precision_recall_curve:
        # predict class values
        yhat = model.predict(pX_test)
        # calculate precision-recall curve
        precision, recall, thresholds = precision_recall_curve(py_test, probs)
        # calculate F1 score
        f1 = f1_score(py_test, yhat)
        # calculate precision-recall AUC
        auc_value = auc(recall, precision)
        # calculate average precision score
        ap = average_precision_score(py_test, probs)
        print('f1=%.3f auc=%.3f ap=%.3f' % (f1, auc_value, ap))
        # plot no skill
        plt.plot([0, 1], [0.5, 0.5], label='Treshold 0.5', linestyle='--')
        label = 'Treshold ' + str(threshold)
        plt.plot([0, 1], [threshold, threshold], label=label, linestyle='--')
        # plot the roc curve for the model
        # plt.plot(recall, precision, marker='.')
        plt.step(recall, precision, color='b', alpha=0.2,
                 where='post')
        # In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
        step_kwargs = ({'step': 'post'}
                       if 'step' in signature(plt.fill_between).parameters
                       else {})
        plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)
        plt.title('Precision-Recall curve')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.legend(loc="lower right")
        # show the plot
        plt.show()

    if do_precision_recall_vs_treshold:
        precisions, recalls, thresholds = precision_recall_curve(py_test, probs)
        plt.plot(thresholds, precisions[:-1], "b--", label="Precision")
        plt.plot(thresholds, recalls[:-1], "g-", label="Recall")
        plt.xlabel("Threshold")
        plt.legend(loc="upper left")
        plt.ylim([0, 1])
        plt.show()

    # View a list of the features and their importance scores
    if do_features_importance:
        feat_importances = pd.Series(model.feature_importances_, index=pX_columns)
        if nb_features_imp > 20:
            plt.figure(figsize=(20, 20))
        feat_importances.nlargest(nb_features_imp).plot(kind='barh')
        plt.show()


def show_model_accuracy_new_way(model, X_, y_test_value, X_close_price, threshold, show_graphs=True):
    predicted_proba = model.predict_proba(X_.values)
    probs = predicted_proba[:, 1]
    df_probs = pd.DataFrame(probs)
    df_probs.index = X_.index
    df_probs.columns = ['prob']
    df_probs['sup_treshold'] = (df_probs['prob'] >= threshold)
    df_probs = df_probs[df_probs['sup_treshold']]
    df_probs['close_price'] = X_close_price
    df_probs['close_price_+term'] = y_test_value  # y_test['y_+1d_value']
    df_probs['pct_change_value'] = ((df_probs['close_price_+term'] - df_probs['close_price']) / df_probs[
        'close_price']) * 100

    if show_graphs:
        from matplotlib import pyplot as plt
        import seaborn as sns
        plt.figure(figsize=(6, 6))
        sns.distplot(df_probs.pct_change_value)
        print('pct_change_value: ' + str(df_probs.pct_change_value.mean()))
    return df_probs.pct_change_value.mean()


# https://ocefpaf.github.io/python4oceanographers/blog/2015/03/16/outlier_detection/
def remove_outliers(df, columns_name):
    for column_name in columns_name:
        # print('shape before outliers : ' + str(df.shape))

        # 1 / remove extreme values than can make outliers removing with zscore method KO
        quantile = df[column_name].quantile(0.95)
        df = df[df[column_name] < quantile * 20]

        # print('shape after outliers #1 (quantile) : ' + str(df.shape))

        # 2 / remove outliers with zscore (/!\ done on all columns...)
        df = df[(np.abs(stats.zscore(df)) < 6).all(axis=1)]

        # print('shape after outliers #2 (zscore) : ' + str(df.shape))

        # 3 / remove outliers with rolling_median
        if column_name != 'volume_aggregated_1h': # TODO : Moche !
            threshold_sup = 1.5  # 1.5 times higher than median
            threshold_inf = 1 / 1.5  # 1.5 times lower than median
            df['rm'] = df[column_name].rolling(window=10, center=True).median().fillna(method='bfill').fillna(
                method='ffill')
            df['divided'] = np.abs(df[column_name] / df['rm'])
            df = df[df.divided < threshold_sup]
            df = df[df.divided > threshold_inf]

            # print('shape after outliers #3 (rolling_median) : ' + str(df.shape))

            df.drop(columns=['rm', 'divided'], inplace=True)
    return df


def get_last_dates_per_trading_pair(df):
    return df.index[-1][0].to_pydatetime()


def get_useless_features(model, index, threshold=0.002):
    s = pd.Series(model.feature_importances_, index=index)
    return s[s <= threshold].index.values


# Serialization
def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def remove_id_index(X_close):
    X_close = X_close.copy().reset_index()
    X_close = X_close.drop(['id_cryptocompare'], axis=1)
    X_close = X_close.set_index('timestamp')
    return X_close


def format_both_close_prices(X_train, X_test, id_cryptocompare):
    return format_close_prices(X_train, id_cryptocompare), format_close_prices(X_test, id_cryptocompare)


def format_close_prices(X_, id_cryptocompare):
    X_ = pd.DataFrame(X_)
    X_ = remove_id_index(X_.query('id_cryptocompare == "' + id_cryptocompare + '"'))
    return X_.close_price


def calcul_signals_for_crypto(model, df_crypto):
    predicted_proba = model.predict_proba(df_crypto.values)
    probs = predicted_proba[:, 1]
    df_probs = pd.DataFrame(probs)
    df_probs.index = df_crypto.index
    df_probs.columns = ['signal_prob']
    return df_probs