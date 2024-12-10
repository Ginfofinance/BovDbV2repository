import sqlite3
import pandas as pd
import plotly.graph_objects as go

# Função para carregar os dados do banco de dados SQLite para o intervalo de datas especificado
def load_data_for_period(db_path, id_ticker, start_date, end_date):
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    
    # Query para obter os dados do ticker específico e do período definido
    query = f"""
    SELECT id_ticker, date, time, open, close, high, low, volume
    FROM price5
    WHERE id_ticker = {id_ticker} AND date BETWEEN '{start_date}' AND '{end_date}'
    """
    
    # Carregar os dados em um DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Fechar a conexão com o banco de dados
    conn.close()
    
    # Criar uma nova coluna de datetime combinando data e hora
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y-%m-%d %H:%M:%S')
    
    # Configurar datetime como índice
    df.set_index('datetime', inplace=True)
    
    return df

# Parâmetros do banco de dados e intervalo de datas
db_path = r"C:\bovdb\database\Database_define.db" #caminho para o banco de dadods
id_ticker = 3193
start_date = '2024-06-26'
end_date = '2024-06-26'

# Carregar os dados
df = load_data_for_period(db_path, id_ticker, start_date, end_date)

# Identificar os dias com negociações
dias_negociacoes = df['date'].unique()

# Função para plotar o gráfico de candles de 5 minutos para um dia específico
def plot_candlestick_for_day(df, day):
    # Filtrar os dados para o dia
    df_day = df[df['date'] == day]
    
    # Verificar se há dados disponíveis para o dia
    if df_day.empty:
        print(f"Nenhum dado disponível para o dia {day}.")
        return
    
    # Resample para janelas de 5 minutos (usando a forma recomendada)
    df_resampled = df_day.resample('5min').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Verificar se há dados após a reamostragem
    if df_resampled.empty:
        print(f"Nenhum dado após reamostragem para o dia {day}.")
        return
    
    # Criar o gráfico de candlestick usando Plotly
    fig = go.Figure(data=[go.Candlestick(x=df_resampled.index,
                                         open=df_resampled['open'],
                                         high=df_resampled['high'],
                                         low=df_resampled['low'],
                                         close=df_resampled['close'])])
    
    # Adicionar o título e os eixos
    fig.update_layout(title=f'Candlestick de 5 Minutos para o dia {day}',
                      xaxis_title='Hora',
                      yaxis_title='Preço')
    
    # Mostrar o gráfico
    fig.show()

# Plotar o gráfico para cada dia com negociações
for day in dias_negociacoes:
    print(f"Plotando gráfico para o dia: {day}")
    plot_candlestick_for_day(df, day)
