#!/usr/bin/env python3
"""
Script para popular o Supabase com dados dos consultores CVM.
Execute uma vez para importar os dados.

Uso:
    1. Configure as variáveis de ambiente ou crie um arquivo .env:
       SUPABASE_URL=https://xxx.supabase.co
       SUPABASE_KEY=eyJhbGci...

    2. Execute:
       python init_db.py
"""

import os
import csv
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Caminho para o CSV fonte
CSV_PATH = Path(__file__).parent.parent / 'cvm_consultores' / 'cad_consultor_vlmob_pf.csv'


def criar_tabela_sql():
    """Retorna o SQL para criar a tabela no Supabase."""
    return """
-- Execute este SQL no Supabase SQL Editor:

CREATE TABLE IF NOT EXISTS consultores_pf (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    dt_reg TEXT,
    situacao TEXT,
    site_admin TEXT,
    pesquisado BOOLEAN DEFAULT FALSE,
    observacoes TEXT,
    potencial TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Criar índice para busca por nome
CREATE INDEX IF NOT EXISTS idx_consultores_nome ON consultores_pf(nome);

-- Criar índice para filtro por situação
CREATE INDEX IF NOT EXISTS idx_consultores_situacao ON consultores_pf(situacao);

-- Habilitar RLS (Row Level Security) - opcional
-- ALTER TABLE consultores_pf ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura e escrita pública (para este caso de uso)
-- CREATE POLICY "Allow all" ON consultores_pf FOR ALL USING (true);
"""


def carregar_csv():
    """Carrega consultores do CSV."""
    consultores = []

    with open(CSV_PATH, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            # Filtrar apenas ativos
            if row.get('SIT', '') == 'EM FUNCIONAMENTO NORMAL':
                consultores.append({
                    'nome': row.get('NOME', '').strip(),
                    'dt_reg': row.get('DT_REG', ''),
                    'situacao': row.get('SIT', ''),
                    'site_admin': row.get('SITE_ADMIN', ''),
                    'pesquisado': False,
                    'observacoes': None,
                    'potencial': None
                })

    return consultores


def popular_supabase(consultores: list):
    """Insere consultores no Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERRO: Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env")
        print("\nExemplo de .env:")
        print("SUPABASE_URL=https://xxx.supabase.co")
        print("SUPABASE_KEY=eyJhbGci...")
        return False

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print(f"Inserindo {len(consultores)} consultores...")

    # Inserir em lotes de 100 para evitar timeout
    batch_size = 100
    for i in range(0, len(consultores), batch_size):
        batch = consultores[i:i + batch_size]
        result = supabase.table('consultores_pf').insert(batch).execute()
        print(f"  Lote {i // batch_size + 1}: {len(batch)} registros inseridos")

    print(f"\nTotal inserido: {len(consultores)} consultores")
    return True


def verificar_tabela():
    """Verifica se a tabela existe e retorna contagem."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        result = supabase.table('consultores_pf').select('id', count='exact').limit(1).execute()
        return result.count
    except Exception as e:
        print(f"Erro ao verificar tabela: {e}")
        return None


def main():
    print("=" * 60)
    print("IMPORTAR CONSULTORES CVM PARA SUPABASE")
    print("=" * 60)

    # Verificar se tabela já tem dados
    count = verificar_tabela()

    if count is None:
        print("\n1. Primeiro, crie a tabela no Supabase SQL Editor:")
        print("-" * 40)
        print(criar_tabela_sql())
        print("-" * 40)
        print("\n2. Depois, execute este script novamente.")
        return

    if count > 0:
        print(f"\nA tabela já contém {count} registros.")
        resp = input("Deseja limpar e reimportar? (s/N): ").strip().lower()
        if resp != 's':
            print("Operação cancelada.")
            return

        # Limpar tabela
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase.table('consultores_pf').delete().neq('id', 0).execute()
        print("Tabela limpa.")

    # Carregar CSV
    print(f"\nCarregando CSV: {CSV_PATH}")
    consultores = carregar_csv()
    print(f"Consultores ativos encontrados: {len(consultores)}")

    # Popular Supabase
    if popular_supabase(consultores):
        print("\nImportação concluída com sucesso!")
    else:
        print("\nErro na importação.")


if __name__ == '__main__':
    main()
