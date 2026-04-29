import json
import pandas as pd
import unicodedata
import re

# 1. Lista (array) dos municípios do RS conforme as fontes (Censo 2022)
# Esta lista contém os nomes extraídos das fontes, do mais populoso ao menos populoso.
municipios_alvo = [
    "Porto Alegre", "Caxias do Sul", "Canoas", "Pelotas", "Santa Maria", "Gravataí", "Novo Hamburgo", "Viamão", "São Leopoldo", "Passo Fundo", # 1-10
    "Rio Grande", "Alvorada", "Cachoeirinha", "Santa Cruz do Sul", "Sapucaia do Sul", "Bento Gonçalves", "Bagé", "Uruguaiana", "Erechim", "Lajeado", # 11-20
    "Guaíba", "Ijuí", "Santana do Livramento", "Cachoeira do Sul", "Santa Rosa", "Santo Ângelo", "Esteio", "Sapiranga", "Alegrete", "Farroupilha", # 21-30
    "Venâncio Aires", "Vacaria", "Montenegro", "Capão da Canoa", "Campo Bom", "Camaquã", "Carazinho", "São Borja", "Cruz Alta", "São Gabriel", # 31-40
    "Tramandaí", "Taquara", "Parobé", "Canguçu", "Canela", "Santiago", "Estância Velha", "Osório", "Marau", "Panambi", # 41-50
    "Santo Antônio da Patrulha", "São Lourenço do Sul", "Torres", "Gramado", "Eldorado do Sul", "Dom Pedrito", "Rosário do Sul", "Itaqui", "Charqueadas", "São Luiz Gonzaga", # 51-60
    "Rio Pardo", "Garibaldi", "Portão", "Palmeira das Missões", "Igrejinha", "Teutônia", "Frederico Westphalen", "Caçapava do Sul", "Estrela", "Santa Vitória do Palmar", # 61-70
    "Flores da Cunha", "Dois Irmãos", "Carlos Barbosa", "Soledade", "Nova Santa Rita", "Candelária", "Lagoa Vermelha", "Triunfo", "Imbé", "Vera Cruz", # 71-80
    "Jaguarão", "Capão do Leão", "Nova Prata", "São José do Norte", "Três Passos", "Guaporé", "Taquari", "Três de Maio", "Tapejara", "São Sebastião do Caí", # 81-90
    "Três Coroas", "Veranópolis", "Encruzilhada do Sul", "Quaraí", "Nova Petrópolis", "Ivoti", "Encantado", "Sarandi", "Arroio do Meio", "São Francisco de Paula", # 91-100
    "Ibirubá", "Rolante", "São Sepé", "São Marcos", "São Jerônimo", "Nova Hartz", "Tupanciretã", "Butiá", "Horizontina", "Júlio de Castilhos", # 101-110
    "Não-Me-Toque", "São Francisco de Assis", "Arroio Grande", "Piratini", "Cidreira", "Serafina Corrêa", "Getúlio Vargas", "Xangri-lá", "Sananduva", "Agudo", # 111-120
    "Giruá", "São Pedro do Sul", "Santo Cristo", "Espumoso", "Balneário Pinhal", "Restinga Sêca", "Tapes", "Arroio dos Ratos", "Tenente Portela", "Sobradinho", # 121-130
    "Santo Augusto", "Feliz", "Nonoai", "Cerro Largo", "Bom Princípio", "Dom Feliciano", "Antônio Prado", "Crissiumal", "Palmares do Sul", "Bom Retiro do Sul", # 131-140
    "Barra do Ribeiro", "Mostardas", "Arroio do Tigre", "Seberi", "Cruzeiro do Sul", "Pinheiro Machado", "Bom Jesus", "Capela de Santana", "Cacequi", "Arroio do Sal", # 141-150
    "Três Cachoeiras", "Candiota", "Tapera", "Jaguari", "Roca Sales", "Planalto", "Constantina", "Arvorezinha", "Santo Antônio das Missões", "Terra de Areia", # 151-160
    "Pantano Grande", "Salto do Jacuí", "Porto Xavier", "Ronda Alta", "Redentora", "Nova Bassano", "Vale do Sol", "Fontoura Xavier", "Chapada", "Casca", # 161-170
    "Cerro Grande do Sul", "Barros Cassal", "Entre-Ijuís", "Catuípe", "Sinimbu", "Araricá", "Tuparendi", "Santa Bárbara do Sul", "São Vicente do Sul", "Paverama", # 171-180
    "Palmitinho", "Glorinha", "Ametista do Sul", "General Câmara", "Trindade do Sul", "Minas do Leão", "Pedro Osório", "Iraí", "Maquiné", "Guarani das Missões", # 181-190
    "Caraá", "Cristal", "Paraí", "Jóia", "Lavras do Sul", "Augusto Pestana", "Barão de Cotegipe", "Alpestre", "São Miguel das Missões", "Santana da Boa Vista", # 191-200
    "Boa Vista do Buricá", "Santa Clara do Sul", "Salvador do Sul", "São José do Ouro", "Manoel Viana", "Erval Seco", "Ibiraiaras", "Ajuricaba", "Faxinal do Soturno", "Rodeio Bonito", # 201-210
    "Roque Gonzales", "Paraíso do Sul", "Aratiba", "Barão", "Independência", "Formigueiro", "Condor", "Cambará do Sul", "Santa Maria do Herval", "Cândido Godói", # 211-220
    "Chuí", "Boqueirão do Leão", "Lindolfo Collor", "Herval", "Coronel Bicaco", "Alecrim", "Vale Real", "Morro Redondo", "Morro Reuter", "Passo do Sobrado", # 221-230
    "Segredo", "Hulha Negra", "Anta Gorda", "Bossoroca", "Barão do Triunfo", "Campina das Missões", "Sertão Santana", "São Paulo das Missões", "Cerrito", "Machadinho", # 231-240
    "Gaurama", "Nova Palma", "Estação", "Itaara", "Tucunduva", "Sertão", "São Martinho", "Harmonia", "Picada Café", "Lagoão", # 241-250
    "Progresso", "Ipê", "Amaral Ferrador", "Sentinela do Sul", "Campinas do Sul", "Tavares", "Tiradentes do Sul", "São Nicolau", "Selbach", "Tupandi", # 251-260
    "Rondinha", "Campo Novo", "Brochier", "Nova Araçá", "Erval Grande", "Nova Esperança do Sul", "Mato Leitão", "Caiçara", "Barracão", "Liberato Salzano", # 261-270
    "Viadutos", "Três Palmeiras", "Caibaté", "Mata", "Humaitá", "Vicente Dutra", "Cacique Doble", "Muçum", "Chuvisca", "Pinheirinho do Vale", # 271-280
    "Ibiaçá", "Fortaleza dos Valos", "Riozinho", "Doutor Maurício Cardoso", "São João da Urtiga", "Tabaí", "São José do Hortêncio", "Miraguaí", "Maçambará", "Vila Maria", # 281-290
    "Porto Lucena", "David Canabarro", "Marcelino Ramos", "Pareci Novo", "Fazenda Vilanova", "Novo Barreiro", "Barra do Quaraí", "Maximiliano de Almeida", "São José dos Ausentes", "Aceguá", # 291-300
    "Ilópolis", "Ciríaco", "Arambaré", "Capivari do Sul", "Passa-Sete", "Marques de Souza", "Mariana Pimentel", "Chiapetta", "Água Santa", "Quinze de Novembro", # 301-310
    "Vila Nova do Sul", "Cotiporã", "Pinhal Grande", "Cerro Branco", "Jaboticaba", "Putinga", "Pejuçara", "Ibarama", "Ibirapuitã", "Jaquirana", # 311-320
    "Tunas", "Alegria", "Vila Flores", "Paim Filho", "Campos Borges", "Novo Cabrais", "São Pedro da Serra", "Nova Roma do Sul", "Turuçu", "Severiano de Almeida", # 321-330
    "Áurea", "Jari", "Jacutinga", "Gramado Xavier", "Pontão", "Braga", "Tio Hugo", "São Valentim", "Vitória das Missões", "Colorado", # 331-340
    "Campestre da Serra", "Esperança do Sul", "Itatiba do Sul", "Novo Machado", "Esmeralda", "Monte Alegre dos Campos", "Nova Alvorada", "Barra do Guarita", "Vale Verde", "Mampituba", # 341-350
    "Capão do Cipó", "Taquaruçu do Sul", "Westfália", "Dois Lajeados", "Imigrante", "Dona Francisca", "Presidente Lucena", "Alto Feliz", "Morrinhos do Sul", "Estrela Velha", # 351-360
    "São Pedro do Butiá", "Nova Candelária", "Erebango", "Nova Bréscia", "Ernestina", "Caseiros", "Itacurubi", "Camargo", "Pinhal", "Capitão", # 361-370
    "São Jorge", "Muitos Capões", "Salvador das Missões", "Rio dos Índios", "Coronel Barros", "São Martinho da Serra", "Dilermando de Aguiar", "Vista Gaúcha", "Victor Graeff", "Boa Vista do Sul", # 371-380
    "Charrua", "Três Forquilhas", "Mormaço", "São Domingos do Sul", "Derrubadas", "Pinto Bandeira", "Centenário", "Sede Nova", "Cristal do Sul", "Garruchos", # 381-390
    "Entre Rios do Sul", "Senador Salgado Filho", "Coxilha", "Vista Alegre", "São João do Polêsine", "Itati", "Eugênio de Castro", "Lajeado do Bugre", "Arroio do Padre", "Santa Margarida do Sul", # 391-400
    "Três Arroios", "Saldanha Marinho", "Fagundes Varela", "Dom Pedro de Alcântara", "Monte Belo do Sul", "Toropi", "Mato Castelhano", "São Valério do Sul", "Herveiras", "Faxinalzinho", # 401-410
    "Dezesseis de Novembro", "Quevedos", "Barra Funda", "Sagrada Família", "Maratá", "Colinas", "São José do Inhacorá", "Forquetinha", "Cerro Grande", "São José das Missões", # 411-420
    "Santo Expedito do Sul", "Nova Pádua", "Rolador", "São José do Sul", "Boa Vista do Incra", "Pirapó", "Lagoa Bonita do Sul", "São Vendelino", "Pinhal da Serra", "Boa Vista do Cadeado", # 421-430
    "Coqueiros do Sul", "São Valentim do Sul", "Poço das Antas", "Nova Ramada", "Travesseiro", "Bozano", "Silveira Martins", "Novo Tiradentes", "Paulo Bento", "Porto Mauá", # 431-440
    "Bom Progresso", "Santo Antônio do Palma", "Dois Irmãos das Missões", "Santo Antônio do Planalto", "Benjamin Constant do Sul", "Vila Lângaro", "Pedras Altas", "Nova Boa Vista", "Jacuizinho", "Protásio Alves", # 441-450
    "Gramado dos Loureiros", "Inhacorá", "Vanini", "Unistalda", "Ubiretama", "Almirante Tamandaré do Sul", "Sério", "Itapuca", "Boa Vista das Missões", "Nicolau Vergueiro", # 451-460
    "Ivorá", "São José do Herval", "Doutor Ricardo", "Mariano Moro", "Sete de Setembro", "Vespasiano Corrêa", "Alto Alegre", "Relvado", "Mato Queimado", "São Pedro das Missões", # 461-470
    "Gentil", "Pouso Novo", "Lagoa dos Três Cantos", "Capão Bonito do Sul", "Muliterno", "Ipiranga do Sul", "Barra do Rio Azul", "Linha Nova", "Santa Cecília do Sul", "Floriano Peixoto", # 471-480
    "Canudos do Vale", "Novo Xingu", "Cruzaltense", "Coronel Pilar", "Vista Alegre do Prata", "Ponte Preta", "Porto Vera Cruz", "Quatro Irmãos", "Santa Tereza", "Montauri", # 481-490
    "Guabiju", "Tupanci do Sul", "Carlos Gomes", "Engenho Velho", "Coqueiro Baixo", "União da Serra", "André da Rocha" # 491-497
]

def normalize_name(nome):
    if not isinstance(nome, str):
        return ""

    nome = nome.strip().lower()
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    return nome

def normalize_json_attr_name(text):
    # Remove anything inside parentheses (including the parentheses)
    text = re.sub(r"\s*\([^)]*\)", "", text)

    # Remove accents
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    
    # Replace spaces with underscores
    text = text.replace(' ', '_')

    return text

def filtrar_municipios(input_file, output_file, lista_nomes):
    df = pd.read_excel(f"./data/Atlas_RS_short.xlsx", sheet_name="Atlas Valores Corrigidos")
    df["nome_norm"] = df["Nome_Municipio"].apply(normalize_name)

    campos = [
        "DH_MORTOS",
        "DH_FERIDOS",
        "DH_ENFERMOS",
        "DH_DESABRIGADOS",
        "DH_DESALOJADOS",
        "DH_DESAPARECIDOS",
        "DH_AFETADOS_SECA_ESTIAGEM",
        "DH_total_danos_humanos_diretos",
        "DH_OUTROS AFETADOS",

        "DM_Uni Habita Danificadas",
        "DM_Uni Habita Destruidas",
        "DM_Uni Habita Valor",
        "DM_Inst Saúde Danificadas",
        "DM_Inst Saúde Destruidas",
        "DM_Inst Saúde Valor",
        "DM_Inst Ensino Danificadas",
        "DM_Inst Ensino Destruidas",
        "DM_Inst Ensino Valor",
        "DM_Inst Serviços Danificadas",
        "DM_Inst Serviços Destruidas",
        "DM_Inst Serviços Valor",
        "DM_Inst Comuni Danificadas",
        "DM_Inst Comuni Destruidas",
        "DM_Inst Comuni Valor",
        "DM_Obras de Infra Danificadas",
        "DM_Obras de Infra Destruidas",
        "DM_Obras de Infra Valor",
        "DM_total_danos_materiais",

        "PEPL_Assis_méd e emergên(R$)",
        "PEPL_Abast de água pot(R$)",
        "PEPL_sist de esgotos sanit(R$)",
        "PEPL_Sis limp e rec lixo (R$)",
        "PEPL_Sis cont pragas (R$)",
        "PEPL_distrib energia (R$)",
        "PEPL_Telecomunicações (R$)",
        "PEPL_Tran loc/reg/l_curso (R$)",
        "PEPL_Distrib combustíveis(R$)",
        "PEPL_Segurança pública (R$)",
        "PEPL_Ensino (R$)",
        "PEPL_total_publico",

        "PEPR_Agricultura (R$)",
        "PEPR_Pecuária (R$)",
        "PEPR_Indústria (R$)",
        "PEPR_Comércio (R$)",
        "PEPR_Serviços (R$)",
        "PEPR_total_privado",

        "PE_PLePR",
    ]

    dados_agrupados = df.groupby("nome_norm")[campos].sum()
    
    try:
        # Carrega o JSON completo (baixado do GitHub)
        with open(input_file, 'r', encoding="utf-8-sig") as f:
            dados_completos = json.load(f)
        
        municipios_filtrados = []
        for municipio in dados_completos:
            if municipio["codigo_uf"] == 43:
                nome_norm = normalize_name(municipio["nome"])
                for campo in campos:
                    municipio[normalize_json_attr_name(campo)] = int(dados_agrupados.get(campo, {}).get(nome_norm, 0))
                municipios_filtrados.append(municipio)
        
        # Salva o novo arquivo JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(municipios_filtrados, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso! {len(municipios_filtrados)} municípios foram salvos em '{output_file}'.")

    except FileNotFoundError:
        print("Erro: O arquivo 'municipios.json' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def main():
    filtrar_municipios('data/municipios.json', 'data/municipios_rs_filtrados.json', municipios_alvo)

if __name__ == "__main__":
    main()