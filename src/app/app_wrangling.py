"""
takes data from board_games.csv and changes it to a usable format for the app
"""

import pandas as pd
import numpy as np


def call_boardgame_data():
    """
    Returns data from board_game.csv formatted for use in functions
    results in listed values for 'category', 'mechanic, 'publisher'

    :return boardgame_data: a pandas data frame
    """

    # Note that the path is relative to the root folder due to deployment
    # files located in root:
    boardgame_data = pd.read_csv(
        "./data/processed/bgg_data_tsne.csv",
        parse_dates=["year_published"],
        index_col=0,
    )

    boardgame_data["year_published"] = pd.to_datetime(
        boardgame_data["year_published"], format="%Y"
    )

    # Convert NA values for these features to a value:
    values = {"category": "Unknown", "mechanic": "Unknown", "publisher": "Unknown"}
    boardgame_data.fillna(value=values, inplace=True)

    # Create lists from strings:
    cats_split = ["category", "mechanic", "publisher"]
    boardgame_data[cats_split] = (
        boardgame_data[cats_split].stack().str.split(r",(?![+ ])").unstack()
    )

    return boardgame_data


def call_boardgame_filter(
    data, cat=[None], mech=[None], pub=[None], n=None, n_ratings=0
):
    """
    Returns board games filtered based on list of values in
    'category', 'mechanic', 'publisher' columns. Provides
    games in descending order and number of games returned
    can be limited to n.

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()
    :param cat: list of str, list of categories (default [None])
    :param mech: list of str, list of mechanics (default [None])
    :param pub: list of str, list of publishers (default [None])
    :param n: int, optional (default None)
        number of games to be returned
    :param n_rating: int, optional (default None)
        minimum number of ratings to filter on

    :return boardgame_data: a pandas data frame
    """

    # Copy data, deep required as contains lists:
    boardgame_data = data.copy(deep=True)
    # Filter based on minimum number of ratings:
    boardgame_data = rating_filter(boardgame_data, n_ratings)
    # Create dictionary based on user input lists:
    columns = {"category": cat, "mechanic": mech, "publisher": pub}
    # Creates a list of bool series for each column:
    columns_bool = [
        call_bool_series_and(boardgame_data, key, columns[key]) for key in columns
    ]

    # Remove rows that aren't matched:
    boardgame_data = boardgame_data[
        (columns_bool[0] & columns_bool[1] & columns_bool[2])
    ]

    # Sorts by average rating and returns top "n" games if applicable:
    boardgame_data = boardgame_data.sort_values("average_rating", ascending=False)
    if n:
        boardgame_data = boardgame_data[:n]

    return boardgame_data


def call_bool_series_and(data, col, list_):
    """
    Takes filter entries and creates bool series to filter dataframe on.
    Logic is based on matching all entries.
    However, if no values in the column are True, then all values changed to True.

    :param data: pd.DataFrame,
        generated from app_wrangling.call_boardgame_data()
    :param col: string, column name to apply function to
    :param list_: list of str, list of values to check for

    :return list_bool: list of class bool
    """

    list_bool = data[col].apply(lambda x: all(item in x for item in list_))

    # If no True values in entire list, switch all values to True:
    if list_bool.sum() == 0:
        list_bool = ~list_bool

    return list_bool


def call_bool_series_or(data, col, list_):
    """
    Takes filter entries and creates bool series to filter dataframe on.
    Logic is based on matching one of entries.

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()
    :param col: string, column name to apply function to
    :param list_: list of str, list of values to check for

    :return list_bool: list of class bool
    """

    list_bool = data[col].apply(lambda x: any(item in x for item in list_))

    return list_bool


def call_boardgame_radio(
    data, col, list_, year_in=1900, year_out=2200, no_of_ratings=0
):
    """
    Returns filtered data based on selecting
    'category','mechanic', or 'publisher' column
    and a list of values.

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()
    :param col: string, column to filter on
    :param list_: list of str, list of values to check for
    :param year_in: int, year to start filtering on (default 1900)
    :param year_out: int, year to end filtering on (default 2200)
    :param no_of_ratings: int, (default 0)
        minimum number of ratings to filter on

    :return boardgame_date: a pandas data frame
    """

    boardgame_data = data.copy(deep=True)
    # filters data based on years provided
    boardgame_data = year_filter(boardgame_data, year_in, year_out)
    # filter data based on minimum number of ratings
    boardgame_data = rating_filter(boardgame_data, no_of_ratings)
    # subset based on user selection
    boardgame_data = boardgame_data[call_bool_series_or(boardgame_data, col, list_)]
    # call form_group() to add group column
    boardgame_data = form_group(boardgame_data, col, list_)
    # remove all entries that aren't part of a group
    boardgame_data = boardgame_data[boardgame_data["group"] != ""]

    return boardgame_data


def helper_form_group(x, user_list):
    """
    Helper function to check if all values in user list are met.

    :param x: list
    :param user_list: list

    Return "All Selected' if all met.
    """

    if all(item in x for item in user_list):
        return ["All Selected"]
    else:
        return x


def form_group(data, col, list_):
    """
    This takes the selected filter and populates a group column
    indicating which selected values a boardgame has.

    :param data: pd.DataFrame
    :param col: string, column to filter on
    :param list_: list of str, list of values to check for

    :return data: a pandas data frame
    """

    # takes column and forms new one with appropriate groups based on matching
    data["group"] = data[col].apply(lambda x: list(set(x).intersection(set(list_))))

    # replaces groups containing all items with 'All Selected'
    if len(list_) > 1:
        data["group"] = data["group"].apply(lambda x: helper_form_group(x, list_))

    return data


def count_group(data):
    """
    Provides group counts after `call_boardgame_radio()` is used.

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_radio()

    :return data: a pandas data frame
    """

    df_out = data.copy(deep=True)
    # explode dataframe, group, and count to new df
    df_out = df_out.explode("group")
    df_out = pd.DataFrame(df_out.groupby(["year_published", "group"]).game_id.count())
    # rearrange df
    df_out = df_out.unstack().droplevel(0, axis=1)

    # if 'All Selected' exists add counts to other categories
    if "All Selected" in df_out.columns:
        # create series from 'All Selected'
        all_addition = df_out["All Selected"].fillna(0)
        # add counts from 'All Selected to each group'
        revised_columns = df_out.drop(columns=["All Selected"]).apply(
            lambda x: x + all_addition.values
        )
        # create revised df
        df_out = pd.concat([revised_columns, df_out[["All Selected"]]], axis=1)

    return df_out


def call_boardgame_top(data, col, year_in, year_out, no_of_ratings):
    """
    Creates dataframe with top 5 values by user rating in either
    'category', 'mechanic', or 'publisher'

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()
    :param col: string, column to filter on
    :param list_: list of str, list of values to check for
    :param year_in: int, year to start filtering on
    :param year_out: int, year to end filtering on
    :param no_of_ratings: int,
        minimum number of ratings to filter on

    :return board_game_exp: a pandas data frame
    """

    # Copy data, deep required as contains lists:
    boardgame_data = data.copy(deep=True)
    # Filters data based on years provided:
    boardgame_data = year_filter(boardgame_data, year_in, year_out)
    # Filter data based on minimum number of ratings:
    boardgame_data = rating_filter(boardgame_data, no_of_ratings)
    # Split up column into categorical values:
    board_game_exp = boardgame_data.explode(col)
    # Find the average rating for the top 5 categories:
    board_game_exp = (
        board_game_exp.groupby(col)["average_rating"]
        .mean()
        .sort_values(ascending=False)[:5]
        .to_frame()
        .reset_index()
    )
    return board_game_exp


def subset_data(data, col):
    """
    Creates list of categories for column used to populate
    dropdown menus

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()
    :param col: string, column generate list for

    :return list(exp_series.unique()): list of strings
    """

    boardgame_data = data.copy(deep=True)
    exp_series = boardgame_data[col].explode()
    return list(exp_series.unique())


def remove_columns(data):
    """
    Removes columns unnecessary for plotting first two graphs on tab1

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()

    :return boardgame_data[keep]: a pandas data frame
    """

    boardgame_data = data.copy(deep=True)
    keep = ["name", "year_published", "average_rating"]
    if "group" in boardgame_data.columns:
        keep.append("group")

    return boardgame_data[keep]


def call_boardgame_top_density(data, col, year_in, year_out, no_of_ratings):
    """
    Creates dataframe populated with all top 5 values by
    user rating in either 'category', 'mechanic', or 'publisher'

    :param data: pd.DataFrame
        generated from app_wrangling.call_boardgame_data()
    :param col: string, column to filter on
    :param year_in: int, start of time period (inclusive)
    :param year_in: int, end of time period (inclusive)
    :param no_of_ratings: int minimum number of ratings to filter on

    :return boardgame_data: a pandas data frame
    """

    boardgame_data = data.copy(deep=True)

    boardgame_list = call_boardgame_top(data, col, year_in, year_out, no_of_ratings)[
        col
    ].to_list()

    boardgame_data = boardgame_data[
        call_bool_series_or(boardgame_data, col, boardgame_list)
    ]

    boardgame_data = form_group(boardgame_data, col, boardgame_list)
    boardgame_data = boardgame_data.explode("group")

    return boardgame_data


def year_filter(data, year_in, year_out):
    """
    Limits pandas data frame by year range

    :param data: pd.DataFrame
    :param year_in: int, start of time period (inclusive)
    :param year_in: int, end of time period (inclusive)

    :return boardgame_data: a pandas data frame
    """

    boardgame_data = data
    # Turns year inputs to date time:
    year_in = pd.to_datetime(year_in, format="%Y")
    year_out = pd.to_datetime(year_out, format="%Y")

    # Create a boolean series to filter by start + end year:
    year_filter = (boardgame_data["year_published"] >= year_in) & (
        boardgame_data["year_published"] <= year_out
    )
    boardgame_data = boardgame_data[year_filter]

    return boardgame_data


def rating_filter(data, no_of_ratings):
    """
    Limits pandas data frame by minimum
    number of rating

    :param data: pd.DataFrame
    :param no_of_ratings: int
        minimum number of ratings to filter on

    :return boardgame_data: a pandas data frame
    """

    boardgame_data = data

    # Create a boolean series to filter out number of ratings less than required:
    rating_filter = boardgame_data["users_rated"] >= no_of_ratings
    boardgame_data = boardgame_data[rating_filter]

    return boardgame_data


def bin_rating(data):
    """
    Bins the average rating into 0.5 increments

    :param data: pd.DataFrame

    :return data: a pandas dataframe
    """
    # List of bins:
    bin_list = list(np.arange(-0.25, 10.5, 0.5))
    # List of bin labels:
    set_list = list(np.arange(0, 10.5, 0.5))
    # Bins the average rating column:
    data["average_rating_bin"] = pd.cut(
        data["average_rating"], bins=bin_list, labels=set_list
    )

    return data


def density_transform(data, col):
    """
    Creates a density column for average ratings

    :param data: pd.DataFrame
    :param col: string, column to filter on

    :return chart_data: a pandas data frame
    """

    data_copy = data.copy()

    # Create density column:
    plot_density = (
        data_copy.explode("group")
        .groupby(["average_rating_bin", "group"])[col]
        .count()
        .to_frame("density")
        .reset_index()
    )
    # Create mean values:
    plot_mean = (
        data_copy.explode("group")
        .groupby("group")["average_rating"]
        .mean()
        .to_frame("average_rating")
        .reset_index()
    )

    # Generate list of group names:
    names = list(plot_density["group"].unique())
    # Create empty list for chart data:
    chart_data = []

    # Runs through each group and creates density:
    for x in names:
        temp = plot_density[plot_density["group"] == x]
        temp["density"] = temp["density"] / temp["density"].sum()
        temp["mean"] = plot_mean[plot_mean["group"] == x]["average_rating"]
        chart_data.append(temp)

    # Puts back into single dataframe:

    chart_data = pd.concat(chart_data).reset_index().drop(columns="index")

    return chart_data


def clean_table(data):
    """
    Cleans the table on tab 2 including rounding and date formatting.

    :param data: pd.DataFrame

    :return data: a pandas data frame
    """
    data["year_published"] = data["year_published"].dt.year
    data["mechanic"] = [", ".join(map(str, item)) for item in data["mechanic"]]
    data["publisher"] = [", ".join(map(str, item)) for item in data["publisher"]]
    data["category"] = [", ".join(map(str, item)) for item in data["category"]]
    data["average_rating"] = round(data["average_rating"], 2)
    return data
