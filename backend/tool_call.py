import html
import io
import re
import json
import traceback
import logging
import math
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

cities_data = None

def safe_parse(raw: str) -> dict:
    cleaned = re.sub(r'(?<!\\)\n', ' ', raw)
    cleaned = re.sub(r'(?<!\\)\r', '', cleaned)
    return json.loads(cleaned)

def extract_tool_arguments(line):
    # Extracts the arguments of a tool from a JSON format:
    # {
    # "use_notice": "This is a notice about using the tool",
    # "tool": "TOOL_NAME",
    # "arguments": {
    #   "param1": "example",
    #   "param2": "example"
    #   }
    # }

    try:
        print(repr(line[:200]))
        tool_data = json.loads(line)
        use_notice = tool_data.get("use_notice", {})
        tool_name = tool_data.get("tool")
        arguments = tool_data.get("arguments", {})

        return tool_name, arguments, use_notice
    except json.JSONDecodeError as e:
        print("Erro:", e)
        print("Linha:", repr(line))
        return None, {}, {}
    
    
def get_metrica_total(city='0',before_year=2020, after_year=2024, before_month=1, after_month=12, disaster_type=0, metric_type="total_desastres"):
    global cities_data
    if not cities_data:
        return {"error": "Cities data not initialized"}
    
    data = {}
    data[metric_type] = 0
    
    for row in cities_data:
        if not row.get("Data_Evento"):
            continue
        
        # Parse date
        date_parts = row["Data_Evento"].split("/")
        year = int(date_parts[2]) if len(date_parts) > 2 else None
        month = int(date_parts[1]) if len(date_parts) > 1 else None

        if city != '0' and row.get("Nome_Municipio") != city:
            continue

        if not year or not month:
            continue

        # Filter by date range
        if year > after_year or year < before_year:
            continue
        if month > after_month or month < before_month:
            continue
        
        # Filter by disaster type
        if disaster_type != 0:
            if int(row.get("tipologia", 0)) != disaster_type:
                continue
        
        if metric_type == "total_desastres":
            data[metric_type] += 1
        else:
            data[metric_type] += float(row.get(metric_type, 0) or 0)

    return data

def sort_city_data(before_year=2020, after_year=2024, before_month=1, after_month=12, disaster_type=0, metric_type="total_desastres") -> dict:
    """
    Filters and aggregates city data by time range and disaster type.
    Mirrors the JavaScript sortCityData function.
    """

    global cities_data
    if not cities_data:
        return {"error": "Cities data not initialized"}
    
    city_data = {}
    
    for row in cities_data:
        if not row.get("Data_Evento"):
            continue
        
        # Parse date
        date_parts = row["Data_Evento"].split("/")
        year = int(date_parts[2]) if len(date_parts) > 2 else None
        month = int(date_parts[1]) if len(date_parts) > 1 else None
        
        if not year or not month:
            continue
        
        # Filter by date range
        if year > after_year or year < before_year:
            continue
        if month > after_month or month < before_month:
            continue
        
        # Filter by disaster type
        if disaster_type != 0:
            if int(row.get("tipologia", 0)) != disaster_type:
                continue
        
        # Initialize city entry
        city_name = row.get("Nome_Municipio")
        if city_name not in city_data:
            city_data[city_name] = {
                "nome": city_name,
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "populacao": row.get("populacao"),
                "total_desastres": 0,
                metric_type: 0
            }
        
        city_data[city_name]["total_desastres"] += 1
        value = float(row.get(metric_type, 0) or 0)
        city_data[city_name][metric_type] += value

    return city_data

def get_max_value():
    global cities_data
    if not cities_data:
        return {"error": "Cities data not initialized"}
    
    max_value = 0
    for row in cities_data:
        if row.get("Data_Evento"):
            max_value += 1
    
    return max_value

def get_field_scale(cities, field, scale, k):

    # Guarda (nome_da_cidade, valor)
    city_values = []

    # Filtra os valores relevantes
    for city_name, city_data in cities.items():
        if city_data.get("latitude") and city_data.get("longitude"):
            value = city_data.get(field)

            if (
                value is not None
                and value != ""
                and not math.isnan(value)
                and value != 0
            ):
                city_values.append((city_name, value))

    if not city_values:
        return {
            "top_k": []
        }


    if scale == "max":
        city_values.sort(key=lambda x: x[1], reverse=True)
    elif scale == "min":
        city_values.sort(key=lambda x: x[1])
    else:
        raise ValueError(f"Unknown scale: {scale!r}")
    
    top_k = city_values[:k]

    return {
        "top_k": top_k
    }

def create_bar_plot(arguments):
    fig, ax = plt.subplots()
    
    categorias = arguments.get("categorias", [])
    valores = arguments.get("valores", [])
    titulo = arguments.get("title", "")
    xlabel = arguments.get("xlabel", "")
    ylabel = arguments.get("ylabel", "")
    
    ax.bar(categorias, valores)
    ax.set_title(titulo)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    plt.close(fig)

    return buffer.getvalue()

def create_line_plot(arguments):
    fig, ax = plt.subplots()
    
    categorias = arguments.get("categorias", [])
    valores = arguments.get("valores", [])
    titulo = arguments.get("title", "")
    xlabel = arguments.get("xlabel", "")
    ylabel = arguments.get("ylabel", "")
    
    ax.plot(categorias, valores)
    ax.set_title(titulo)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    plt.close(fig)

    return buffer.getvalue()

def create_pie_chart(arguments):
    fig, ax = plt.subplots()
    
    categorias = arguments.get("categorias", [])
    valores = arguments.get("valores", [])
    titulo = arguments.get("title", "")
    
    ax.pie(valores, labels=categorias, autopct='%1.1f%%')
    ax.set_title(titulo)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    plt.close(fig)

    return buffer.getvalue()

def create_scatter_plot(arguments):
    fig, ax = plt.subplots()
    
    x_valores = arguments.get("x_valores", [])
    y_valores = arguments.get("y_valores", [])
    titulo = arguments.get("title", "")
    xlabel = arguments.get("xlabel", "")
    ylabel = arguments.get("ylabel", "")
    
    ax.scatter(x_valores, y_valores)
    ax.set_title(titulo)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    plt.close(fig)

    return buffer.getvalue()

def create_histogram(arguments):
    fig, ax = plt.subplots()
    
    valores = arguments.get("valores", [])
    bins = arguments.get("bins", 10)
    titulo = arguments.get("title", "")
    xlabel = arguments.get("xlabel", "")
    ylabel = arguments.get("ylabel", "")
    
    ax.hist(valores, bins=bins)
    ax.set_title(titulo)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    plt.close(fig)

    return buffer.getvalue()

def create_report(arguments):
    from xhtml2pdf import pisa  # lazy import

    nome_relatorio = arguments.get("nome_relatorio", "relatorio.pdf")
    conteudo_html = arguments.get("conteudo", "")
    buffer = io.BytesIO()
    result = pisa.CreatePDF(src=conteudo_html, dest=buffer)
    if result.err:
        raise RuntimeError("Failed to generate PDF")
    return buffer.getvalue()


# TOOL LOGIC -------------------------------------------------------------------

def manage_tool_call(tool_call, tool_results):
    tool_name, arguments, use_notice = extract_tool_arguments(tool_call)
    results = None

    if tool_name == "maior_metrica":
        sorted_data = sort_city_data(
            arguments.get("ano_inicio", 2020),
            arguments.get("ano_fim", 2024),
            arguments.get("mes_inicio", 1),
            arguments.get("mes_fim", 12),
            arguments.get("tipologia", 0),
            arguments.get("metrica", "total_desastres")
        )
        max_value = get_field_scale(sorted_data, arguments.get("metrica", "total_desastres"), "max", arguments.get("k", 5))
        results = max_value

    elif tool_name == "menor_metrica":
        sorted_data = sort_city_data(
            arguments.get("ano_inicio", 2020),
            arguments.get("ano_fim", 2024),
            arguments.get("mes_inicio", 1),
            arguments.get("mes_fim", 12),
            arguments.get("tipologia", 0),
            arguments.get("metrica", "total_desastres")
        )
        min_value = get_field_scale(sorted_data, arguments.get("metrica", "total_desastres"), "min", arguments.get("k", 5))
        results = min_value

    elif tool_name == "metrica_total":
        total = get_metrica_total(
            arguments.get("cidade", 0),
            arguments.get("ano_inicio", 2020),
            arguments.get("ano_fim", 2024),
            arguments.get("mes_inicio", 1),
            arguments.get("mes_fim", 12),
            arguments.get("tipologia", 0),
            arguments.get("metrica", "total_desastres")
        )
        results = total

    elif tool_name == "criar_grafico":
        graph_type = arguments.get("tipo_grafico")
        image_data = None
        if graph_type in ("bar", "barra"):
            image_data = create_bar_plot(arguments)
        elif graph_type in ("line", "linha"):
            image_data = create_line_plot(arguments)
        elif graph_type in ("pie", "pizza", "torta"):
            image_data = create_pie_chart(arguments)
        elif graph_type in ("scatter", "dispersao"):
            image_data = create_scatter_plot(arguments)
        elif graph_type in ("histogram", "histograma"):
            image_data = create_histogram(arguments)

        if image_data:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            base64_html_image = f"data:image/png;base64,{base64_image}"
            image = f"""
            <div class="image-container" style="text-align: center;">
                <img src=\"{base64_html_image}\" style=\"max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0;\">
                <a href=\"{base64_html_image}\" download="chart.png" class="download-btn">
                    <img src="images/download_icon.png" class="main-icon" alt="Baixar Gráfico" style="width: 24px; height: 24px; margin-top: 5px;">
                </a>
            </div>
            """
            return image
    
    elif tool_name == "criar_relatorio":
        pdf_data = create_report(arguments)
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        nome_relatorio = arguments.get('nome_relatorio', 'relatorio.pdf')
        return f"""
        <button class="download-artifact-container" data-pdf-url="data:application/pdf;base64,{base64_pdf}" data-filename="{nome_relatorio}">
            <img src="images/download_icon.png" class="main-icon" alt="Baixar Relatório" style="width: 24px; height: 24px;">
            {nome_relatorio}
        </button>
        """

    else:
        raise ValueError(f"Unknown tool: {tool_name!r}")
    
    if tool_name not in tool_results:
        tool_results[tool_name] = []
    tool_results[tool_name].append({
        "arguments": arguments,
        "result": results
    })

    print(f"Tool call: {tool_name} with arguments {arguments} returned result {results}")