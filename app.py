from flask import Flask, render_template, request
import pandas as pd
import io

app = Flask(__name__)

def obter_fator_anuidade(idade, sexo):
    tabela_fatores_str = """idade,sexo,fator_anuidade
50,M,23.55
51,M,22.98
52,M,22.41
53,M,21.84
54,M,21.27
55,M,20.70
56,M,20.13
57,M,19.56
58,M,18.99
59,M,18.42
60,M,17.85
61,M,17.28
62,M,16.71
63,M,16.14
64,M,15.57
65,M,15.00
50,F,26.50
51,F,25.95
52,F,25.40
53,F,24.85
54,F,24.30
55,F,23.75
56,F,23.20
57,F,22.65
58,F,22.10
59,F,21.55
60,F,21.00
61,F,20.45
62,F,19.90
63,F,19.35
64,F,18.80
65,F,18.25
"""
    # Usando io.StringIO para ler a string como se fosse um arquivo
    tabela_df = pd.read_csv(io.StringIO(tabela_fatores_str))
    
    fator = tabela_df[(tabela_df['idade'] == idade) & (tabela_df['sexo'] == sexo)]
    
    if not fator.empty:
        return fator.iloc[0]['fator_anuidade']
    else:
        # Retorna um valor padrão ou lança um erro se a idade/sexo não for encontrado
        # Para simplicidade, vamos retornar um valor médio ou 0.
        # Numa aplicação real, o tratamento de erro seria mais robusto.
        return 20.0 # Valor padrão para evitar erros

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simular', methods=['POST'])
def simular():
    try:
        saldo_conta = float(request.form['saldo_conta'])
        idade_participante = int(request.form['idade_participante'])
        sexo_participante = request.form['sexo_participante']
        
        # Lógica para o beneficiário
        idade_beneficiario_str = request.form.get('idade_beneficiario')
        sexo_beneficiario = request.form.get('sexo_beneficiario')

        aa = obter_fator_anuidade(idade_participante, sexo_participante)
        ap = 0.0

        if idade_beneficiario_str and sexo_beneficiario:
            idade_beneficiario = int(idade_beneficiario_str)
            ap = obter_fator_anuidade(idade_beneficiario, sexo_beneficiario)

        # Fórmula do Regulamento: RMA = SC / (13 * (AA + AP))
        # Adicionado um tratamento para evitar divisão por zero
        denominador = 13 * (aa + ap)
        if denominador == 0:
            resultado = "Erro: Fatores de anuidade resultaram em zero. Verifique os dados de entrada."
            return render_template('index.html', resultado=resultado)
            
        rma = saldo_conta / denominador
        
        resultado = f"R$ {rma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return render_template('index.html', resultado=resultado, form_data=request.form)

    except (ValueError, TypeError) as e:
        resultado = f"Erro nos dados de entrada. Por favor, verifique os valores. Detalhe: {e}"
        return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
