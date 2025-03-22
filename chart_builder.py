import plotly.express as px


def build_chart(chart_id, x_data, y_data, title):
    # Словарь для типов графиков по chart_id
    chart_types = {
        1: "line",  # Линейный график для Chart с id=1
        2: "bar",  # Столбчатый график для Chart с id=2
        3: "scatter",  # Точечный график для Chart с id=3
    }

    chart_type = chart_types.get(chart_id, "line")  # По умолчанию линейный

    if chart_type == "line":
        fig = px.line(x=x_data, y=y_data, title=title)
    elif chart_type == "bar":
        fig = px.bar(x=x_data, y=y_data, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(x=x_data, y=y_data, title=title)
    else:
        fig = px.line(x=x_data, y=y_data, title=title)

    fig.update_layout(xaxis_title="Время", yaxis_title="Значение")
    return fig