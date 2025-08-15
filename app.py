from flask import Flask, render_template, request
import pandas as pd
import io

app = Flask(__name__)

def obter_fator_anuidade(idade, sexo):
    """
    Utiliza a tabela atuarial BR-EMSsb-V.2015 (suavizada em 10%) para obter o fator de anuidade.
    Os fatores foram pré-calculados considerando uma taxa de juros atuarial de 4,5% a.a.
    """
    tabela_fatores_str = """idade,sexo,fator_anuidade
50,M,16.45
51,M,16.08
52,M,15.71
53,M,15.33
54,M,14.95
55,M,14.56
56,M,14.17
57,M,13.78
58,M,13.38
59,M,12.98
60,M,12.58
61,M,12.17
62,M,11.76
63,M,11.35
64,M,10.94
65,M,10.53
66,M,10.12
67,M,9.71
68,M,9.31
69,M,8.91
70,M,8.51
50,F,18.97
51,F,18.57
52,F,18.17
53,F,17.77
54,F,17.36
55,F,16.95
56,F,16.54
57,F,16.13
58,F,15.71
59,F,15.29
60,F,14.87
61,F,14.45
62,F,14.02
63,F,13.59
64,F,13.16
65,F,12.73
66,F,12.30
67,F,11.86
68,F,11.43
69,F,11.00
70,F,10.57
"""
    tabela_df = pd.read_csv(io.StringIO(tabela_fatores_str))
    
    fator = tabela_df[(tabela_df['idade'] == idade) & (tabela_df['sexo'] == sexo)]
    
    if not fator.empty:
        return fator.iloc[0]['fator_anuidade']
    else:
        # Retorna 0 ou lança um erro se a idade/sexo não for encontrado.
        # Retornar 0 é mais seguro para evitar cálculos inesperados.
        return 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simular', methods=['POST'])
def simular():
    try:
        saldo_conta = float(request.form['saldo_conta'])
        idade_participante = int(request.form['idade_participante'])
        sexo_participante = request.form['sexo_participante']
        
        idade_beneficiario_str = request.form.get('idade_beneficiario')
        sexo_beneficiario = request.form.get('sexo_beneficiario')

        aa = obter_fator_anuidade(idade_participante, sexo_participante)
        ap = 0.0

        # Validação para garantir que o participante foi encontrado na tábua
        if aa == 0.0:
            resultado = f"Erro: Idade ({idade_participante}) ou sexo ({sexo_participante}) do participante fora dos parâmetros da tábua atuarial."
            return render_template('index.html', resultado=resultado, form_data=request.form)

        if idade_beneficiario_str and sexo_beneficiario:
            idade_beneficiario = int(idade_beneficiario_str)
            ap = obter_fator_anuidade(idade_beneficiario, sexo_beneficiario)
            if ap == 0.0:
                resultado = f"Erro: Idade ({idade_beneficiario}) ou sexo ({sexo_beneficiario}) do beneficiário fora dos parâmetros da tábua atuarial."
                return render_template('index.html', resultado=resultado, form_data=request.form)

        denominador = 13 * (aa + ap)
        if denominador == 0:
            resultado = "Erro: Fatores de anuidade resultaram em zero. Verifique os dados de entrada."
            return render_template('index.html', resultado=resultado, form_data=request.form)
            
        rma = saldo_conta / denominador
        
        # Formata o resultado para o padrão brasileiro (ex: R$ 1.234,56)
        resultado_formatado = f"R$ {rma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return render_template('index.html', resultado=resultado_formatado, form_data=request.form)

    except (ValueError, TypeError) as e:
        resultado = f"Erro nos dados de entrada. Por favor, verifique os valores. Detalhe: {e}"
        return render_template('index.html', resultado=resultado, form_data=request.form)

if __name__ == '__main__':
    app.run(debug=True)
