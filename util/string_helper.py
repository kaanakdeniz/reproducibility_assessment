import re
import string

from cleantext import clean
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

printable_chars = set(string.printable)


def clear_stopwords(tokenized_text: list[str], stopwords) -> list[str]:
    return [w for w in tokenized_text if w not in stopwords]


def clear_special_characters(tokenized_text: list[str]) -> list[str]:
    return [re.sub(r"[^A-Za-z]+", '', text) for text in tokenized_text]


def clear_links(tokenized_text: list[str]) -> list[str]:
    return [re.sub(r'http\S+', '', text) for text in tokenized_text]


def stemming(tokenized_text: list[str]) -> list[str]:
    porter_stemmer = PorterStemmer()
    return [porter_stemmer.stem(word) for word in tokenized_text]


def lemmatization(tokenized_text: list[str]) -> list[str]:
    wordnet_lemmatizer = WordNetLemmatizer()
    return [wordnet_lemmatizer.lemmatize(word) for word in tokenized_text]


def clear_text(text):
    printable_text = ''.join(filter(lambda x: x in printable_chars, text))
    return clean(printable_text, no_emoji=True, lower=False, no_punct=False,
                 no_currency_symbols=True, no_numbers=False, replace_with_currency_symbol="").encode("ascii", errors="ignore").decode()
