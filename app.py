#!/usr/bin/env python3
"""
API Flask para lista de consultores CVM com Supabase.
Permite múltiplos usuários compartilharem anotações.
"""

import os
from flask import Flask, jsonify, request, render_template, Response
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import csv
import io

load_dotenv()

app = Flask(__name__)

# Supabase config
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def get_supabase() -> Client:
    """Retorna cliente Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route('/')
def index():
    """Página principal com a lista de consultores."""
    return render_template('index.html')


@app.route('/api/consultores')
def listar_consultores():
    """Lista consultores com filtros opcionais."""
    supabase = get_supabase()

    # Parâmetros de filtro
    situacao = request.args.get('situacao', '')
    pesquisado = request.args.get('pesquisado', '')
    potencial = request.args.get('potencial', '')
    busca = request.args.get('busca', '')

    # Query base
    query = supabase.table('consultores_pf').select('*')

    # Aplicar filtros
    if situacao:
        query = query.ilike('situacao', f'%{situacao}%')

    if pesquisado == 'sim':
        query = query.eq('pesquisado', True)
    elif pesquisado == 'nao':
        query = query.eq('pesquisado', False)

    if potencial == 'sim':
        query = query.eq('potencial', 'sim')
    elif potencial == 'nao':
        query = query.eq('potencial', 'nao')
    elif potencial == 'indefinido':
        query = query.is_('potencial', 'null')

    if busca:
        query = query.ilike('nome', f'%{busca}%')

    # Ordenar por nome
    query = query.order('nome')

    result = query.execute()

    return jsonify({
        'consultores': result.data,
        'total': len(result.data)
    })


@app.route('/api/consultor/<int:consultor_id>', methods=['POST'])
def atualizar_consultor(consultor_id):
    """Atualiza anotações de um consultor."""
    supabase = get_supabase()
    data = request.json

    # Campos permitidos para atualização
    update_data = {}

    if 'pesquisado' in data:
        update_data['pesquisado'] = bool(data['pesquisado'])

    if 'observacoes' in data:
        update_data['observacoes'] = data['observacoes']

    if 'potencial' in data:
        # Aceita 'sim', 'nao' ou None/null
        potencial = data['potencial']
        if potencial in ['sim', 'nao']:
            update_data['potencial'] = potencial
        else:
            update_data['potencial'] = None

    if update_data:
        update_data['updated_at'] = datetime.utcnow().isoformat()

        result = supabase.table('consultores_pf').update(update_data).eq('id', consultor_id).execute()

        if result.data:
            return jsonify({'success': True, 'data': result.data[0]})

    return jsonify({'success': False, 'error': 'Nenhum dado para atualizar'}), 400


@app.route('/api/stats')
def estatisticas():
    """Retorna estatísticas gerais."""
    supabase = get_supabase()

    # Total
    total = supabase.table('consultores_pf').select('id', count='exact').execute()

    # Pesquisados
    pesquisados = supabase.table('consultores_pf').select('id', count='exact').eq('pesquisado', True).execute()

    # Potenciais SIM
    potenciais = supabase.table('consultores_pf').select('id', count='exact').eq('potencial', 'sim').execute()

    return jsonify({
        'total': total.count,
        'pesquisados': pesquisados.count,
        'potenciais': potenciais.count
    })


@app.route('/api/export/csv')
def exportar_csv():
    """Exporta todos consultores para CSV."""
    supabase = get_supabase()

    result = supabase.table('consultores_pf').select('*').order('nome').execute()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['Nome', 'Registro CVM', 'Situacao', 'Site', 'Pesquisado', 'Potencial', 'Observacoes'])

    # Data
    for c in result.data:
        writer.writerow([
            c.get('nome', ''),
            c.get('dt_reg', ''),
            c.get('situacao', ''),
            c.get('site_admin', ''),
            'Sim' if c.get('pesquisado') else 'Nao',
            c.get('potencial', '').upper() if c.get('potencial') else '',
            c.get('observacoes', '')
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=consultores_cvm.csv'}
    )


@app.route('/api/export/potenciais')
def exportar_potenciais():
    """Exporta apenas consultores marcados como potencial."""
    supabase = get_supabase()

    result = supabase.table('consultores_pf').select('*').eq('potencial', 'sim').order('nome').execute()

    if not result.data:
        return jsonify({'error': 'Nenhum consultor marcado como potencial'}), 404

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['Nome', 'Registro CVM', 'Site', 'Observacoes'])

    # Data
    for c in result.data:
        writer.writerow([
            c.get('nome', ''),
            c.get('dt_reg', ''),
            c.get('site_admin', ''),
            c.get('observacoes', '')
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=potenciais_adam.csv'}
    )


if __name__ == '__main__':
    app.run(debug=True, port=5001)
