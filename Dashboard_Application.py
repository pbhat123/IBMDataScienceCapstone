import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("spacex_launch_dash.csv")
df["res"] = df["class"].map({0: "Failure", 1: "Success"})
lo, hi = df["Payload Mass (kg)"].min(), df["Payload Mass (kg)"].max()

opts = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": s, "value": s} for s in df["Launch Site"].unique()
]

app = dash.Dash(__name__)
app.layout = html.Div(
    style={"font-family": '"Open Sans", verdana, arial, sans-serif'},
    children=[
        html.H1("SpaceX Launch Records Dashboard",
                style={"textAlign": "center", "color": "#503D36", "fontSize": 40}),
        dcc.Dropdown("site", opts, "ALL", searchable=True),
        dcc.Graph("pie"),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider("mass", 0, 10000, 1000, value=[lo, hi]),
        dcc.Graph("scatter"),
    ],
)

@app.callback(Output("pie", "figure"), Input("site", "value"))
def pie(site):
    d = df if site == "ALL" else df[df["Launch Site"] == site]
    f = df[df["class"] == 1] if site == "ALL" else d
    fig = px.pie(
        f,
        names="Launch Site" if site == "ALL" else "res",
        title="Total Successful Launches by Site"
        if site == "ALL"
        else f"Launch Success vs Failure for site {site}",
        color="res" if site != "ALL" else None,
        color_discrete_map={"Success": "lightblue", "Failure": "tomato"},
    )
    fig.update_traces(textinfo="percent+label", textposition="inside",
                      marker=dict(line=dict(color="black", width=2)))
    fig.update_layout(hovermode=False)
    return fig

@app.callback(
    Output("scatter", "figure"),
    Input("site", "value"),
    Input("mass", "value"),
)
def scatter(site, m):
    d = df[(df["Payload Mass (kg)"] >= m[0]) & (df["Payload Mass (kg)"] <= m[1])]
    if site != "ALL":
        d = d[d["Launch Site"] == site]
    fig = px.scatter(
        d,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Payload Success Rate for All Sites"
        if site == "ALL"
        else f"Payload Success Rate for site {site}",
    )
    fig.update_layout(yaxis_tickvals=[0, 1])
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)