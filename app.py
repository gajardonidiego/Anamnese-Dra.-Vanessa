import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Ficha de Anamnese - Dra. Vanessa Mendonça", page_icon="🦷", layout="centered")

# Estilos Personalizados (Azul, Dourado e Cinza)
st.markdown("""
    <style>
        /* Cores da Identidade Visual */
        :root {
            --azul: #1B365D;
            --dourado: #D4AF37;
            --cinza: #F0F2F5;
        }
        
        .stApp {
            background-color: var(--cinza);
        }
        
        h1, h2, h3, h4, h5, h6, p, label {
            color: var(--azul) !important;
        }
        
        .stButton>button {
            background-color: var(--azul);
            color: var(--dourado);
            border: 2px solid var(--dourado);
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: var(--dourado);
            color: var(--azul);
            border: 2px solid var(--azul);
        }
        
        .header-box {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 5px solid var(--dourado);
            margin-bottom: 30px;
        }
        
        .header-title {
            color: var(--azul);
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .header-subtitle {
            color: #555;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Inicialização do Banco de Dados
@st.cache_resource
def get_db_connection():
    return sqlite3.connect('anamnese_guararapes.db', check_same_thread=False)

conn = get_db_connection()

# Roteamento via URL
query_params = st.query_params
is_admin = query_params.get("admin", "") == "true"

if not is_admin:
    # --- ÁREA DO PACIENTE ---
    
    # Cabeçalho Personalizado
    st.markdown('''
        <div class="header-box">
            <div class="header-title">CONSULTÓRIO ODONTOLÓGICO GUARARAPES</div>
            <div class="header-subtitle"><b>Dra. Vanessa Mendonça</b> – Cirurgiã Dentista<br>CROSP: 107.045</div>
            <hr style="border: 1px solid #D4AF37; margin: 15px 0;">
            <p style="font-size: 14px; text-align: justify; margin:0;">
                Este questionário atende às exigências legais, éticas e terapêuticas, tendo a finalidade de auxiliar a Cirurgiã Dentista na avaliação das condições gerais de saúde. As informações são confidenciais.
            </p>
        </div>
    ''', unsafe_allow_html=True)
    
    with st.form("anamnese_form"):
        st.subheader("1. IDENTIFICAÇÃO DO PACIENTE")
        nome = st.text_input("Nome completo *")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            data_nasc = st.date_input("Data de nascimento", format="DD/MM/YYYY")
        with col2:
            idade = st.number_input("Idade *", min_value=0, max_value=120)
        with col3:
            telefone = st.text_input("Telefone *")
            
        col4, col5 = st.columns(2)
        with col4:
            cpf = st.text_input("CPF *")
        with col5:
            rg = st.text_input("RG")
            
        endereco = st.text_input("Endereço completo")
        
        st.markdown("---")
        st.subheader("2. MOTIVO DA CONSULTA")
        motivo = st.text_area("Descreva o motivo da consulta *")
        
        st.markdown("---")
        st.subheader("3. INFORMAÇÕES MÉDICAS GERAIS")
        tratamento_medico = st.radio("Está em tratamento médico atualmente?", ["Não", "Sim"])
        condicao_tratada = st.text_input("Se SIM, qual condição está sendo tratada?")
        medico = st.text_input("Médico responsável e Telefone")
        ult_exame = st.text_input("Último exame físico médico (aprox.)")
        ult_dentista = st.text_input("Último tratamento dentário (aprox.)")
        
        st.markdown("---")
        st.subheader("4. HÁBITOS E FUNÇÃO ORAL")
        col6, col7 = st.columns(2)
        with col6:
            range_dentes = st.radio("Range os dentes à noite?", ["Não", "Sim"])
            aperta_dentes = st.radio("Aperta os dentes com frequência?", ["Não", "Sim"])
            fuma = st.radio("Fuma?", ["Não", "Sim"])
        with col7:
            dif_abrir_boca = st.radio("Sente dificuldade para abrir a boca?", ["Não", "Sim"])
            bebe = st.radio("Bebe bebida alcoólica?", ["Não", "Sim"])
            
        st.markdown("---")
        st.subheader("5. HISTÓRICO DE SAÚDE")
        st.write("Você tem ou já teve:")
        
        doencas = []
        if st.checkbox("Febre reumática ou doença cardíaca reumática"): doencas.append("Febre Reumática")
        if st.checkbox("Anormalidades cardíacas congênitas"): doencas.append("Anormalidade Cardíaca")
        if st.checkbox("Doença cardiovascular (pressão alta, sopro, etc)"): doencas.append("Doença Cardiovascular")
        if st.checkbox("Asma"): doencas.append("Asma")
        if st.checkbox("Sinusite"): doencas.append("Sinusite")
        if st.checkbox("Diabetes"): doencas.append("Diabetes")
        if st.checkbox("Osteoporose"): doencas.append("Osteoporose")
        if st.checkbox("Anemia"): doencas.append("Anemia")
        if st.checkbox("Hepatite, icterícia ou doença hepática"): doencas.append("Hepatite/Doença Hepática")
        if st.checkbox("Úlcera estomacal"): doencas.append("Úlcera")
        if st.checkbox("Tuberculose"): doencas.append("Tuberculose")
        if st.checkbox("HIV/AIDS"): doencas.append("HIV/AIDS")
        
        hist_detalhe = st.text_area("Se marcou algum item acima, especifique detalhes:")
        
        st.markdown("---")
        st.subheader("6. MEDICAMENTOS")
        uso_medicamento = st.radio("Faz uso de medicamentos, drogas ou substâncias (inclusive homeopáticos)?", ["Não", "Sim"])
        medicamentos_quais = st.text_input("Se SIM, quais e por qual motivo?")
        
        st.markdown("---")
        st.subheader("7. SANGRAMENTOS E INTERCORRÊNCIAS")
        sangramento = st.radio("Já apresentou sangramento anormal após extrações, cirurgias ou traumas?", ["Não", "Sim"])
        hematomas = st.radio("Tem hematomas com frequência?", ["Não", "Sim"])
        transfusao = st.radio("Já precisou de transfusão sanguínea?", ["Não", "Sim"])
        reacao_anestesia = st.radio("Já teve reação a anestésicos?", ["Não", "Sim"])
        problema_odonto = st.radio("Já teve problema sério em tratamento odontológico anterior?", ["Não", "Sim"])
        problema_odonto_detalhe = st.text_input("Se SIM ao problema odontológico, descreva:")
        
        st.markdown("---")
        st.subheader("8. ALERGIAS")
        alergia_med = st.radio("Tem alergia a medicamentos?", ["Não", "Sim"])
        alergia_med_qual = st.text_input("Qual medicamento?")
        alergia_outra = st.radio("Possui outro tipo de alergia?", ["Não", "Sim"])
        alergia_outra_qual = st.text_input("Qual outra alergia?")
        
        st.markdown("---")
        st.subheader("9. INFORMAÇÕES COMPLEMENTARES")
        tipo_sang = st.text_input("Sabe seu tipo sanguíneo? Qual?")
        hospitalizado = st.radio("Foi hospitalizado nos últimos 5 anos?", ["Não", "Sim"])
        hosp_motivo = st.text_input("Motivo da hospitalização:")
        cirurgia = st.radio("Já realizou cirurgia importante?", ["Não", "Sim"])
        cirurgia_qual = st.text_input("Qual cirurgia?")
        outra_condicao = st.text_area("Possui alguma condição não mencionada acima que a dentista deva saber? Explique:")
        
        st.markdown("---")
        st.subheader("10. PARA PACIENTES DO SEXO FEMININO")
        sexo = st.radio("Sexo biológico", ["Masculino", "Feminino"])
        
        anticoncepcional = "N/A"
        gravida = "N/A"
        amamentando = "N/A"
        menopausa = "N/A"
        gineco = "N/A"
        
        if sexo == "Feminino":
            anticoncepcional = st.text_input("Toma anticoncepcional? Qual?")
            gravida = st.radio("Está ou pode estar grávida?", ["Não", "Sim"])
            amamentando = st.radio("Está amamentando?", ["Não", "Sim"])
            menopausa = st.radio("Já entrou em menopausa?", ["Não", "Sim"])
            gineco = st.radio("Está em acompanhamento ginecológico?", ["Não", "Sim"])
            
        st.markdown("---")
        st.subheader("DECLARAÇÃO DE RESPONSABILIDADE E CIÊNCIA")
        st.info("Declaro que todas as informações acima são verdadeiras e completas, assumindo total responsabilidade por sua veracidade. Comprometo-me a informar imediatamente qualquer alteração em meu estado de saúde. Autorizo, em caso de urgência, a adoção das medidas necessárias à preservação de minha saúde.")
        
        aceite = st.checkbox("Li, compreendi e concordo com a declaração acima. *", value=False)
        resp_legal = st.text_input("Nome do Responsável Legal (apenas se paciente for menor/incapaz)")
        cpf_resp = st.text_input("CPF do Responsável")
        
        submit = st.form_submit_button("Assinar e Enviar Ficha de Anamnese", use_container_width=True)
        
        if submit:
            if not nome.strip() or not telefone.strip() or not cpf.strip() or not motivo.strip():
                st.error("⚠️ Preencha os campos obrigatórios (Nome, Telefone, CPF e Motivo da Consulta).")
            elif not aceite:
                st.error("⚠️ Você deve concordar com a Declaração de Responsabilidade para enviar a ficha.")
            else:
                # Preparar dados para o banco
                dados = {
                    "Data_Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Nome": nome,
                    "Data_Nascimento": str(data_nasc),
                    "Idade": idade,
                    "Telefone": telefone,
                    "CPF": cpf,
                    "RG": rg,
                    "Endereco": endereco,
                    "Motivo": motivo,
                    "Tratamento_Medico": tratamento_medico,
                    "Condicao_Tratada": condicao_tratada,
                    "Medico_Resp": medico,
                    "Range_Dentes": range_dentes,
                    "Fuma": fuma,
                    "Bebe": bebe,
                    "Doencas_Previas": ", ".join(doencas),
                    "Medicamentos": medicamentos_quais if uso_medicamento == "Sim" else "Nenhum",
                    "Alergias_Med": alergia_med_qual if alergia_med == "Sim" else "Nenhuma",
                    "Cirurgias": cirurgia_qual if cirurgia == "Sim" else "Nenhuma",
                    "Sexo": sexo,
                    "Gestante": gravida,
                    "Responsavel": resp_legal
                }
                
                df_novo = pd.DataFrame([dados])
                df_novo.to_sql('pacientes', conn, if_exists='append', index=False)
                
                st.success("✅ Ficha enviada com sucesso! A Dra. Vanessa Mendonça e nossa equipe agradecem.")
                st.balloons()

else:
    # --- ÁREA DO MÉDICO ---
    st.markdown('''
        <div class="header-box">
            <div class="header-title">PAINEL CLÍNICO</div>
            <div class="header-subtitle">Consultório Odontológico Guararapes</div>
        </div>
    ''', unsafe_allow_html=True)
    
    senha = st.text_input("Senha de Acesso:", type="password")
    
    if senha == "vanessa2026":
        st.success("Acesso Autorizado - Dra. Vanessa")
        
        try:
            df = pd.read_sql_query("SELECT * FROM pacientes ORDER BY rowid DESC", conn)
            
            if not df.empty:
                st.write(f"**Fichas recebidas:** {len(df)}")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Banco de Dados (CSV)",
                    data=csv,
                    file_name='banco_anamnese_guararapes.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            else:
                st.info("Nenhuma ficha registrada ainda.")
        except Exception as e:
            st.info("O banco de dados ainda está vazio.")
            
    elif senha:
        st.error("Senha incorreta.")
