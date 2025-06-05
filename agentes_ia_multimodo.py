import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import random
import time
from dotenv import load_dotenv
from gtts import gTTS
import base64

# Carrega variáveis do .env
load_dotenv()

# CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="Minha Cabeça", layout="wide", page_icon="🧠")

# Tela de abertura com imagem engraçada personalizada
if "iniciado" not in st.session_state:
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; height: 80vh;'>
            <img src='cerebro_zoeiro.png' width='600'>
        </div>
    """, unsafe_allow_html=True)
    st.title("🧠 Minha Cabeça")
    st.markdown("### Bem-vindo ao seu laboratório de agentes de IA.")
    st.markdown("Clique no botão abaixo para começar.")
    if st.button("Entrar na mente »"):
        st.session_state.iniciado = True
    st.stop()

# Interface principal
st.title("🧠 Minha Cabeça - Bate-papo com Agentes IA")
st.markdown("""<style>body { background-color: #0e1117; color: white; } .stButton>button { background-color: #262730; color: white; }</style>""", unsafe_allow_html=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-3.5-turbo"
preco_por_1k_tokens = {"gpt-3.5-turbo": 0.0015, "gpt-4": 0.03}

# AGENTES
agentes = [
    {
        "nome": "Hacker Rebelde",
        "persona": "Você desafia o sistema com sarcasmo. É criativo, curioso e destemido. Sempre procura soluções com código. Adora automatizar tudo e pensa como um hacker.",
        "mensagens": []
    },
    {
        "nome": "Especialista em Marketing",
        "persona": "Você é um marqueteiro criativo e direto. Astuto nas palavras, domina ferramentas de criação de conteúdo e sabe como promover qualquer negócio ou ideia.",
        "mensagens": []
    },
    {
        "nome": "Advogado Rebelde",
        "persona": "Você é perspicaz, fala de forma simples e domina Direito Civil, Penal, Trabalhista e de Marcas e Patentes. Gosta de provocar com argumentos diretos e fortes.",
        "mensagens": []
    },
    {
        "nome": "Curioso",
        "persona": "Você é extremamente curioso. Opine sobre qualquer tema, traga ideias, dados e responda como se estivesse explorando a web para enriquecer a conversa com os demais agentes.",
        "mensagens": []
    },
    {
        "nome": "Observador",
        "persona": "Você observa tudo com calma e sabedoria. Resume, conecta ideias, aponta contradições e entrega conselhos ponderados com base nas falas dos demais.",
        "mensagens": []
    }
]

# Verificação de modo antes de continuar
if "modo" not in st.session_state:
    st.session_state.modo = None

modo = st.sidebar.radio("Escolha o modo de interação:", ["Conversa Individual", "Debate entre Agentes"])

if modo:
    st.session_state.modo = modo

def gerar_audio(texto):
    tts = gTTS(text=texto, lang='pt')
    tts.save("voz_observador.mp3")
    with open("voz_observador.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return f"data:audio/mp3;base64,{audio_b64}"

if st.session_state.modo == "Conversa Individual":
    st.sidebar.subheader("Escolha o agente")
    agente_nomes = [a["nome"] for a in agentes]
    escolhido = st.sidebar.selectbox("Agente:", agente_nomes)
    agente = next((a for a in agentes if a["nome"] == escolhido), None)

    if agente:
        st.markdown(f"### 💬 Conversa com **{agente['nome']}**")
        entrada = st.text_input("Você:", key="input_usuario")
        if entrada:
            agente["mensagens"].append({"role": "user", "content": entrada})
            with st.spinner("A IA está pensando..."):
                resposta = client.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "system", "content": agente["persona"]}] + agente["mensagens"],
                    temperature=0.9
                )
                conteudo = resposta.choices[0].message.content
                agente["mensagens"].append({"role": "assistant", "content": conteudo})
                st.markdown(f"**{agente['nome']}:** {conteudo}")

elif st.session_state.modo == "Debate entre Agentes":
    st.markdown("### 🧠 Debate entre agentes de IA")
    tema = st.text_input("Tema para o debate:")
    rodadas = st.number_input("Número de rodadas:", min_value=1, max_value=10, value=2, step=1)
    tempo_entre_rodadas = st.slider("Tempo entre rodadas (segundos):", 0, 10, 2)

    if st.button("Iniciar debate") and tema:
        st.markdown(f"#### Tema: *{tema}*")
        mensagens_debate = [{"role": "user", "content": tema}]

        ordem = agentes[:-1]
        debate_texto = f"Tema do debate: {tema}\n\n"

        for rodada in range(rodadas):
            st.markdown(f"### 🔁 Rodada {rodada + 1}")
            random.shuffle(ordem)
            for agente in ordem:
                resposta = client.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "system", "content": agente["persona"]}] + mensagens_debate,
                    temperature=0.9
                )
                conteudo = resposta.choices[0].message.content
                mensagens_debate.append({"role": "assistant", "content": conteudo})
                st.markdown(f"**{agente['nome']}**: {conteudo}")
                debate_texto += f"{agente['nome']}: {conteudo}\n\n"
                time.sleep(tempo_entre_rodadas)

        st.markdown("---")
        st.markdown("### 🧠 Conclusão do Observador")
        observador = next(a for a in agentes if a["nome"] == "Observador")
        resposta_obs = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "system", "content": observador["persona"]}] + mensagens_debate,
            temperature=0.7
        )
        conteudo_obs = resposta_obs.choices[0].message.content
        st.markdown(f"**{observador['nome']}**: {conteudo_obs}")

        st.audio(gerar_audio(conteudo_obs), format="audio/mp3")
        debate_texto += f"Observador: {conteudo_obs}\n"

        st.download_button("📥 Baixar debate completo", data=debate_texto, file_name="debate_minha_cabeca.txt")
