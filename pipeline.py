import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# 1. Carregar
df = pd.read_csv(
    "data/raw/samp-balanco.csv",
    sep=";",
    encoding="latin1",
)

df_pe = df[df['NomAgente'] == 'NEOENERGIA PE - COMPANHIA ENERGETICA DE PERNAMBUCO'].copy()


df_pe = df_pe.dropna(subset=['VlrEnergia', 'AnoReferenciaBalanco', 'MesReferenciaBalanco'])
df_pe['VlrEnergia'] = pd.to_numeric(df_pe['VlrEnergia'], errors='coerce')
df_pe = df_pe.dropna(subset=['VlrEnergia'])


df_pe['data'] = pd.to_datetime(
    df_pe['AnoReferenciaBalanco'].astype(str) + '-' +
    df_pe['MesReferenciaBalanco'].astype(str).str.zfill(2) + '-01'
)


df_final = df_pe[[
    'data',
    'AnoReferenciaBalanco',
    'MesReferenciaBalanco',
    'DscModalidadeBalanco',
    'DscFluxoEnergia',
    'DscDetalheBalanco',
    'VlrEnergia'
]].rename(columns={
    'AnoReferenciaBalanco': 'ano',
    'MesReferenciaBalanco': 'mes',
    'DscModalidadeBalanco': 'modalidade',
    'DscFluxoEnergia': 'fluxo_energia',
    'DscDetalheBalanco': 'detalhe',
    'VlrEnergia': 'valor_kwh'
})

print("Shape final:", df_final.shape)
print("\nTipos:", df_final.dtypes)
print("\nAmostra:")
print(df_final.head(5))


df_final.to_csv("data/samp_pe_limpo.csv", index=False)
print("\nArquivo salvo em data/samp_pe_limpo.csv")

# 7. Carregar no PostgreSQL
engine = create_engine(
    "postgresql+psycopg2://",
    creator=lambda: psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="energia_pe",
        user="postgres",
        password="1227"
    )
)

df_final.to_sql('consumo_energia_pe', engine, if_exists='replace', index=False)
print("\nDados carregados no PostgreSQL com sucesso!")
print(f"Total de registros inseridos: {len(df_final)}")