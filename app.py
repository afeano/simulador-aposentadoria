from flask import Flask, render_template, request
import pandas as pd
import io
import os

# --- Configuração do Flask (funciona para Render e Vercel) ---
# Verifica se está no ambiente Vercel para ajustar o caminho dos templates
if os.environ.get('VERCEL'):
    template_dir = os.path.abspath('../templates')
    app = Flask(__name__, template_folder=template_dir)
else:
    app = Flask(__name__) # Para Render e execução local

def obter_fator_anuidade(idade, sexo):
    """
    Utiliza a tabela atuarial BR-EMSsb-V.2015 (suavizada em 10%).
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
    return fator.iloc[0]['fator_anuidade'] if not fator.empty else 0.0

# --- ROTA UNIFICADA: A GRANDE MUDANÇA ESTÁ AQUI ---
@app.route('/', methods=['GET', 'POST'])
def simulador():
    resultado = None
    form_data = {}

    if request.method == 'POST':
        try:
            # Pega os dados do formulário enviado
            form_data = request.form
            saldo_conta = float(form_data['saldo_conta'])
            idade_participante = int(form_data['idade_participante'])
            sexo_participante = form_data['sexo_participante']
            
            idade_beneficiario_str = form_data.get('idade_beneficiario')
            sexo_beneficiario = form_data.get('sexo_beneficiario')

            aa = obter_fator_anuidade(idade_participante, sexo_participante)
            ap = 0.0

            if aa == 0.0:
                resultado = f"Erro: Idade ({idade_participante}) ou sexo do participante fora dos parâmetros."
            else:
                if idade_beneficiario_str and sexo_beneficiario:
                    idade_beneficiario = int(idade_beneficiario_str)
                    ap = obter_fator_anuidade(idade_beneficiario, sexo_beneficiario)
                    if ap == 0.0:
                        resultado = f"Erro: Idade ({idade_beneficiario}) ou sexo do beneficiário fora dos parâmetros."

                if not resultado: # Se não houve erro até agora, calcula
                    denominador = 13 * (aa + ap)
                    if denominador == 0:
                        resultado = "Erro: Fatores de anuidade resultaram em zero."
                    else:
                        rma = saldo_conta / denominador
                        resultado = f"R$ {rma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        except (ValueError, TypeError) as e:
            resultado = f"Erro nos dados de entrada. Verifique os valores."

    # Renderiza a mesma página para GET e POST
    # Se for POST, envia o resultado e os dados do formulário de volta
    return render_template('index.html', resultado=resultado, form_data=form_data)

