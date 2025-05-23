import gradio as gr
import geopandas as gpd
from data_processor import DataProcessor
from visualizer import Visualizer
import os
import webbrowser

processor = DataProcessor()

def handle_file(file):
    if file is None:
        return "Nenhum arquivo carregado.", ""

    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'csv':
            processor.load_csv(file.name)
        elif ext == 'json':
            processor.load_json(file.name)
        elif ext == 'xml':
            processor.load_xml(file.name)
        else:
            return f"Extensão '{ext}' não suportada.", ""

        gdf = processor.get_data()

        if gdf.empty:
            return "GeoDataFrame está vazio.", ""

        # Gera o mapa
        html_path = Visualizer.plot_folium(gdf)

        # Gera a tabela em HTML (removendo coluna geometry para ficar mais limpa)
        try:
            table_html = gdf.drop(columns='geometry', errors='ignore').to_html(classes='table table-striped', index=False)
        except:
            # fallback para texto simples
            table_html = gdf.to_string(index=False)

        return table_html, html_path

    except Exception as e:
        return f"Erro ao carregar arquivo: {str(e)}", ""

def open_map(file_path):
    if file_path and os.path.isfile(file_path):
        webbrowser.open("file://" + os.path.abspath(file_path))

with gr.Blocks() as demo:
    gr.Markdown("## Sistema Geoespacial Interativo")

    file_input = gr.File(label="Carregar arquivo CSV, JSON ou XML", file_types=['.csv', '.json', '.xml'])
    table_output = gr.HTML(label="Tabela de atributos")
    map_file = gr.Textbox(visible=False)  # Guarda o caminho do HTML gerado

    open_button = gr.Button("Abrir Mapa Interativo")

    file_input.change(fn=handle_file, inputs=file_input, outputs=[table_output, map_file])
    open_button.click(fn=open_map, inputs=map_file)

demo.launch()