import dash
from dash import dcc, html, Input, Output
from datetime import datetime

# Заглушка данных
FACTORIES = [
    {"id": 1, "title": "Завод 1"},
    {"id": 2, "title": "Завод 2"}
]

DEVICES = [
    {"id": 1, "title": "Устройство 1", "factory_id": 1},
    {"id": 2, "title": "Устройство 2", "factory_id": 1},
    {"id": 3, "title": "Устройство 3", "factory_id": 2}
]

CHARTS = [
    {"id": 1, "title": "Температура", "device_id": 1,
     "time_series": {"x": ["2023-01-01", "2023-01-02", "2023-01-03"], "y": [10, 20, 30]}},
    {"id": 2, "title": "Давление", "device_id": 1,
     "time_series": {"x": ["2023-01-01", "2023-01-02", "2023-01-03"], "y": [5, 15, 25]}},
    {"id": 3, "title": "Скорость", "device_id": 2,
     "time_series": {"x": ["2023-01-01", "2023-01-02", "2023-01-03"], "y": [100, 200, 300]}}
]

# Инициализация Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Макет главной страницы
app.layout = html.Div([
    html.H1("Тестовый Дашборд", style={"text-align": "center"}),
    html.Div([
        html.Label("Выберите завод:"),
        dcc.Dropdown(
            id="factory-dropdown",
            options=[{"label": f["title"], "value": f["id"]} for f in FACTORIES],
            value=None,
            placeholder="Завод"
        ),
        html.Label("Выберите устройство:"),
        dcc.Dropdown(
            id="device-dropdown",
            options=[],
            value=None,
            placeholder="Устройство"
        ),
        html.Label("Фильтр по дате:"),
        dcc.DatePickerRange(
            id="date-filter",
            start_date_placeholder_text="Начало",
            end_date_placeholder_text="Конец"
        ),
        html.Div(id="charts-container", style={"margin-top": "20px"})
    ], style={"width": "50%", "margin": "0 auto", "padding": "20px"})
])


# Callback для обновления списка устройств
@app.callback(
    Output("device-dropdown", "options"),
    Input("factory-dropdown", "value")
)
def update_devices(factory_id):
    if not factory_id:
        return []
    devices = [d for d in DEVICES if d["factory_id"] == factory_id]
    return [{"label": d["title"], "value": d["id"]} for d in devices]


# Callback для построения графиков
@app.callback(
    Output("charts-container", "children"),
    [Input("device-dropdown", "value"), Input("date-filter", "start_date"), Input("date-filter", "end_date")]
)
def update_charts(device_id, start_date, end_date):
    if not device_id:
        return html.Div("Выберите устройство")

    charts = [c for c in CHARTS if c["device_id"] == device_id]
    if not charts:
        return html.Div("Нет данных для этого устройства")

    chart_elements = []
    for chart in charts:
        filtered_x, filtered_y = filter_data(chart["time_series"], start_date, end_date)
        print(f"Chart {chart['id']}: x={filtered_x}, y={filtered_y}")  # Отладка
        if not filtered_x or not filtered_y:
            chart_elements.append(html.Div(f"Нет данных для графика '{chart['title']}' в выбранном диапазоне"))
            continue

        fig = build_chart(chart["id"], filtered_x, filtered_y, chart["title"])
        chart_elements.append(dcc.Graph(figure=fig))

    return chart_elements


# Функция фильтрации данных (только по дате)
def filter_data(time_series, start_date, end_date):
    x_data = time_series["x"]
    y_data = time_series["y"]

    if not start_date or not end_date:
        return x_data, y_data

    filtered_x = []
    filtered_y = []
    for x, y in zip(x_data, y_data):
        if start_date <= x <= end_date:  # Сравнение строковых дат
            filtered_x.append(x)
            filtered_y.append(y)

    return filtered_x, filtered_y


# Функция построения графиков
def build_chart(chart_id, x_data, y_data, title):
    import plotly.express as px
    chart_types = {
        1: "line",  # Линейный график
        2: "bar",  # Столбчатый график
        3: "scatter"  # Точечный график
    }

    chart_type = chart_types.get(chart_id, "line")

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


# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
