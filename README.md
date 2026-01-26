# Consultores CVM - Lista Colaborativa

Aplicacao web para gerenciar lista de consultores CVM com anotacoes compartilhadas entre a equipe.

## Setup

### 1. Criar projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta gratuita
2. Crie um novo projeto
3. Va em **SQL Editor** e execute:

```sql
CREATE TABLE consultores_pf (
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

CREATE INDEX idx_consultores_nome ON consultores_pf(nome);
CREATE INDEX idx_consultores_situacao ON consultores_pf(situacao);
```

4. Va em **Settings > API** e copie:
   - Project URL
   - anon/public key

### 2. Configurar ambiente local

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas credenciais do Supabase
```

### 3. Importar dados

```bash
# Instalar dependencias
pip install -r requirements.txt

# Importar consultores para o Supabase
python init_db.py
```

### 4. Rodar localmente

```bash
python app.py
# Acesse http://localhost:5000
```

## Deploy no Render

1. Suba o codigo para um repositorio GitHub
2. Em [render.com](https://render.com):
   - New > Web Service
   - Conecte ao repositorio
   - Configure as variaveis de ambiente:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
3. Deploy automatico!

## Funcionalidades

- Lista de consultores CVM (Pessoa Fisica) ativos
- Links para buscar no Google, LinkedIn e Instagram
- Marcar como "pesquisado"
- Adicionar observacoes
- Classificar como potencial (SIM/NAO)
- Filtros por situacao, pesquisado, potencial
- Exportar CSV
- **Dados compartilhados** entre todos os usuarios
