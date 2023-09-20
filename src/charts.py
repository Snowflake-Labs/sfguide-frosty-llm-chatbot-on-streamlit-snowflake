import streamlit as st


DEFAULT_TYPE = 0
CHART_FUNCTIONS = [
    {"label": "Table", "func": st.dataframe},
    {"label": "Line Chart", "func": st.line_chart},
    {"label": "Area Chart", "func": st.area_chart},
    {"label": "Bar Chart", "func": st.bar_chart},
]


def render_data(data, key):
    def set_type(i):
        data["type"] = i

    columns = st.columns(len(CHART_FUNCTIONS))
    # render chart type buttons
    for i, column in enumerate(columns):
        with column:
            label = CHART_FUNCTIONS[i]["label"]
            key = f"b_{key}_type_{i}"
            st.button(
                label,
                key=key,
                on_click=set_type,
                args=[i],
            )
    # render chart
    type = data.get("type", DEFAULT_TYPE)
    func = CHART_FUNCTIONS[type]["func"]
    func(data["data"])
