import streamlit as st
import requests
from datetime import datetime

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="NEXUS AI", layout="wide")

st.markdown("""
<style>
    body { background: #ffffff; color: #2c3e50; }
    .header { border-bottom: 1px solid #e0e0e0; padding: 20px; }
    .message-content { padding: 12px 16px; border-radius: 8px; line-height: 1.5; }
    .user-content { background: #2c3e50; color: white; }
    .assistant-content { background: #ecf0f1; color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logado:
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("# NEXUS AI")
        st.markdown("### IA Inteligente e Rápida")
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Google", "GitHub", "Discord", "Email"])
        
        with tab1:
            if st.button("Continuar com Google", use_container_width=True):
                st.session_state.email = "usuario@gmail.com"
                st.session_state.nome = "Usuário"
                st.session_state.logado = True
                st.rerun()
        
        with tab2:
            if st.button("Continuar com GitHub", use_container_width=True):
                st.session_state.email = "usuario@github.com"
                st.session_state.nome = "Dev"
                st.session_state.logado = True
                st.rerun()
        
        with tab3:
            if st.button("Continuar com Discord", use_container_width=True):
                st.session_state.email = "usuario@discord.com"
                st.session_state.nome = "Gamer"
                st.session_state.logado = True
                st.rerun()
        
        with tab4:
            email = st.text_input("Email:")
            nome = st.text_input("Nome:")
            if st.button("Enviar Código", use_container_width=True):
                if email and nome:
                    st.session_state.email = email
                    st.session_state.nome = nome
                    st.success("Código enviado!")
else:
    with st.sidebar:
        st.markdown("### NEXUS AI")
        if st.button("Nova Conversa", use_container_width=True):
            st.session_state.messages = []
        
        st.markdown("---")
        st.markdown(f"**Usuário:** {st.session_state.nome}")
        st.markdown("**Mensagens:** 200/200")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logado = False
            st.rerun()
    
    st.markdown("# NEXUS AI")
    st.markdown("---")
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='message-content user-content'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message-content assistant-content'>{msg['content']}</div>", unsafe_allow_html=True)
    
    mensagem = st.text_input("Mensagem...")
    tipo = st.selectbox("Tipo", ["Fácil", "Difícil"])
    
    if mensagem:
        st.session_state.messages.append({"role": "user", "content": mensagem})
        
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"email": st.session_state.email, "mensagem": mensagem, "tipo": tipo.lower()}
            ).json()
            
            if response["status"] == "sucesso":
                st.session_state.messages.append({"role": "assistant", "content": response["resposta"]})
                st.success(f"✓ {response['mensagens_restantes']} mensagens restantes")
        except:
            st.error("Erro na conexão")
        
        st.rerun()
