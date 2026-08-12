import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time
import uuid
from fpdf import FPDF
from supabase import create_client, Client

# Configuração da Página
st.set_page_config(page_title="Ficha de Anamnese - Dra. Vanessa Mendonça", page_icon="🦷", layout="centered")

# Estilos Personalizados
st.markdown("""
    <style>
        :root { --azul: #1B365D; --dourado: #D4AF37; --cinza: #F0F2F5; }
        .stApp { background-color: var(--cinza); }
        h1, h2, h3, h4, h5, h6, p, label { color: var(--azul) !important; }
        .stButton > button[kind="primary"] {
            background-color: var(--dourado) !important; color: var(--azul) !important; font-size: 20px !important;
            font-weight: 900 !important; padding: 25px !important; border-radius: 12px !important;
            border: 2px solid var(--azul) !important; box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important; text-transform: uppercase; margin-top: 20px;
        }
        .stButton > button[kind="primary"]:hover { background-color: #E6C657 !important; transform: scale(1.02); box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important; }
        .header-box { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid var(--dourado); margin-bottom: 30px; }
        .header-title { color: var(--azul); font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .header-subtitle { color: #555; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

def limpa_numeros(texto):
    return re.sub(r'\D', '', texto)

# Conexão Oficial com o Supabase via Secrets
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()
query_params = st.query_params
is_admin = query_params.get("admin", "") == "true"

# --- FUNÇÃO PARA GERAR O PDF IDÊNTICO À FICHA FÍSICA ---
def gerar_pdf(paciente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def c(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')
        
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, txt=c("CONSULTÓRIO ODONTOLÓGICO GUARARAPES"), ln=True, align='C')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, txt=c("Dra. Vanessa Mendonça - Cirurgiã Dentista | CROSP: 107.045"), ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, txt=c("Avenida Rio Branco 832, Centro, Guararapes, SP | Tel: (18) 3606-0509"), ln=True, align='C')
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(7)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt=c("FICHA DE ANAMNESE CLINICA"), ln=True, align='C')
    pdf.ln(3)
    
    def section(title):
        pdf.ln(3)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 6, txt=c(title), ln=True, fill=True)
        pdf.ln(2)
        
    def field(label, value):
        pdf.set_font("Arial", 'B', 9)
        pdf.write(5, c(label))
        pdf.set_font("Arial", '', 9)
        pdf.write(5, c(str(value)) + "\n")

    section("1. IDENTIFICAÇÃO DO PACIENTE")
    field("Data do Preenchimento: ", paciente.get('Data_Envio'))
    field("Nome: ", paciente.get('Nome'))
    field("Data de Nascimento: ", paciente.get('Data_Nascimento'))
    field("Idade: ", paciente.get('Idade'))
    field("Telefone: ", paciente.get('Telefone'))
    field("CPF: ", paciente.get('CPF'))
    field("RG: ", paciente.get('RG'))
    field("Endereço: ", paciente.get('Endereco'))
    
    section("2. MOTIVO DA CONSULTA")
    field("Queixa Principal: ", paciente.get('Motivo_Consulta'))
    
    section("3. INFORMAÇÕES MÉDICAS GERAIS")
    field("Em tratamento médico? ", paciente.get('Tratamento_Medico_Atual'))
    field("Condição tratada: ", paciente.get('Condicao_Sendo_Tratada'))
    field("Médico e Telefone: ", paciente.get('Medico_e_Telefone'))
    field("Último Exame Físico: ", paciente.get('Ultimo_Exame_Medico'))
    field("Último Tratamento Dentário: ", paciente.get('Ultimo_Dentista'))
    
    section("4. HÁBITOS E FUNÇÃO ORAL")
    field("Range os dentes: ", paciente.get('Range_Dentes'))
    field("Aperta os dentes: ", paciente.get('Aperta_Dentes'))
    field("Dificuldade para abrir a boca: ", paciente.get('Dificuldade_Abrir_Boca'))
    field("Fuma: ", paciente.get('Fuma'))
    field("Bebe: ", paciente.get('Bebe'))
    
    section("5. HISTÓRICO DE SAÚDE")
    field("Doenças Prévias: ", paciente.get('Doencas_Previas'))
    field("Detalhes das Doenças: ", paciente.get('Detalhes_Doencas'))
    
    section("6. MEDICAMENTOS")
    field("Usa medicamentos? ", paciente.get('Usa_Medicamentos'))
    field("Quais: ", paciente.get('Quais_Medicamentos'))
    
    section("7. SANGRAMENTOS E INTERCORRÊNCIAS")
    field("Sangramento Anormal: ", paciente.get('Sangramento_Anormal'))
    field("Hematomas: ", paciente.get('Hematomas_Frequentes'))
    field("Transfusão Sanguínea: ", paciente.get('Transfusao_Sanguinea'))
    field("Reação a Anestésicos: ", paciente.get('Reacao_Anestesico'))
    field("Problema Odontológico Anterior: ", paciente.get('Problema_Odonto_Anterior'))
    field("Detalhes do Problema: ", paciente.get('Detalhe_Problema_Odonto'))
    
    section("8. ALERGIAS")
    field("Alergia a Medicamentos: ", paciente.get('Alergia_Medicamentos'))
    field("Qual Medicamento: ", paciente.get('Qual_Alergia_Med'))
    field("Outra Alergia: ", paciente.get('Outra_Alergia'))
    field("Qual Outra Alergia: ", paciente.get('Qual_Outra_Alergia'))
    
    section("9. INFORMAÇÕES COMPLEMENTARES")
    field("Tipo Sanguíneo: ", paciente.get('Tipo_Sanguineo'))
    field("Hospitalizado nos últimos 5 anos: ", paciente.get('Hospitalizado_5_Anos'))
    field("Motivo Hospitalização: ", paciente.get('Motivo_Hospitalizacao'))
    field("Cirurgia Importante: ", paciente.get('Cirurgia_Importante'))
    field("Qual Cirurgia: ", paciente.get('Qual_Cirurgia'))
    field("Outras Condições: ", paciente.get('Outras_Condicoes_Saude'))
    
    section("10. QUESTIONÁRIO FEMININO")
    field("Sexo Biológico: ", paciente.get('Sexo_Biologico'))
    if paciente.get('Sexo_Biologico') == "Feminino":
        field("Toma Anticoncepcional: ", paciente.get('Toma_Anticoncepcional'))
        field("Grávida: ", paciente.get('Gravida'))
        field("Amamentando: ", paciente.get('Amamentando'))
        field("Menopausa: ", paciente.get('Menopausa'))
        field("Acompanhamento Ginecológico: ", paciente.get('Acompanhamento_Gineco'))
        
    section("ASSINATURA E RESPONSABILIDADE")
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, txt=c("Declaro que todas as informações acima são verdadeiras e completas, assumindo total responsabilidade por sua veracidade."))
    pdf.ln(3)
    field("Responsável Legal: ", paciente.get('Responsavel_Legal'))
    field("CPF Responsável: ", paciente.get('CPF_Responsavel'))
    
    pdf.ln(10)
    pdf.line(55, pdf.get_y(), 155, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, txt=c("Assinatura Eletrônica do Paciente / Responsável"), ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')


if not is_admin:
    # --- ÁREA DO PACIENTE ---
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
    
    st.subheader("1. IDENTIFICAÇÃO DO PACIENTE")
    nome = st.text_input("Nome completo *")
    
    col1, col2 = st.columns(2)
    with col1: 
        hoje = datetime.today()
        data_nasc = st.date_input("Data de nascimento *", min_value=datetime(1900, 1, 1), max_value=hoje, format="DD/MM/YYYY")
        idade_calc = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
        st.info(f"Idade calculada: **{idade_calc} anos**")
        
    with col2: 
        telefone = st.text_input("Telefone (com DDD) *", placeholder="Ex: 11999999999")
        
    col4, col5 = st.columns(2)
    with col4: 
        cpf = st.text_input("CPF (Apenas números) *", placeholder="Ex: 12345678900")
    with col5: 
        rg = st.text_input("RG (Apenas números)", placeholder="Ex: 123456789")
        
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
    sexo = st.radio("Sexo biológico *", ["Masculino", "Feminino"], index=None)
    
    is_female = (sexo == "Feminino")
    anticoncepcional = st.text_input("Toma anticoncepcional? Qual?", disabled=not is_female)
    gravida = st.radio("Está ou pode estar grávida?", ["Não", "Sim"], disabled=not is_female, index=0 if is_female else None)
    amamentando = st.radio("Está amamentando?", ["Não", "Sim"], disabled=not is_female, index=0 if is_female else None)
    menopausa = st.radio("Já entrou em menopausa?", ["Não", "Sim"], disabled=not is_female, index=0 if is_female else None)
    gineco = st.radio("Está em acompanhamento ginecológico?", ["Não", "Sim"], disabled=not is_female, index=0 if is_female else None)
        
    st.markdown("---")
    st.subheader("DECLARAÇÃO DE RESPONSABILIDADE E CIÊNCIA")
    st.info("Declaro que todas as informações acima são verdadeiras e completas, assumindo total responsabilidade por sua veracidade. Comprometo-me a informar imediatamente qualquer alteração em meu estado de saúde.")
    
    aceite = st.checkbox("Li, compreendi e concordo com a declaração acima. *", value=False)
    resp_legal = st.text_input("Nome do Responsável Legal (apenas se paciente for menor/incapaz)")
    cpf_resp = st.text_input("CPF do Responsável")
    
    submit = st.button("Assinar e Enviar Ficha de Anamnese", type="primary", use_container_width=True)
    
    if submit:
        cpf_limpo = limpa_numeros(cpf)
        telefone_limpo = limpa_numeros(telefone)
        rg_limpo = limpa_numeros(rg)
        
        if not nome.strip() or not telefone_limpo or not cpf_limpo or not motivo.strip() or not sexo:
            st.error("⚠️ Preencha os campos obrigatórios (Nome, Telefone, CPF, Motivo e Sexo).")
        elif len(cpf_limpo) != 11:
            st.error("⚠️ O CPF digitado é inválido. Por favor, digite os 11 números corretamente.")
        elif len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            st.error("⚠️ O Telefone digitado é inválido. Digite o DDD + Número.")
        elif rg.strip() and len(rg_limpo) < 5:
            st.error("⚠️ O RG digitado parece inválido. Digite apenas números.")
        elif not aceite:
            st.error("⚠️ Você deve concordar com a Declaração de Responsabilidade para enviar a ficha.")
        else:
            dados = {
                "ID_Ficha": str(uuid.uuid4()),
                "Data_Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome": nome,
                "Data_Nascimento": str(data_nasc),
                "Idade": idade_calc,
                "Telefone": telefone_limpo,
                "CPF": cpf_limpo,
                "RG": rg_limpo,
                "Endereco": endereco,
                "Motivo_Consulta": motivo,
                "Tratamento_Medico_Atual": tratamento_medico,
                "Condicao_Sendo_Tratada": condicao_tratada,
                "Medico_e_Telefone": medico,
                "Ultimo_Exame_Medico": ult_exame,
                "Ultimo_Dentista": ult_dentista,
                "Range_Dentes": range_dentes,
                "Aperta_Dentes": aperta_dentes,
                "Dificuldade_Abrir_Boca": dif_abrir_boca,
                "Fuma": fuma,
                "Bebe": bebe,
                "Doencas_Previas": ", ".join(doencas) if doencas else "Nenhuma",
                "Detalhes_Doencas": hist_detalhe,
                "Usa_Medicamentos": uso_medicamento,
                "Quais_Medicamentos": medicamentos_quais,
                "Sangramento_Anormal": sangramento,
                "Hematomas_Frequentes": hematomas,
                "Transfusao_Sanguinea": transfusao,
                "Reacao_Anestesico": reacao_anestesia,
                "Problema_Odonto_Anterior": problema_odonto,
                "Detalhe_Problema_Odonto": problema_odonto_detalhe,
                "Alergia_Medicamentos": alergia_med,
                "Qual_Alergia_Med": alergia_med_qual,
                "Outra_Alergia": alergia_outra,
                "Qual_Outra_Alergia": alergia_outra_qual,
                "Tipo_Sanguineo": tipo_sang,
                "Hospitalizado_5_Anos": hospitalizado,
                "Motivo_Hospitalizacao": hosp_motivo,
                "Cirurgia_Importante": cirurgia,
                "Qual_Cirurgia": cirurgia_qual,
                "Outras_Condicoes_Saude": outra_condicao,
                "Sexo_Biologico": sexo,
                "Toma_Anticoncepcional": anticoncepcional if is_female else "N/A",
                "Gravida": gravida if is_female else "N/A",
                "Amamentando": amamentando if is_female else "N/A",
                "Menopausa": menopausa if is_female else "N/A",
                "Acompanhamento_Gineco": gineco if is_female else "N/A",
                "Responsavel_Legal": resp_legal,
                "CPF_Responsavel": limpa_numeros(cpf_resp)
            }
            
            try:
                supabase.table("fichas_nuvem").insert(dados).execute()
                st.success("✅ Ficha enviada com sucesso! A Dra. Vanessa Mendonça e nossa equipe agradecem.")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar na nuvem. Verifique se a tabela 'fichas_nuvem' foi criada no Supabase. Detalhe: {e}")

else:
    # --- ÁREA DO MÉDICO ---
    
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False

    st.markdown('''
        <div class="header-box">
            <div class="header-title">PAINEL CLÍNICO</div>
            <div class="header-subtitle">Consultório Odontológico Guararapes</div>
        </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.autenticado:
        with st.form("login_form"):
            st.markdown("### 🔒 Acesso Restrito")
            senha = st.text_input("Senha de Acesso:", type="password", placeholder="Digite a senha do painel...")
            submit_login = st.form_submit_button("Entrar no Painel", type="primary", use_container_width=True)
            
            if submit_login:
                if senha == "vanessa2026":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta.")
    else:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.success("✅ Acesso Autorizado - Dra. Vanessa")
        with col2:
            if st.button("Sair (Logout)"):
                st.session_state.autenticado = False
                st.rerun()
                
        try:
            response = supabase.table("fichas_nuvem").select("*").execute()
            data = response.data
            
            if data:
                df = pd.DataFrame(data)
                if "Data_Envio" in df.columns:
                    df = df.sort_values(by="Data_Envio", ascending=False)
                
                lista_opcoes = ["📊 Visualizar Tabela Completa"] + [f"{row['Nome']} (Enviado em: {row['Data_Envio']})" for index, row in df.iterrows()]
                selecao = st.selectbox("Selecione uma opção:", lista_opcoes)
                
                if selecao == "📊 Visualizar Tabela Completa":
                    df_display = df.drop(columns=['ID_Ficha'], errors='ignore')
                    
                    st.write(f"**Total de pacientes registrados:** {len(df_display)}")
                    st.dataframe(df_display, use_container_width=True)
                    
                    csv = df_display.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Baixar Planilha Excel Correta (CSV)",
                        data=csv,
                        file_name='banco_anamnese_guararapes.csv',
                        mime='text/csv',
                        use_container_width=True
                    )
                else:
                    indice_paciente = lista_opcoes.index(selecao) - 1
                    paciente_dados = df.iloc[indice_paciente]
                    
                    st.markdown("---")
                    st.write(f"**Ficha selecionada:** {paciente_dados['Nome']}")
                    st.write(f"**Motivo da Consulta:** {paciente_dados['Motivo_Consulta']}")
                    
                    pdf_bytes = gerar_pdf(paciente_dados)
                    st.download_button(
                        label=f"📄 Gerar e Baixar PDF de {paciente_dados['Nome']}",
                        data=pdf_bytes,
                        file_name=f"Anamnese_{paciente_dados['Nome']}.pdf",
                        mime='application/pdf',
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.markdown("---")
                    with st.expander("🗑️ Excluir Ficha (Ação Irreversível)"):
                        st.warning(f"Você está prestes a excluir permanentemente a ficha de **{paciente_dados['Nome']}** da nuvem.")
                        
                        with st.form("form_exclusao"):
                            senha_exclusao = st.text_input("Confirme a senha do painel:", type="password")
                            palavra_exclusao = st.text_input("Digite a palavra EXCLUIR para autorizar:", placeholder="EXCLUIR")
                            
                            btn_excluir = st.form_submit_button("Confirmar Exclusão Permanente", use_container_width=True)
                            
                            if btn_excluir:
                                if senha_exclusao == "vanessa2026" and palavra_exclusao == "EXCLUIR":
                                    supabase.table("fichas_nuvem").delete().eq("ID_Ficha", paciente_dados['ID_Ficha']).execute()
                                    st.success("✅ Ficha excluída com sucesso! Atualizando painel...")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Erro: Senha incorreta ou palavra de segurança inválida (digite EXCLUIR em maiúsculas).")
                                    
            else:
                st.info("Nenhuma ficha registrada na nuvem ainda.")
        except Exception as e:
            st.info(f"Aguardando dados da nuvem. Detalhe: {e}")
