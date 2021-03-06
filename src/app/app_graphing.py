"""
contains graph calls for dashboard
"""

import altair as alt
import app_wrangling as app_wr
import plotly.graph_objs as go


def scatter_plot_dates(data, col="category", list_=[], n_ratings=0):
    """
    Takes in inputs filtering data and creates an altair scatter
    plot for comparison of user ratings over time

    :param data: a pandas df generated from app_wrangling.call_boardgame_data()
    :param col: string indicating which column (default 'category')
    :param list_: list of elements in column (default [])
    :param n_ratings: int of number of minimum rating to filter (default 0)

    :return scatter_plot: altair plot
    """

    # Need to disable max rows in case of showing entire dataset:
    alt.data_transformers.disable_max_rows()
    # If no elements selected return entire dataset:
    if (list_ == [None]) or (not list_):
        set_scatter = app_wr.rating_filter(data, n_ratings)
        # colors the graph grey:
        set_scatter_col = alt.value("grey")
    else:
        set_scatter = app_wr.call_boardgame_radio(
            data, col, list_, no_of_ratings=n_ratings
        ).explode("group")
        # colors the graph according to elements selected:
        set_scatter_col = alt.Color(
            "group:N", title=None, scale=alt.Scale(scheme="dark2")
        )
    # removes extraneous columns:
    reduced_data = app_wr.remove_columns(set_scatter)
    # creates altair scatter plot:
    scatter_plot = (
        alt.Chart(reduced_data)
        .mark_circle(size=60, opacity=0.2)
        .encode(
            alt.X(
                "year_published:T",
                axis=alt.Axis(title=None, labelFontSize=13, titleFontWeight=100),
                scale=alt.Scale(zero=False),
            ),
            alt.Y(
                "average_rating:Q",
                axis=alt.Axis(
                    title="Average Rating",
                    titleFontSize=15,
                    offset=14,
                    titleFontWeight=100,
                    labelFontSize=13,
                ),
            ),
            color=set_scatter_col,
            tooltip=[
                alt.Tooltip("name:N", title="Name"),
                alt.Tooltip("average_rating:Q", title="Average Rating"),
                alt.Tooltip("year_published:T", title="Year Published", format="%Y"),
            ],
        )
        .properties(
            width=650,
            height=150,
        )
    )
    # create data for the total mean user rating:
    line_plot_data = (
        data[["year_published", "average_rating"]].groupby("year_published").mean()
    ).reset_index()
    # creates altair plot of the total mean user rating:
    line_plot = (
        alt.Chart(line_plot_data)
        .mark_line(color="#62a9b5", size=3, opacity=0.6)
        .encode(x="year_published:T", y="average_rating")
    )
    # combine plots:
    scatter_plot = (
        (scatter_plot + line_plot)
        .configure(background="transparent")
        .configure_legend(titleFontSize=18, labelFontSize=13)
    )
    return scatter_plot


def count_plot_dates(data, col="category", list_=[], n_ratings=0):
    """
    Takes input filtering data and creates
    a plot counting how many game occurrences

    :param data: a pandas df generated from app_wrangling.call_boardgame_data()
    :param col: string indicating which column (default 'category')
    :param list_: list of elements in column (default [])
    :param n_ratings: int of number of minimum rating to filter (default 0)

    :return count_plot: altair plot
    """

    # Need to disable max rows in case of showing entire dataset:
    alt.data_transformers.disable_max_rows()
    # If no elements selected return entire dataset:
    if (list_ == [None]) or (not list_):
        set_data = app_wr.rating_filter(data, n_ratings)
        # colors the graph blue:
        set_color = alt.value("#62a9b5")
    else:
        set_data = app_wr.call_boardgame_radio(
            data, col, list_, no_of_ratings=n_ratings
        ).explode("group")
        # colors the graph according to elements selected:
        set_color = alt.Color("group:N", title=None, scale=alt.Scale(scheme="dark2"))
    # removes extraneous columns:
    reduced_data = app_wr.remove_columns(set_data)
    reduced_data = reduced_data.drop(columns=["name"])

    grouping_columns = ["year_published"]
    if "group" in reduced_data.columns:
        grouping_columns.append("group")
    grouped_data = reduced_data.groupby(grouping_columns).count()
    grouped_data.columns = ["count"]
    grouped_data = grouped_data.reset_index()
    # create altair bar chart:
    count_plot = (
        alt.Chart(grouped_data)
        .mark_bar()
        .encode(
            alt.X(
                "year_published:T",
                axis=alt.Axis(title=None, labelFontSize=13, titleFontWeight=100),
                scale=alt.Scale(zero=False),
            ),
            alt.Y(
                "count:Q",
                axis=alt.Axis(
                    title="Count",
                    titleFontSize=15,
                    offset=8,
                    titleFontWeight=100,
                    labelFontSize=13,
                ),
            ),
            color=set_color,
            tooltip=[
                alt.Tooltip("group:N", title="Group"),
                alt.Tooltip("count:Q", title="Number of Games"),
                alt.Tooltip("year_published:T", title="Year_Published", format="%Y"),
            ],
        )
        .properties(
            width=650,
            height=150,
        )
        .configure(background="transparent")
        .configure_legend(titleFontSize=18, labelFontSize=13)
    )
    return count_plot


def rank_plot_density(
    data, col="category", list_=[], year_in=1990, year_out=2010, n_ratings=0
):
    """
    Creates altair graph of set column for set years

    :param data: a pandas df generated from app_wrangling.call_boardgame_data()
    :param col: string indicating which column (default 'category')
    :param list_: list of elements in column (default [])
    :param year_in: int of year to start filtering on (default 1990)
    :param year_out: int of year to stop filtering on (default 2010)
    :param n_ratings: int of number of minimum rating to filter (default 0)

    :return out_plot: altair plot
    """

    # If no elements selected return entire dataset:
    if not bool(list_):
        plot_data = app_wr.call_boardgame_top_density(
            data, col, year_in, year_out, n_ratings
        )
    else:
        plot_data = app_wr.call_boardgame_radio(
            data, col, list_, year_in, year_out, n_ratings
        )
    # Bins average rating:
    plot_data = app_wr.bin_rating(plot_data)
    # Creates density column:
    plot_data = app_wr.density_transform(plot_data, col)
    # Creates altair density chart:
    rank_plot = (
        alt.Chart(plot_data, height=80)
        .mark_area(
            interpolate="monotone", fillOpacity=0.8, stroke="lightgray", strokeWidth=0.5
        )
        .encode(
            alt.X(
                "average_rating_bin:Q",
                title="Average Rating",
                axis=alt.Axis(
                    labelFontSize=13, titleFontSize=15, titleFontWeight=100, grid=False
                ),
            ),
            alt.Y(
                "density:Q",
                title=None,
                scale=alt.Scale(domain=[0, 1]),
                axis=None,
            ),
            alt.Color("group:N", title=None, scale=alt.Scale(scheme="dark2")),
        )
    )
    # creates rule of mean average rating:
    avg_line = (
        alt.Chart(plot_data)
        .mark_rule(color="black")
        .encode(
            x=alt.X("mean", title="Average Rating"),
            fill=alt.Fill("group", legend=None),
            tooltip=[
                alt.Tooltip("group:N", title="Group"),
                alt.Tooltip("mean:Q", title="Mean"),
            ],
        )
    )
    # combines density and rule chart:
    out_plot = (
        (rank_plot + avg_line)
        .facet(
            row=alt.Row(
                "group:N",
                title=None,
                header=alt.Header(labelAngle=0, labelAlign="left", labelFontSize=13),
            )
        )
        .properties(bounds="flush")
        .configure(background="transparent")
        .configure_legend(titleFontSize=18, labelFontSize=13)
        .configure_facet(spacing=0)
        .configure_view(stroke=None, strokeOpacity=0)
    )
    return out_plot


def top_n_plot(data, cat=[None], mech=[None], pub=[None], n=10, n_ratings=0):
    """
    Creates altair graph for top "n" games with filtered data

    :param data: a pandas df generated from app_wrangling.call_boardgame_data()
    :param cat: list of elements in category (default [None])
    :param mech: list of elements in mechanic (default [None])
    :param pub: list of elements in publisher (default [None])
    :param n: int of maximum games to call (default 10)
    :param n_ratings: int of number of minimum rating to filter (default 0)

    :return out_plot: altair plot
    """

    # Need to disable max rows in case of showing entire dataset:
    alt.data_transformers.disable_max_rows()
    # Filters data:
    plot_data = app_wr.call_boardgame_filter(data, cat, mech, pub, n, n_ratings)

    # Create altair bar chart:
    top_plot = (
        alt.Chart(plot_data)
        .mark_bar()
        .encode(
            alt.X(
                "name:N",
                sort="-y",
                axis=alt.Axis(title=None, labels=False, ticks=False),
            ),
            alt.Y(
                "average_rating:Q",
                axis=alt.Axis(
                    title="Average Rating",
                    labelFontSize=13,
                    titleFontSize=15,
                    grid=False,
                    titleFontWeight=100,
                ),
                scale=alt.Scale(domain=(0, 10)),
            ),
            color=alt.Color(
                "name:N",
                title="Boardgame Name",
                sort=alt.EncodingSortField("-y", order="descending"),
                scale=alt.Scale(scheme="dark2"),
            ),
            tooltip=[
                alt.Tooltip("name", title="Name"),
                alt.Tooltip("users_rated", title="# of Ratings"),
            ],
        )
        .properties(
            width=600,
            height=300,
        )
    )
    # Create text of bar chart ratings:
    top_text = top_plot.mark_text(align="center", baseline="bottom", dy=-3).encode(
        text=alt.Text("average_rating:Q", format=",.2r")
    )
    # Combine bar and text charts:
    out_plot = (
        (top_plot + top_text)
        .configure(background="transparent")
        .configure_legend(titleFontSize=15, labelFontSize=13, titleFontWeight=100)
        .configure_view(strokeOpacity=0)
    )
    return out_plot


def graph_3D(data, col="category", list_=[None], game=None, extents=None):
    """
    3D t-sne graph data output

    :param data: a pandas df generated from app_wrangling.call_boardgame_data()
    :param col: string indicating which column (default 'category')
    :param list_: list of elements in column (default [None])
    :param game: string of board game name (default None)
    :param extents: string (default None)

    :return fig_out: 3D plotly figure
    """
    # layout for the 3D plot:
    axis_x = dict(
        title="",
        showgrid=True,
        zeroline=False,
        showticklabels=False,
        showspikes=False,
        range=[extents["min_x"], extents["max_x"]],
    )
    axis_y = axis_x.copy()
    axis_y["range"] = [extents["min_y"], extents["max_y"]]
    axis_z = axis_x.copy()
    axis_z["range"] = [extents["min_z"], extents["max_z"]]

    layout_out = go.Layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(xaxis=axis_x, yaxis=axis_y, zaxis=axis_z),
        legend=dict(yanchor="top", y=0.93, xanchor="right", x=0.99),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # plotting data:
    if (list_ == [None]) or (not list_):
        set_data = data.copy(deep=True)
        set_data["group"] = "none"
    else:
        set_data = app_wr.call_boardgame_radio(data, col, list_).explode("group")

    data_out = []
    # corresponds with dark2 palette:
    # had trouble manually setting color palette for graph_object:
    color_list = [
        "#1b9e77",
        "#d95f02",
        "#7570b3",
        "#e7298a",
        "#66a61e",
        "#e6ab02",
        "#a6761d",
        "#666666",
    ]
    i = 0
    for idx, val in set_data.groupby(set_data.group):
        if idx == "none":
            marker_style = dict(
                size=val["average_rating"] * 1.6,
                symbol="circle",
                opacity=0.1,
                color="grey",
            )
            legend_show = False

        else:
            marker_style = dict(
                size=val["average_rating"] * 1.6,
                symbol="circle",
                opacity=0.4,
                color=color_list[i],
            )
            legend_show = True
            i += 1

        scatter = go.Scatter3d(
            name=idx,
            x=val["x"],
            y=val["y"],
            z=val["z"],
            mode="markers",
            marker=marker_style,
            text=val["name"],
            hoverinfo="text+name",
            showlegend=legend_show,
        )
        data_out.append(scatter)

    if game:
        game_data = data[data["name"] == game]
        marker_style = dict(
            size=game_data["average_rating"] * 1.6,
            symbol="circle",
            opacity=1.0,
            color="purple",
        )

        scatter = go.Scatter3d(
            name=game,
            x=game_data["x"],
            y=game_data["y"],
            z=game_data["z"],
            mode="markers",
            marker=marker_style,
            text=game_data["name"],
            hoverinfo="text",
        )
        data_out.append(scatter)

    fig_out = {"data": data_out, "layout": layout_out}

    return fig_out
