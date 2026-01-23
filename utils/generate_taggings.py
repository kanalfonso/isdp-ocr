# run in cd sms_spam_type_clf
"""
Pass a dataframe then this script will generate the spam tag outputs
"""



# ===== Third-party libraries =====
from IPython.display import display
import pandas as pd
import numpy as np
import joblib
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# ===== Local/project imports =====
from utils import spamcode_utils
from utils.spamtype_utils import TextPreprocessor

# ===== Setup =====
tqdm.pandas()

# Shorten class names
SpamCodeModelFrame = spamcode_utils.SpamCodeModelFrame
URLCleaner = spamcode_utils.URLCleaner


#### CONFIGS ####
SPAM_CODE_CLF_PATH = 'models/spam_code_clf.pkl'
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
SMS_SPAM_TYPE_CLF_PATH = 'models/sms_spam_type_clf.pkl'


############## STEP 1 ##############
def step_1(spamshield_df):
    # print("\nStep 1: Removing no record rows / no record indeces....")

    condition_1 = spamshield_df['CONTENT'].str.strip().str.lower() == 'no record'
    # condition_2 = raw_holdout_df['Campaign Key'].str.strip().str.lower() == 'no record'
    complete_records_spamshield_df = spamshield_df[~(condition_1)].copy()

    no_record_indeces = spamshield_df[condition_1].index

    return complete_records_spamshield_df, spamshield_df, no_record_indeces





############## STEP 2 ##############

def step_2(complete_records_spamshield_df):
    # print("\nStep 2: Generating spam code features....")
    spamcode_df = SpamCodeModelFrame(complete_records_spamshield_df, raw_text_col_name='CONTENT')
    display(spamcode_df.apply_features())

    return spamcode_df




############## STEP 3 ##############
def step_3(spamcode_df):
    # print("\nStep 3: Calling spam code model....")
    spam_code_clf = joblib.load(SPAM_CODE_CLF_PATH)
    spamcode_features = [
        "LETTER_TO_SYMBOL_RATIO",
        "SPECIAL_CHAR_RATIO",
        "MAX_CONSEC_CONSONANTS",
        "HAS_IMSI_STR",
        "HAS_CJK",
        "HAS_URL",
        "DIGIT_RATIO",
        "CAPITAL_LETTER_TO_WORD_RATIO",
        "CHAR_LENGTH",
        "CAPITAL_LETTER_COUNT",
        "WORD_COUNT",
        "AVG_CAPS_PER_WORD",
        "NON_SPACE_CHAR_LENGTH",
        "HAS_UNICODE_ODDITIES",
        "CHAR_ENTROPY",
        "REGEX_SPAM"
    ]


    spam_code_modeling_df = spamcode_df.display_dataframe()
    X = spam_code_modeling_df[spamcode_features]

    X['IS_SPAM_CODE_PRED'] = spam_code_clf.predict(X)

    return spam_code_modeling_df, X





############## STEP 4 ##############
def step_4(spam_code_modeling_df, X):
    # print("\nStep 4: Determining spam code prediction....")
    df1 = spam_code_modeling_df[['CONTENT', 'REGEX_SPAM', 'HAS_CJK', 'HAS_IMSI_STR', 'HAS_URL']]
    df2 = X[['IS_SPAM_CODE_PRED']]

    spam_code_eval_df = pd.concat([df1, df2], axis=1)


    def get_final_spam_code_pred(row) -> int:
        """
        Determine the final spam code prediction for a given row.

        A row is classified as spam (1) if either:
        - REGEX_SPAM = 1, OR
        - IS_SPAM_CODE_PRED = 1,
        AND at least one of the following is 0:
        - HAS_IMSI_STR = 0
        - HAS_CJK = 0
        - HAS_URL = 0
        """
        if (
            (row['REGEX_SPAM'] == 1 or row['IS_SPAM_CODE_PRED'] == 1)
            and (row['HAS_IMSI_STR'] == 0 or row['HAS_CJK'] == 0 or row['HAS_URL'] == 0)
        ):
            return 1

        return 0


    spam_code_eval_df['IS_SPAM_CODE_PRED_FINAL'] = spam_code_eval_df\
                                                    .progress_apply(get_final_spam_code_pred, axis=1)


    spamcode_indeces = spam_code_eval_df[spam_code_eval_df['IS_SPAM_CODE_PRED_FINAL'] == 1].index

    non_spam_code_indices = spam_code_eval_df[spam_code_eval_df['IS_SPAM_CODE_PRED_FINAL'] == 0].index

    sms_no_spamcodes_df = spam_code_modeling_df[spam_code_modeling_df.index.isin(non_spam_code_indices)]

    return sms_no_spamcodes_df, spamcode_indeces




############## STEP 5 ##############
def step_5(sms_no_spamcodes_df):
    # print("\nStep 5: Generating spam type features....")

    filtered_sms_no_spamcodes_df = sms_no_spamcodes_df.copy()

    text_cleaning_pipeline = TextPreprocessor(filtered_sms_no_spamcodes_df, raw_text_col_name='CONTENT')
    cleaned_sms_no_spamcodes_df = text_cleaning_pipeline.clean_raw_text()

    # if text_final is NaN, fill with raw_text instead 
    cleaned_sms_no_spamcodes_df['TEXT_FINAL'] = cleaned_sms_no_spamcodes_df['TEXT_FINAL']\
                                                    .fillna(cleaned_sms_no_spamcodes_df['CONTENT'])


    only_url_str_masking = cleaned_sms_no_spamcodes_df['CLEANED_URL_STR'].str.strip() == 'url'
    imsi_str_masking = cleaned_sms_no_spamcodes_df['HAS_IMSI_STR'] == 1


    sms_no_spamcodes_no_url_no_imsi_df = cleaned_sms_no_spamcodes_df[~only_url_str_masking 
                                                                    & ~imsi_str_masking]

    imsi_indeces = cleaned_sms_no_spamcodes_df[imsi_str_masking].index
    url_indeces = cleaned_sms_no_spamcodes_df[only_url_str_masking].index

    return sms_no_spamcodes_no_url_no_imsi_df, imsi_indeces, url_indeces





############## STEP 6 ##############
def step_6(sms_no_spamcodes_no_url_no_imsi_df):
    # print("\nStep 6: Generating embeddings....")


    cols_to_keep = ['sender', 'TEXT_FINAL']
    modeling_df = sms_no_spamcodes_no_url_no_imsi_df.copy()[cols_to_keep]

    # Load model
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Optional: show progress bar for batches
    tqdm.pandas()

    # Step 1: Get texts as list
    texts = modeling_df['TEXT_FINAL'].astype(str).tolist()

    # Step 2: Batch encode
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)  # you can tune batch_size

    # Step 3: Save embeddings to one column
    modeling_df['EMBEDDINGS'] = embeddings.tolist()

    return modeling_df




############## STEP 7 ##############
def step_7(modeling_df):
    # print("\nStep 7: Predicting spam type....")

    sms_clf = joblib.load(SMS_SPAM_TYPE_CLF_PATH)
    embeddings = pd.DataFrame(np.vstack(modeling_df['EMBEDDINGS'].values))
    modeling_df['SPAM_TYPE_PRED_NUM'] = sms_clf.predict(embeddings)

    modeling_df['SPAM_TYPE_PRED_WORD'] = modeling_df['SPAM_TYPE_PRED_NUM'].progress_apply(
        lambda x: (
            'COMMERCIAL'
            if x == 0
            else 'LOAN/SCAM/SPAM'
            if x == 1
            else 'P2P'
        )
    )


    label_mapping_df = modeling_df[['SPAM_TYPE_PRED_WORD', 'SPAM_TYPE_PRED_NUM']]
    predicted_spam_type_indeces = label_mapping_df.index

    return predicted_spam_type_indeces, label_mapping_df




############## STEP 8 ##############
def step_8(
        spamshield_df,
        spamcode_indeces,
        url_indeces,
        imsi_indeces,
        no_record_indeces,
        predicted_spam_type_indeces,
        label_mapping_df

    ):

    # print("\nStep 8: Assigning labels....")
    output_table = spamshield_df.copy()

    # create col
    # spam codes, url, imsi, no records
    output_table.loc[
        spamcode_indeces, 
        'spam_tag'
    ] = 'SPAM_CODE'

    output_table.loc[
        url_indeces, 
        'spam_tag'
    ] = 'URL_ONLY'

    output_table.loc[
        imsi_indeces, 
        'spam_tag'
    ] = 'IMSI_ONLY' 

    output_table.loc[
        no_record_indeces, 
        'spam_tag'
    ] = 'NO_RECORD' 

    output_table.loc[
        predicted_spam_type_indeces, 
        'spam_tag'
    ] = label_mapping_df['SPAM_TYPE_PRED_WORD'].tolist()



    # print("\nPrediction complete!")
    # print(output_table)

    return output_table


def pipeline():
    # print("Pipeline begin\n")
    
    # print("Step 0: Loading dataframe...")

    data = [
        {
            'id': 1,
            'sender': 'Juan',
            'CONTENT': 'Your loan has been approved. Click the link to proceed.',
            'spam_tag': 'LOAN/SCAM/SPAM'
        },
        {
            'id': 2,
            'sender': 'Maya',
            'CONTENT': 'Congratulations! You won a cash prize. Reply YES to claim.',
            'spam_tag': 'SCAM/SPAM'
        },
        {
            'id': 3,
            'sender': 'BankPH',
            'CONTENT': 'Reminder: Your credit card payment is due tomorrow.',
            'spam_tag': 'LEGIT'
        },
        {
            'id': 4,
            'sender': 'Unknown',
            'CONTENT': 'Limited offer! Get instant cash with no requirements.',
            'spam_tag': 'LOAN/SPAM'
        },
        {
            'id': 5,
            'sender': 'Globe',
            'CONTENT': 'Your data promo will expire today. Register now.',
            'spam_tag': 'LEGIT'
        }
    ]

    spamshield_df = pd.DataFrame(data)

    complete_records_spamshield_df, spamshield_df, no_record_indeces = step_1(spamshield_df)

    spamcode_df = step_2(complete_records_spamshield_df)

    spam_code_modeling_df, X = step_3(spamcode_df)

    sms_no_spamcodes_df, spamcode_indeces = step_4(spam_code_modeling_df, X)

    sms_no_spamcodes_no_url_no_imsi_df, imsi_indeces, url_indeces = step_5(sms_no_spamcodes_df)

    modeling_df = step_6(sms_no_spamcodes_no_url_no_imsi_df)

    predicted_spam_type_indeces, label_mapping_df = step_7(modeling_df)

    output_table = step_8(
        spamshield_df,
        spamcode_indeces,
        url_indeces,
        imsi_indeces,
        no_record_indeces,
        predicted_spam_type_indeces,
        label_mapping_df

    )

    # print("\nPipeline complete")

    

if __name__ == '__main__':
    pipeline()