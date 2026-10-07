import os
import re

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import requests
import tool_call as tc

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cities_data = []
sys_prompt = """Você é um assistente de análise de dados chamado Dars. Responda às perguntas do usuário com base nos dados disponíveis. Se precisar realizar uma ação, use a ferramenta apropriada.
Ferramentas disponíveis:
1. maior_metrica: Retorna as cidades com a maior métrica de desastres.
   Argumentos:
   - ano_inicio (int): Ano de início do período de análise.
   - ano_fim (int): Ano de fim do período de análise.
   - mes_inicio (int): Mês de início do período de análise.
   - mes_fim (int): Mês de fim do período de análise.
   - tipologia (int): Tipo de desastre a ser analisado (0 para todos).
   - metrica (str): Métrica a ser analisada (ex: "total_desastres").
   - k (int): Número de cidades a retornar.

2. menor_metrica: Retorna as cidades com a menor métrica de desastres.
    Argumentos:
    - ano_inicio (int): Ano de início do período de análise.
    - ano_fim (int): Ano de fim do período de análise.
    - mes_inicio (int): Mês de início do período de análise.
    - mes_fim (int): Mês de fim do período de análise.
    - tipologia (int): Tipo de desastre a ser analisado (0 para todos).
    - metrica (str): Métrica a ser analisada (ex: "total_desastres").
    - k (int): Número de cidades a retornar.

2. metrica_total: Retorna a soma de uma métrica de desastres para uma ou todas as cidades.
    Argumentos:
    - cidade (str): Nome da cidade a ser analisada (opcional, "0" para todas).
    - ano_inicio (int): Ano de início do período de análise.
    - ano_fim (int): Ano de fim do período de análise.
    - mes_inicio (int): Mês de início do período de análise.
    - mes_fim (int): Mês de fim do período de análise.
    - tipologia (int): Tipo de desastre a ser analisado (0 para todos).
    - metrica (str): Métrica a ser analisada (ex: "total_desastres").
    - k (int): Número de cidades a retornar.

3. criar_grafico: Cria um gráfico com base nos dados de desastres.
    Argumentos:
    - tipo_grafico (str): Tipo do gráfico a ser criado ("linha", "barra", "pizza", "dispersao", "histograma").
    - categorias (list): Lista de categorias para o gráfico (ex: ["Cidade A", "Cidade B"]).
    - valores (list): Lista de valores correspondentes às categorias (ex: [10, 20]).
    - x_values (list): Lista de valores para o eixo x (apenas para gráfico de dispersão).
    - y_values (list): Lista de valores para o eixo y (apenas para gráfico de dispersão).
    - bins (int): Número de bins para o histograma (apenas para gráfico de histograma).
    - title (str): Título do gráfico.

4. criar_relatorio: Cria um relatório em formato PDF com base nos dados de desastres.
    Argumentos:
    - nome_relatorio (str): Nome do arquivo PDF a ser criado.
    - conteudo (str html): Conteúdo do relatório em formato HTML.
    

Todas as ferramentas devem ser chamadas usando a seguinte sintaxe:
{
    "use_notice": "Descrição para que a ferramenta está sendo usada (e.g. Buscando dados de...)."
    "tool": "nome_da_ferramenta",
    "arguments": {
        ... argumentos específicos da ferramenta ...
    },
}

Sem "```json" ou "```tool_call" no início ou "```" no final. Apenas o JSON puro da ferramenta.

Se necessário, você também pode fazer várias chamadas em apenas uma resposta, mas cada chamada deve ser um JSON separado, seguindo a sintaxe acima.

Todas as métricas disponíveis:
* DH_MORTOS
* DH_FERIDOS
* DH_ENFERMOS
* DH_DESABRIGADOS
* DH_DESALOJADOS
* DH_DESAPARECIDOS
* DH_AFETADOS_SECA_ESTIAGEM
* DH_total_danos_humanos_diretos
* DH_OUTROS AFETADOS
* DM_Uni Habita Danificadas
* DM_Uni Habita Destruidas
* DM_Uni Habita Valor
* DM_Inst Saúde Danificadas
* DM_Inst Saúde Destruidas
* DM_Inst Saúde Valor
* DM_Inst Ensino Danificadas
* DM_Inst Ensino Destruidas
* DM_Inst Ensino Valor
* DM_Inst Serviços Danificadas
* DM_Inst Serviços Destruidas
* DM_Inst Serviços Valor
* DM_Inst Comuni Danificadas
* DM_Inst Comuni Destruidas
* DM_Inst Comuni Valor
* DM_Obras de Infra Danificadas
* DM_Obras de Infra Destruidas
* DM_Obras de Infra Valor
* DM_total_danos_materiais
* PEPL_Assis_méd e emergên(R$)
* PEPL_Abast de água pot(R$)
* PEPL_sist de esgotos sanit(R$)
* PEPL_Sis limp e rec lixo (R$)
* PEPL_Sis cont pragas (R$)
* PEPL_distrib energia (R$)
* PEPL_Telecomunicações (R$)
* PEPL_Tran loc/reg/l_curso (R$)
* PEPL_Distrib combustíveis(R$)
* PEPL_Segurança pública (R$)
* PEPL_Ensino (R$)
* PEPL_total_publico
* PEPR_Agricultura (R$)
* PEPR_Pecuária (R$)
* PEPR_Indústria (R$)
* PEPR_Comércio (R$)
* PEPR_Serviços (R$)
* PEPR_total_privado
* PE_PLePR

Tipologia dos desastres:
0 - Todos
1 - Alagamentos
2 - Enxurradas
3 - Erosão
4 - Estiagem e seca
5 - Granizo
6 - Incêndio Florestal
7 - Inundações
8 - Movimentos de Massa
9 - Chuvas Intensas
10 - Ondas de Frio
11 - Tornado
12 - Vendavais e Ciclones
13 - Chuvas Intensas
15 - Rompimento ou Colapsos de Barragens
14 - Outros
"""
chat_history = []
chat_history.append({"role": "system", "content": sys_prompt})

class MessageRequest(BaseModel):
    message: str

class CitiesRequest(BaseModel):
    cities: list

class PDFRequest(BaseModel):
    html: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat_endpoint(req: MessageRequest):
    return StreamingResponse(
        request_reply(chat_history, req.message),
        media_type="text/event-stream"
    )

@app.post("/init-cities")
def init_cities_endpoint(req: CitiesRequest):
    global cities_data
    cities_data = req.cities
    tc.cities_data = req.cities
    return {"status": "success", "message": "Cities data received", "count": len(cities_data)}

api_key = os.environ.get("OPENROUTER_API_KEY", "")

def request_reply(chat, message):
    full_reply = ""
    reply_buffer = ""
    tool_results = {}
    tool_count = 0
    sent_notice = False
    
    temp_chat = chat.copy()

    temp_chat.append({"role": "user", "content": message})
    chat.append({"role": "user", "content": message})

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "google/gemma-4-26b-a4b-it",
            "temperature": 0.1,
            "top_p": 0.95,
            "messages": temp_chat,
            "stream": True,
        }),
        stream=True
    )

    is_in_tool_call = False
    brace_count = 0;

    if response.status_code == 200:
        print("Streaming reply")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data_str = decoded_line[6:]

                    if data_str.strip() == '[DONE]':
                        break

                    try:
                        data = json.loads(data_str)
                        if not data.get('choices'):
                            continue

                        delta = data['choices'][0]['delta']
                        content = delta.get('content', '')

                        if content:
                            reply_buffer += content
                            full_reply += content

                            if "{" in reply_buffer and is_in_tool_call == False:
                                sentence, reply_buffer = reply_buffer.split("{", 1)
                                reply_buffer = "{" + reply_buffer
                                brace_count += reply_buffer.count('{')
                                brace_count -= reply_buffer.count('}')
                                is_in_tool_call = True
                                sent_notice = False
                                yield sentence

                            elif is_in_tool_call is True:
                                brace_count = reply_buffer.count('{') - reply_buffer.count('}')

                                notice_match = re.search(r'"use_notice"\s*:\s*"([^"]*)"', reply_buffer)
                                if notice_match and sent_notice == False:
                                    current_notice = notice_match.group(1)
                                    if current_notice.strip():
                                        yield f"<div class='chat-tool-card'>🔍 {current_notice}...</div>"
                                        sent_notice = True

                                if brace_count == 0:
                                    close_index = reply_buffer.rfind('}')
                                    tool_call = reply_buffer[:close_index + 1]
                                    reply_buffer = reply_buffer[close_index + 1:]
                                    image = tc.manage_tool_call(tool_call, tool_results)
                                    brace_count = 0
                                    completed_card = "<div class='chat-tool-card chat-tool-complete'>✅ Análise completa</div>"
                                    yield completed_card
                                    yield reply_buffer
                                    if image:
                                        yield image
                                    is_in_tool_call = False
                                    reply_buffer = ""
                                    continue

                            if is_in_tool_call is False:
                                yield content

                    except json.JSONDecodeError:
                        continue
    else:
        print(f"An error occured during text generation: {response.status_code}")
        print(temp_chat)

    chat.append({"role": "assistant", "content": full_reply})
        
    if tool_results:
        print(f"TOOL RESULTS:\n {tool_results}")
        tool_notice = f"O resultado retornado para as ferramentas é:\n{tool_results}"
        yield from request_reply(chat, tool_notice)