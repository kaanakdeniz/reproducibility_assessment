from itertools import chain, combinations

import pandas as pd


def df_to_dict(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Converts a dataframe to a dictionary
    """
    return {column: df[[column]] for column in df.columns}


def dict_to_df(dataframes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Returns a merged dataframe with all annotators
    """
    df_values = list(dataframes.values())
    return df_values[0].join(df_values[1:])


def get_intersection(arrays: list[list]) -> list:
    """
    Returns the intersection of multiple lists
    """
    return list(set.intersection(*(set(x) for x in arrays)))


def min_intersected(lists: list[list[str]], min_intersection_count) -> list[str]:
    """
        If there are any intersection between lists for the given minimum intersection count, then the intersections are returned.
    """
    two_combinations = list(combinations(lists, min_intersection_count))
    intersections = [
        get_intersection(combination) for combination in two_combinations
    ]
    return list(set(chain.from_iterable(intersections)))
