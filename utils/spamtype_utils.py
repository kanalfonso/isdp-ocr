"""Utilities for preprocessing SMS text data, sampling class imbalance, and evaluating models."""
# pylint score - 9.59

# Standard libraries
import re
from typing import Tuple

# Third-party libraries
import numpy as np
import pandas as pd
from tqdm import tqdm
import calamancy
from cleantext import remove_emoji
from googletrans import Translator
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as nltk_stopwords
from stopwordsiso import stopwords as iso_stopwords
from imblearn.over_sampling import BorderlineSMOTE
from sklearn.utils import resample
import sklearn.metrics as skmetrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt

# Configure tqdm after imports
tqdm.pandas()




def show_confusion_matrix(eval_df: pd.DataFrame,
                          actual_col_name: str,
                          predicted_col_name: str,
                          wk_col_name: str,
                          display_labels: dict | list,
                          normalize: str | None = None):

    """Display and evaluate confusion matrices from model predictions."""

    if normalize:
        title_suffix = "Normalized Confusion Matrix"
        values_format = ".2f"
    else:
        title_suffix = "Raw Confusion Matrix"
        values_format = "d"

    if wk_col_name in eval_df.columns:
        for wk in eval_df[wk_col_name].unique():

            df = eval_df[eval_df[wk_col_name] == wk]

            conf_matrix = skmetrics.confusion_matrix(
                df[actual_col_name],
                df[predicted_col_name],
                normalize=normalize
            )

            disp = skmetrics.ConfusionMatrixDisplay(
                confusion_matrix=conf_matrix,
                display_labels=display_labels
            )

            # Calculate metrics
            acc = accuracy_score(df[actual_col_name], df[predicted_col_name])
            prec = precision_score(df[actual_col_name], df[predicted_col_name], average='macro')
            rec = recall_score(df[actual_col_name], df[predicted_col_name], average='macro')
            f1 = f1_score(df[actual_col_name], df[predicted_col_name], average='macro')

            # Print all
            print(f"Accuracy     : {acc:.4f}")
            print(f"Precision    : {prec:.4f}")
            print(f"Recall       : {rec:.4f}")
            print(f"F1 Score     : {f1:.4f}")


            disp.plot(xticks_rotation='vertical', values_format=values_format)
            plt.title(f'{wk} -{title_suffix}')
            plt.grid(False)

    else:

        conf_matrix = skmetrics.confusion_matrix(
            eval_df[actual_col_name],
            eval_df[predicted_col_name],
            normalize=normalize
        )

        disp = skmetrics.ConfusionMatrixDisplay(
            confusion_matrix=conf_matrix,
            display_labels=display_labels
        )

        # Calculate metrics
        acc = accuracy_score(eval_df[actual_col_name],
                             eval_df[predicted_col_name])

        prec = precision_score(eval_df[actual_col_name],
                               eval_df[predicted_col_name],
                               average='macro')

        rec = recall_score(eval_df[actual_col_name],
                           eval_df[predicted_col_name],
                           average='macro')

        f1 = f1_score(eval_df[actual_col_name],
                      eval_df[predicted_col_name],
                      average='macro')

        # Print all
        print(f"Accuracy     : {acc:.4f}")
        print(f"Precision    : {prec:.4f}")
        print(f"Recall       : {rec:.4f}")
        print(f"F1 Score     : {f1:.4f}")


        disp.plot(xticks_rotation='vertical', values_format=values_format)
        plt.title(f'{title_suffix}')
        plt.grid(False)



class CustomSampler(BorderlineSMOTE):
    """Custom resampling strategy that combines undersampling of the majority class
    with Borderline-SMOTE oversampling of the minority class."""

    def __init__(self, random_state=None):
        """Initialize custom sampler"""
        super().__init__()
        self.random_state = random_state

    def fit_resample(self, X: np.ndarray,
                     y: pd.Series,
                     *_args,
                     **_kwargs) -> Tuple[np.ndarray, pd.Series]:

        """Resample the dataset according to the custom strategy."""
        X = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X
        y = pd.Series(y) if not isinstance(y, pd.Series) else y

        class_counts = y.value_counts().sort_values(ascending=False)
        majority_class = class_counts.index[0]
        second_highest_count = class_counts.iloc[1]
        minority_class = class_counts.index[-1]
        second_lowest_count = class_counts.iloc[-2]

        # Downsample majority to second highest count
        downsample_target = int(second_highest_count)
        x_majority = X[y == majority_class]
        y_majority = y[y == majority_class]
        x_majority_down, y_majority_down = resample(
            x_majority, y_majority,
            replace=False,
            n_samples=downsample_target,
            random_state=self.random_state
        )

        # Combine with other classes (not yet oversampled)
        x_rest = X[y != majority_class]
        y_rest = y[y != majority_class]
        x_temp = pd.concat([x_majority_down, x_rest], axis=0)
        y_temp = pd.concat([y_majority_down, y_rest], axis=0)

        # Upsample minority to 125% of second-lowest count
        smote_target = int(second_lowest_count * 1.25)
        smote = BorderlineSMOTE(
            sampling_strategy={minority_class: smote_target},
            random_state=self.random_state
        )
        x_final, y_final = smote.fit_resample(x_temp, y_temp)

        return x_final, y_final



class TextPreprocessor:
    """Text preprocessing pipeline for cleaning, normalizing, and preparing text data
    for downstream NLP tasks such as embeddings or classification."""

    _fil_nlp_model = calamancy.load("tl_calamancy_md-0.2.0")
    en_stopwords = set(nltk_stopwords.words('english'))
    fil_stopwords = set(iso_stopwords("tl"))
    stopwords = en_stopwords.union(fil_stopwords)

    def __init__(self, df: pd.DataFrame, *, raw_text_col_name: str = 'CONTENT') -> None:
        """Initialize text preprocessor"""
        self.df = df
        self.raw_text_col_name = raw_text_col_name


    def display_dataframe(self) -> pd.DataFrame:
        """Displays current dataframe without applying any transformations"""
        return self.df

    @staticmethod
    def is_cjk(text: str) -> int:
        """"Checks whether text contains a CJK character
            Returns 1 if yes, else 0"""

        cjk_ranges = [
            (4352, 4607), (11904, 42191), (43072, 43135),
            (44032, 55215), (63744, 64255), (65072, 65103),
            (65381, 65500), (131072, 196607)
        ]
        return int(any(
            any(start <= ord(char) <= end for start, end in cjk_ranges)
            for char in str(text)
        ))


    @staticmethod
    def translate_to_en(text):
        """Translates text to english"""
        translator = Translator()
        result = translator.translate(text, dest='en')
        return result.text


    def translate_if_needed(self, row):
        """Translates text to english if it contains CJK characters"""
        text = row[self.raw_text_col_name]

        # If text is None or NaN, just return it as-is
        if pd.isna(text) or str(text).strip() == '':
            return text

        if row['HAS_CJK'] == 1:
            try:
                return TextPreprocessor.translate_to_en(text)
            except Exception as e:
                print(f"Translation error on text: {text}\nError: {e}")
                return text  # fallback: just return original
        else:
            return text


    @staticmethod
    def text_cleaning(text):
        """Removes \n, emojis, symbols, digits, excess spaces"""
        # remove \n
        text = text.replace("\n", " ")
        text = re.sub(r'\n{2,}', ' ', text)

        # remove emojis
        text = remove_emoji(text)

        # remove symbols and digits
        text = re.sub(r'[^A-Za-z\s]', ' ', text)

        # # remove single letter characters
        # text = re.sub(r'\b[a-zA-Z]\b', '', text)

        # remove excess spaces (last step)
        text = re.sub(r'\s{2,}', ' ', text)

        return text.lower().strip()


    @staticmethod
    def remove_stopwords(token_list: list) -> list:
        """Filters out stopwords from token list"""
        return [token for token in token_list if token.lower() not in TextPreprocessor.stopwords]


    @staticmethod
    def remove_short_tokens(token_list: list) -> list:
        """Removes tokens with length <= 2 from token list"""
        return [token for token in token_list if not len(token) <= 2]


    @staticmethod
    def lemmatize_en_tokens(token_list: list) -> list:
        """Returns the lemmatized word of each token"""
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token) for token in token_list]

    @staticmethod
    def lemmatize_fil_tokens(text: str) -> list:
        """Returns lemmatized filipino words if applicable"""
        doc = TextPreprocessor._fil_nlp_model(text)
        return [token.lemma_ for token in doc]



    def clean_raw_text(self) -> pd.DataFrame:
        """Pipeline to clean the raw text before generating embeddings"""

        print(f"Setting {self.raw_text_col_name} col to str dtype...\n")
        self.df[self.raw_text_col_name] = self.df[self.raw_text_col_name].astype(str)

        print("Generating HAS_CJK column...")
        self.df['HAS_CJK'] = self.df[self.raw_text_col_name].progress_apply(self.is_cjk)


        print("\nGenerating TRANSLATED_TEXT column...")
        self.df['TRANSLATED_TEXT'] = self.df.progress_apply(self.translate_if_needed, axis=1)


        print("\nGenerating CLEANED_TEXT column...")
        self.df['CLEANED_TEXT'] = self.df['TRANSLATED_TEXT'].progress_apply(self.text_cleaning)


        print("\nGenerating TOKENS column...")
        self.df['TOKENS'] = self.df['CLEANED_TEXT'].progress_apply(word_tokenize)


        print("\nGenerating TOKENS_NO_STOPWORDS column...")
        self.df['TOKENS_NO_STOPWORDS'] = self.df['TOKENS'].progress_apply(self.remove_stopwords)


        print("\nGenerating TOKENS_NO_STOPWORDS_NO_SHORT column...")
        self.df['TOKENS_NO_STOPWORDS_NO_SHORT'] = self.df['TOKENS_NO_STOPWORDS']\
                                                .progress_apply(self.remove_short_tokens)


        print("\nGenerating TOKENS_EN_LEMMATIZED column...")
        self.df['TOKENS_EN_LEMMATIZED'] = self.df['TOKENS_NO_STOPWORDS_NO_SHORT']\
                                            .progress_apply(self.lemmatize_en_tokens)


        print("\nGenerating TEXT_EN_LEMMATIZED column...")
        self.df['TEXT_EN_LEMMATIZED'] = self.df['TOKENS_EN_LEMMATIZED']\
                                        .progress_apply(' '.join)


        print("\nGenerating TOKENS_FIL_LEMMATIZED column...")
        self.df['TOKENS_FIL_LEMMATIZED'] = self.df['TEXT_EN_LEMMATIZED']\
                                            .progress_apply(self.lemmatize_fil_tokens)


        print("\nGenerating TEXT_FINAL column...")
        self.df['TEXT_FINAL'] = self.df['TOKENS_FIL_LEMMATIZED']\
                                    .progress_apply(' '.join)

        print("\nFilling NaNs of TEXT_FINAL column...")

        self.df['TEXT_FINAL'] = self.df['TEXT_FINAL']\
                                    .replace(r'^\s*$', np.nan, regex=True)\
                                    .fillna(self.df[self.raw_text_col_name])

        return self.df



if __name__ == '__main__':
    START_DATE = '2024-05-13'
    END_DATE = '2025-05-12'

    # Convert to datetime
    start = pd.to_datetime(START_DATE)
    end = pd.to_datetime(END_DATE)

    # Generate list with 7-day intervals
    sample_date_list = []
    current_date = start
    while current_date <= end:
        sample_date_list.append(current_date)
        current_date += pd.Timedelta(days=7)

    # Convert to string format
    date_list_str = [date.strftime('%Y-%m-%d') for date in sample_date_list]


    def read_and_concat_dfs(date_list: list = date_list_str) -> pd.DataFrame:
        """Reading all SMS dfs and concatenating them"""

        dfs = [pd.read_csv(f'sms_data/{date}.csv') for date in date_list]

        len_dfs = [len(df) for df in dfs]

        concat_df = pd.concat(dfs, axis=0).reset_index(drop=True)

        assert sum(len_dfs) == len(concat_df)
        return concat_df


    raw_sms_df = read_and_concat_dfs(date_list_str).rename(columns={'Content':'CONTENT'}).head(500)

    print(raw_sms_df)

    pipeline = TextPreprocessor(raw_sms_df)

    print("===== POST-PROCESSING =====")
    print(pipeline.clean_raw_text())
