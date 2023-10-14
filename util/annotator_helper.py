import itertools

import numpy as np
import pandas as pd
from nltk.metrics import agreement

from util.data_structure_helper import df_to_dict, dict_to_df, get_intersection

kappa_range = {
    0: "Poor",
    0.01: "Slight",
    0.21: "Fair",
    0.41: "Moderate",
    0.61: "Substantial",
    0.81: "Almost Perfect"
}


def get_kappa_range(kappa):
    return next(
        (v for k, v in kappa_range.items().__reversed__() if kappa > k and kappa < 1),
        "Perfect",
    )


def form_label_dataframes(merged_dfs: pd.DataFrame) -> list[tuple[str, int, str]]:
    """
    Returns a list of tuples of the form (annotator, index, label)
    """
    keys = merged_dfs.columns
    data = []
    for idx, row in merged_dfs.iterrows():
        data.extend((key, idx, row[key]) for key in keys)
    return data


def select_label_columns(dataframes: dict[str, pd.DataFrame], min_score=0) -> dict[str, pd.DataFrame]:
    """
    Returns a dictionary of dataframes with only the label column with the given minimum score
    """
    dataframes = dataframes.copy()
    for key, df in dataframes.items():
        dataframes[key] = df[df["score"] >= min_score][["label"]]
        dataframes[key].columns = [key]
    return dataframes


def get_agreement(data, metric_f) -> float:
    """
    Returns the agreement between all annotators with the given metric
    """
    a_task = agreement.AnnotationTask(data=data)
    return a_task.__getattribute__(metric_f)()


def get_pairwise_agreements(dfs, metric_f) -> np.ndarray:
    """
    Returns a matrix of pairwise agreements
    """
    matrix = np.zeros((len(dfs), len(dfs)))
    annotators = sorted(dfs.keys())
    for pair in list(itertools.product(dfs.keys(), repeat=2)):
        a, b = pair
        i, j = annotators.index(a), annotators.index(b)
        if a == b:
            matrix[i][j] = 1
            continue
        merged_dfs = dict_to_df({pair[0]: dfs[pair[0]], pair[1]: dfs[pair[1]]})
        data = form_label_dataframes(merged_dfs)
        matrix[i][j] = get_agreement(data, metric_f)
    return matrix


def fix_multiple_labels(merged_dataframes: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], int, dict[str, int], int]:
    """
    Fixes multiple labels for a given dataframe, if there are any intersections between the labels of the annotators
    then the intersection is taken as the label, otherwise the label is set to irrelevant
    """
    dataframes = merged_dataframes.copy()
    df_multi_label = dataframes[dataframes.apply(
        lambda r: r.str.contains('#').any(), axis=1)]
    df_splitted = df_multi_label.apply(
        lambda x: x.str.split('#'))

    not_intersected_count = 0
    intersection_counts = {}
    for idx, value in df_splitted.iterrows():
        intersection = get_intersection(value)
        if len(intersection) == 0:
            not_intersected_count += 1
        else:
            if intersection[0] not in intersection_counts:
                intersection_counts[intersection[0]] = 0
            intersection_counts[intersection[0]] += 1
        df_splitted.loc[idx] = value.apply(
            lambda x: intersection[0] if len(intersection) != 0 else "irrelevant")
    dataframes.loc[df_splitted.index] = df_splitted
    number_of_multi_labels = len(df_multi_label)
    return dataframes, not_intersected_count, intersection_counts, number_of_multi_labels
