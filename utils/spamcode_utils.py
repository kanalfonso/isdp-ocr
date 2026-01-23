"""Helper functions for spam code preprocessing and feature generation."""
# pylint score - 10

# standard
import math
import re
import string
from collections import Counter

# third-party
import emoji
import pandas as pd
import regex
from tqdm import tqdm
from urlextract import URLExtract

# initialize tqdm after import
tqdm.pandas()


class URLCleaner:
    """Utility class for cleaning texts that contains URLs."""
    @staticmethod
    def defragment_url_pieces(text: str) -> str:
        """Remove spaces around ., :, / to reconstruct URLs"""
        return re.sub(r'\s*([.:/])\s*', r'\1', text)

    @staticmethod
    def remove_extracted_urls(text: str, urls: list[str]) -> str:
        """Replace all occurrences of extracted URLs in the text with the placeholder word, url"""
        for url in urls:
            # Escape the URL to safely use it in regex
            pattern = re.escape(url)
            text = re.sub(pattern, 'url', text)
        # Optionally clean up extra spaces
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def clean_str_with_url(text: str) -> str:
        """Returns cleaned string with URLs replaced"""
        # fix url
        str_with_fixed_urls = URLCleaner.defragment_url_pieces(text)

        # extract url
        extractor = URLExtract()
        urls = extractor.find_urls(str_with_fixed_urls)

        # remove url and return string
        return URLCleaner.remove_extracted_urls(str_with_fixed_urls, urls)


class SpamCodeModelFrame:
    """A wrapper class around a pandas DataFrame for feature engineering on spam text data."""
    _feature_funcs = {}

    def __init__(self, df: pd.DataFrame, *, raw_text_col_name: str = 'CONTENT') -> None:
        """Initialize a SpamCodeModelFrame"""
        self.df = df
        self.raw_text_col_name = raw_text_col_name

    @classmethod
    def add_feature(cls, *, feature_name: str):
        """Class method decorator to register a feature extraction function"""
        def wrapper(func):
            cls._feature_funcs[feature_name] = func
            return func
        return wrapper


    def display_dataframe(self) -> pd.DataFrame:
        """Displays current dataframe without applying any transformations"""
        return self.df


    def apply_features(self, features = None) -> pd.DataFrame:
        """Chooses features to apply to the dataframe, and show transformed df"""

        print("Setting CONTENT col to str dtype...\n")
        self.df[self.raw_text_col_name] = self.df[self.raw_text_col_name].astype(str)

        features_to_apply = features or self._feature_funcs.items()

        for index, (name, func) in enumerate(features_to_apply, 1):
            print(f"Generating feature {index}: {name} column")
            self.df[name] = self.df[self.raw_text_col_name].progress_apply(func)
            print("\n")

        if 'CAPITAL_LETTER_COUNT' in self.df.columns and 'WORD_COUNT' in self.df.columns:
            self.df['AVG_CAPS_PER_WORD'] = (
                self.df['CAPITAL_LETTER_COUNT'] / self.df['WORD_COUNT']
            )

        return self.df


# func 1
@SpamCodeModelFrame.add_feature(feature_name='HAS_CJK')
def is_cjk(text):
    """
    Check whether the text contains at least one CJK (Chinese, Japanese, Korean) character.

    Args:
        text (str): Input string.

    Returns:
        int: 1 if the text contains CJK characters, 0 otherwise.
    """
    cjk_ranges = [
        (4352, 4607), (11904, 42191), (43072, 43135),
        (44032, 55215), (63744, 64255), (65072, 65103),
        (65381, 65500), (131072, 196607)
    ]
    return int(any(
        any(start <= ord(char) <= end for start, end in cjk_ranges)
        for char in text
    ))



# func 2
@SpamCodeModelFrame.add_feature(feature_name='LETTER_TO_SYMBOL_RATIO')
def get_alphabetic_ratio(text):
    """Compute the ratio of alphabetic characters to all non-space characters."""
    non_space_chars = [c for c in text if not c.isspace()]
    if not non_space_chars:
        return 0.0

    letter_count = sum(1 for c in non_space_chars if c.isalpha())
    return letter_count / len(non_space_chars)



# func 3
@SpamCodeModelFrame.add_feature(feature_name='SPECIAL_CHAR_RATIO')
def get_special_char_ratio(text):
    """ Compute the ratio of special (punctuation) characters to all non-space characters."""
    if not isinstance(text, str) or not text.strip():
        return 0.0

    special_chars = set(string.punctuation)
    non_space_chars = [char for char in text if not char.isspace()]
    if not non_space_chars:
        return 0.0

    special_count = sum(1 for char in non_space_chars if char in special_chars)
    return special_count / len(non_space_chars)



# func 4
@SpamCodeModelFrame.add_feature(feature_name='MAX_CONSEC_CONSONANTS')
def max_consecutive_consonants(text):
    """Find the maximum length of consecutive consonant sequences in the text."""
    # Regex: match groups of consonants (exclude aeiou, case-insensitive)
    consonant_groups = re.findall(r'(?i)[^aeiou\s\d\W_]+', text)
    if consonant_groups:
        return max(len(group) for group in consonant_groups)
    return 0


# func 5
@SpamCodeModelFrame.add_feature(feature_name='HAS_IMSI_STR')
def contains_imsi_uid_t(text):
    """Detect if text contains an IMSI/UID/T query string pattern."""
    pattern = r'imsi=\d+&uid=[A-Za-z0-9]+&t=\d+'
    return int(bool(re.search(pattern, text)))



# func 6
@SpamCodeModelFrame.add_feature(feature_name='HAS_URL')
def contains_url(text):
    """Detect if text contains at least one URL."""
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    if urls:
        return 1
    return 0


# func 7
@SpamCodeModelFrame.add_feature(feature_name='DIGIT_RATIO')
def get_digit_ratio(text):
    """Compute the ratio of digit characters to total non-space characters."""
    cleaned = text.replace(" ", "")
    total_chars = len(cleaned)
    if total_chars == 0:
        return 0.0

    digit_count = sum(c.isdigit() for c in cleaned)
    return digit_count / total_chars


# func 8
@SpamCodeModelFrame.add_feature(feature_name='CAPITAL_LETTER_TO_WORD_RATIO')
def get_capital_letter_word_ratio(text):
    """Compute the ratio of uppercase letters to total number of words."""
    words = text.split()
    if not words:
        return 0.0
    capital_letters = sum(1 for c in text if c.isupper())
    return capital_letters / len(words)


# func 9
@SpamCodeModelFrame.add_feature(feature_name='CHAR_LENGTH')
def get_char_length(text: str) -> int:
    """Get the total number of characters in the given text."""
    return len(str(text)) if text is not None else 0


# func 10
@SpamCodeModelFrame.add_feature(feature_name='CAPITAL_LETTER_COUNT')
def get_capital_letter_count(text):
    """Count the number of uppercase letters in the text."""
    return sum(1 for c in text if c.isupper())


# func 11
@SpamCodeModelFrame.add_feature(feature_name='WORD_COUNT')
def get_word_count(text):
    """Count the number of words in the text."""
    return len(text.split())



# func 12
@SpamCodeModelFrame.add_feature(feature_name='NON_SPACE_CHAR_LENGTH')
def get_non_space_char_length(text):
    """Count the number of characters in the text excluding spaces."""
    return len(text.replace(" ", ""))



# func 13
@SpamCodeModelFrame.add_feature(feature_name='HAS_UNICODE_ODDITIES')
def has_unicode_oddities(text):
    """Detect if text contains unusual Unicode characters """

    # shouldnt be an emoji, since spam codes dont contain emojis
    special_chars = ''.join([char for char in text if ord(char) > 127
                             and not emoji.is_emoji(char) and not is_cjk(char)])
    if len(special_chars) > 0:
        return 1
    return 0

# func 14
@SpamCodeModelFrame.add_feature(feature_name='CHAR_ENTROPY')
def get_char_entropy(text):
    """Compute the Shannon entropy of characters in the text."""
    if not text or not isinstance(text, str):
        return 0.0

    text = text.strip()
    if len(text) == 0:
        return 0.0

    counter = Counter(text)
    total_chars = len(text)

    entropy = 0.0
    for count in counter.values():
        p = count / total_chars
        entropy -= p * math.log2(p)

    return entropy

# func 15
@SpamCodeModelFrame.add_feature(feature_name='REGEX_SPAM')
def spam_code_matching(spamcode_string: str) -> int:
    """Detect if string matches a regex pattern typically used in spam codes."""""
    pattern = (r"^(?=[\p{L}\p{N}\p{S}\p{P}]{6,}$)"
               r"[\p{L}\p{N}\p{S}\p{P}]*"
               r"[\d𝟎-𝟗\U0001D7CE-\U0001D7FF]{3,7}$"
    )

    return int(bool(regex.match(pattern, spamcode_string)))


# func 16
@SpamCodeModelFrame.add_feature(feature_name='CLEANED_URL_STR')
def clean_url_str(text: str) -> str:
    """Clean URLs from text and replacing them with placeholders."""
    return URLCleaner.clean_str_with_url(text)


if __name__ == '__main__':
    sms_df = pd.read_csv('model/training_data_refined.csv').sample(800)

    sample_urls = [
    "hELLO https://facebook.com",
    "https://google.com",
    "https://twitter.com",
    "https://youtube.com",
    "https://instagram.com"
    ]

    sms_df = pd.DataFrame({'CONTENT': sample_urls})

    spamcode_df = SpamCodeModelFrame(sms_df)

    spamcode_df = spamcode_df.apply_features()
    print(spamcode_df)
    print(spamcode_df[spamcode_df['CLEANED_URL_STR'].str.strip() == 'url'])
