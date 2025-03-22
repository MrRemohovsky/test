import dash
from dash import dcc, html, Input, Output, State
from datetime import datetime

# Заглушка данных
FACTORIES = [{"id": 1, "title": "Завод 1"}, {"id": 2, "title": "Завод 2"}]
DEVICES = [
    {"id": 1, "title": "Устройство 1", "factory_id": 1},
    {"id": 2, "title": "Устройство 2", "factory_id": 1},
    {"id": 3, "title": "Устройство 3", "factory_id": 2}
]
CHARTS = [
    {"id": 1, "title": "Температура", "device_id": 1,
     "time_series": {"x": ["2023-01-01 08:00:00", "2023-01-01 12:00:00", "2023-01-01 16:00:00"], "y": [10, 20, 30]}},
    {"id": 2, "title": "Давление", "device_id": 1,
     "time_series": {"x": ["2023-01-01 08:00:00", "2023-01-01 12:00:00", "2023-01-01 16:00:00"], "y": [5, 15, 25]}},
    {"id": 3, "title": "Скорость", "device_id": 2,
     "time_series": {"x": ["2023-01-01 08:00:00", "2023-01-01 12:00:00", "2023-01-01 16:00:00"], "y": [100, 200, 300]}}
]

# Инициализация Dash с Materialize CSS
app = dash.Dash(
    __name__,
    external_scripts=["https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"],
    external_stylesheets=["https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
                          "/static/style.css"],
    suppress_callback_exceptions=True
)

# Макет приложения
app.layout = html.Div([
    html.H1("Тестовый Дашборд"),
    html.Label("Выберите завод"),
    dcc.Dropdown(
        id="factory-dropdown",
        options=[{"label": f["title"], "value": f["id"]} for f in FACTORIES],
        value=None,
        placeholder="Выберите завод"
    ),
    html.Label("Выберите устройство"),
    dcc.Dropdown(
        id="device-dropdown",
        options=[],
        value=None,
        placeholder="Выберите устройство"
    ),
    html.Label("Фильтр по дате и времени"),
    dcc.Input(
        id="start-date",
        type="text",
        placeholder="Начало (дата)",
        className="datepicker"
    ),
    dcc.Input(
        id="start-time",
        type="text",
        placeholder="Начало (время)",
        className="timepicker"
    ),
    dcc.Input(
        id="end-date",
        type="text",
        placeholder="Конец (дата)",
        className="datepicker"
    ),
    dcc.Input(
        id="end-time",
        type="text",
        placeholder="Конец (время)",
        className="timepicker"
    ),
    html.Button("Применить", id="apply-filter", n_clicks=0),
    html.Div(id="charts-container")
], style={"width": "50%", "margin": "0 auto", "padding": "20px"})

# Инициализация Materialize Datepicker и Timepicker
app.clientside_callback(
    """
    function() {
        M.Datepicker.init(document.querySelectorAll('.datepicker'), {
            format: 'yyyy-mm-dd',
            showClearBtn: true
        });
        M.Timepicker.init(document.querySelectorAll('.timepicker'), {
            twelveHour: false,  // 24-часовой формат
            showClearBtn: true
        });
    }
    """,
    Output("start-date", "id"),
    Input("start-date", "id")
)


# Обновление списка устройств
@app.callback(
    Output("device-dropdown", "options"),
    Input("factory-dropdown", "value")
)
def update_devices(factory_id):
    if not factory_id:
        return []
    return [{"label": d["title"], "value": d["id"]} for d in DEVICES if d["factory_id"] == factory_id]


# Обновление графиков
@app.callback(
    Output("charts-container", "children"),
    Input("apply-filter", "n_clicks"),
    [State("device-dropdown", "value"), State("start-date", "value"), State("start-time", "value"),
     State("end-date", "value"), State("end-time", "value")]
)
def update_charts(n_clicks, device_id, start_date, start_time, end_date, end_time):
    if not device_id:
        return html.Div("Выберите устройство")

    charts = [c for c in CHARTS if c["device_id"] == device_id]
    if not charts:
        return html.Div("Нет данных для этого устройства")

    # Комбинируем дату и время с отладкой
    if start_date and start_time:
        start_datetime = f"{start_date} {start_time}:00"
    else:
        start_datetime = None

    if end_date and end_time:
        end_datetime = f"{end_date} {end_time}:00"
    else:
        end_datetime = None

    print(f"Start: {start_datetime}, End: {end_datetime}")  # Отладка

    chart_elements = []
    for chart in charts:
        filtered_x, filtered_y = filter_data(chart["time_series"], start_datetime, end_datetime)
        print(f"Chart {chart['id']}: x={filtered_x}, y={filtered_y}")
        if not filtered_x or not filtered_y:
            chart_elements.append(html.Div(f"Нет данных для '{chart['title']}'"))
            continue

        fig = build_chart(chart["id"], filtered_x, filtered_y, chart["title"])
        chart_elements.append(dcc.Graph(figure=fig))

    return chart_elements


# Функция фильтрации данных
def filter_data(time_series, start_datetime, end_datetime):
    x_data = time_series["x"]
    y_data = time_series["y"]

    # Если фильтры не указаны, возвращаем все данные
    if not start_datetime or not end_datetime:
        return x_data, y_data

    try:
        start_time = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Ошибка формата даты/времени: {e}")
        return x_data, y_data

    filtered_x = []
    filtered_y = []
    for x, y in zip(x_data, y_data):
        x_datetime = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        if start_time <= x_datetime <= end_time:
            filtered_x.append(x)
            filtered_y.append(y)

    return filtered_x, filtered_y


# Функция построения графиков
def build_chart(chart_id, x_data, y_data, title):
    import plotly.express as px
    chart_types = {1: "line", 2: "bar", 3: "scatter"}
    chart_type = chart_types.get(chart_id, "line")

    if chart_type == "line":
        fig = px.line(x=x_data, y=y_data, title=title)
    elif chart_type == "bar":
        fig = px.bar(x=x_data, y=y_data, title=title)
    else:
        fig = px.scatter(x=x_data, y=y_data, title=title)

    fig.update_layout(xaxis_title="Время", yaxis_title="Значение")
    return fig


if __name__ == "__main__":
    app.run(debug=True)