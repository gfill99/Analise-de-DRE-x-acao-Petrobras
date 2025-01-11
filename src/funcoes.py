import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

def filtrar_tabela(tabela):
    # Verificando valores da primeira linha do dataframe dentro de uma lista:
    novas_colunas = tabela.iloc[0].tolist()
    novas_colunas[0] =  "Descricao"
    novas_colunas

    # reatribuindo a lista de colunas do tabela1.columns para os valores da primeira linha do dataframe:
    tabela.columns =  novas_colunas

    # Reatribuindo, lendo o Dataframe a partir da segunda linha:
    tabela = tabela[1:]

    # Transformar todo o texto da coluna 'Descricao' para minúsculas espaços extras e entre palavras
    tabela['Descricao'] = tabela['Descricao'].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)

    #filtrando da antipenultima linha pra cima
    dados_filtrados = tabela.iloc[:-3]

    colunas_calculadas = ['lucro bruto', 
                    'lucro antes do resultado financeiro', 
                    'participações e impostos',
                    'resultado financeiro líquido',
                    'lucro (prejuízo) antes dos tributos sobre o lucro',
                    'lucro (prejuízo) líquido do período'
                    ]
    
    # FILTRANDO no dataframe na coluna descrição todos os valores que são diferentes da lista 
    dados_filtrados = dados_filtrados[~dados_filtrados['Descricao'].isin(colunas_calculadas)].reset_index().drop(columns='index')

    return dados_filtrados, tabela, novas_colunas


def funcao_lucro_liquido(tabela: pd.DataFrame, novas_colunas:list):
    # Filtrar apenas a linha que contém "lucro (prejuízo) líquido do período"
    dados_filtrados = tabela[tabela['Descricao'].str.contains(r'lucro \(prejuízo\) líquido do período', case=False, na=False)]

    # Função para limpar e converter os valores monetários
    def limpar_valor(valor):
        return pd.to_numeric(valor, errors='coerce')  # Converte para número

    # Calcular o lucro líquido por trimestre
    lucro_liquido = {}
    for trimestre in novas_colunas[1:]:
        lucro_liquido[trimestre] = limpar_valor(dados_filtrados[trimestre].values[0])

    # Exibir o resultado
    print("Lucro Líquido por Trimestre:", lucro_liquido)

    return lucro_liquido


def calcular_preco_medio(colunas:list):
    # Baixar dados históricos da ação PETR3.SA
    acao = yf.Ticker("PETR3.SA")

    # Obter dados históricos
    dados_historicos = acao.history(period="2y")

    # Adicionar coluna de trimestre
    dados_historicos['Trimestre'] = dados_historicos.index.to_period('Q')

    # Calcular preço médio de fechamento por trimestre
    preco_medio_trimestral = dados_historicos.groupby('Trimestre')['Close'].mean().reset_index()

    # Converter 'Trimestre' para string e formatar
    preco_medio_trimestral['Trimestre'] = preco_medio_trimestral['Trimestre'].astype(str)
    preco_medio_trimestral['TRIANO'] = preco_medio_trimestral['Trimestre'].str[-1] + 'T' + preco_medio_trimestral['Trimestre'].str[2:4]

    # Filtrar os trimestres desejados e converter para lista
    preco_medio_filtrado = preco_medio_trimestral[preco_medio_trimestral['TRIANO'].isin(colunas)]['Close'].tolist()

    return preco_medio_filtrado


def tabela_lucro_liquido_trimestre(colunas):
    # Dados de lucro líquido por trimestre
    lucro_liquido = {
        "1º Trimestre de 2023": colunas[0],
        "2º Trimestre de 2023": colunas[1],
        "1º Trimestre de 2024": colunas[2]
    }

    # Extrair trimestres e valores
    trimestres = list(lucro_liquido.keys()) 
    lucros = list(lucro_liquido.values())

    # Mapear os trimestres para um formato descritivo
    trimestres_descritivos = [f"Resultado de {t}" for t in trimestres]

    # Criar o gráfico de linha
    plt.figure(figsize=(10, 6))
    plt.plot(trimestres_descritivos, lucros, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)

    # Adicionar título e rótulos aos eixos
    plt.title('Lucro Líquido por Trimestre', fontsize=14)
    plt.xlabel('Trimestre', fontsize=12)
    plt.ylabel('Lucro Líquido (R$)', fontsize=12)

    # Adicionar grade e exibir o gráfico
    plt.grid(True)
    plt.show()


def comparacao_lucro_acoes(lucro:list, colunas:list):
    # Dados
    trimestres = ["1º Trimestre de 2023", "4º Trimestre de 2023", "1º Trimestre de 2024"]
    lucro_liquido = lucro # Em milhões de reais
    preco_medio_acoes = calcular_preco_medio(colunas[1:])
    preco_medio_acoes = preco_medio_acoes.tolist() if isinstance(preco_medio_acoes, np.ndarray) else preco_medio_acoes

    # Criar figura e eixo
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Eixo Y para lucro líquido
    color = 'tab:blue'
    ax1.set_xlabel('Trimestres')
    ax1.set_ylabel('Lucro Líquido (em milhões de R$)', color=color)
    ax1.plot(trimestres, lucro_liquido, marker='o', color=color, label="Lucro Líquido", linewidth=2, markersize=8)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc="upper left")

    # Eixo Y para preço médio das ações
    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Preço Médio das Ações (R$)', color=color)
    ax2.plot(trimestres, preco_medio_acoes, marker='s', linestyle='--', color=color, label="Preço Médio", linewidth=2, markersize=8)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc="upper right")

    # Título e layout
    plt.title("Lucro Líquido vs. Preço Médio das Ações por Trimestre", fontsize=14, pad=20)
    fig.tight_layout()
    plt.show()