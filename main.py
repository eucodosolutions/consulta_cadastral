import sys
import asyncio
import re
import time

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import pandas as pd
from app.services.orchestrator import processar_cnpj_unico, processar_lote_planilha
from app.services.mailer import enviar_email_resultado

st.set_page_config(
    page_title="Consulta Situação Cadastral",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={},
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, body, p, div, span, h1, h2, h3, button { font-family: 'Inter', sans-serif !important; }

/* Ocultar elementos Streamlit padrão */
#MainMenu, footer, header[data-testid="stHeader"], .stDeployButton,
[data-testid="collapsedControl"], [data-testid="stToolbar"],
[data-testid="stSidebarNav"], [data-testid="stStatusWidget"] {
    display: none !important;
}

body, .stApp { background-color: #0e1117 !important; }

.block-container {
    padding: 72px 24px 120px !important;
    max-width: 800px !important;
}

/* ── Header top-left ── */
.app-header {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: #0e1117;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 10px 28px;
}
.app-header h1 {
    margin: 0; font-size: 20px; font-weight: 700; color: #f0f2f6;
}

/* ── Mensagens ── */
[data-testid="stChatMessage"] { background: transparent !important; padding: 4px 0 !important; }

/* Avatar assistente */
[data-testid="chatAvatarIcon-assistant"] svg,
[data-testid="chatAvatarIcon-assistant"] { color: #fff !important; }
[data-testid="chatAvatarIcon-assistant"] {
    background: #3d3d8f !important;
    border-radius: 50% !important;
    width: 36px !important; height: 36px !important;
}

/* Avatar usuário */
[data-testid="chatAvatarIcon-user"] {
    background: #3a3a4a !important;
    border-radius: 50% !important;
    width: 36px !important; height: 36px !important;
}

/* Balão do usuário */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
    gap: 12px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
    background: #5b5fc7 !important;
    border-radius: 20px 4px 20px 20px !important;
    padding: 12px 16px !important;
    max-width: 72% !important;
    color: #fff !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p {
    color: #fff !important;
}

/* Balão do assistente */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
    background: #1a1d2e !important;
    border-radius: 4px 20px 20px 20px !important;
    padding: 12px 16px !important;
    max-width: 80% !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Card de resultado ── */
.result-card {
    background: #1a1d2e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-top: 8px;
}
.result-card-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 20px;
}
.result-cnpj {
    font-size: 22px; font-weight: 700; color: #f0f2f6;
    display: flex; align-items: center; gap: 8px;
}
.result-company { color: rgba(240,242,246,0.5); font-size: 13px; margin-top: 2px; }
.badge-ativa {
    background: rgba(52,199,89,0.15);
    color: #34c759;
    border: 1px solid rgba(52,199,89,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px; font-weight: 600;
    display: flex; align-items: center; gap: 5px; white-space: nowrap;
}
.badge-nao-optante {
    background: rgba(255,69,58,0.12);
    color: #ff453a;
    border: 1px solid rgba(255,69,58,0.25);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px; font-weight: 600;
    white-space: nowrap;
}
.result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.result-field-label {
    font-size: 10px; font-weight: 600; letter-spacing: 1px;
    color: rgba(240,242,246,0.35); text-transform: uppercase; margin-bottom: 4px;
}
.result-field-value { font-size: 15px; font-weight: 600; color: #f0f2f6; }
.result-divider {
    border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 16px 0;
}
.result-actions { display: flex; gap: 10px; }
.btn-action {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.15);
    color: rgba(240,242,246,0.8);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px; font-weight: 500; cursor: pointer;
    display: flex; align-items: center; gap: 6px;
    transition: all 0.15s;
}
.btn-action:hover { border-color: rgba(255,255,255,0.35); color: #f0f2f6; }

/* ── Barra inferior fixa ── */
.bottom-bar-spacer { height: 90px; }
.bottom-bar {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 9998;
    background: #0e1117;
    border-top: 1px solid rgba(255,255,255,0.06);
    padding: 12px 0 16px;
}
.bottom-bar-inner {
    max-width: 800px; margin: 0 auto; padding: 0 24px;
    display: flex; align-items: center; gap: 10px;
}
.chat-input-wrapper {
    flex: 1;
    display: flex; align-items: center;
    background: #1a1d2e;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0 4px 0 4px;
    transition: border-color 0.2s;
}
.chat-input-wrapper:focus-within { border-color: rgba(91,95,199,0.6); }
.clip-icon-btn {
    background: transparent; border: none; cursor: pointer;
    padding: 10px 10px 10px 12px; color: rgba(240,242,246,0.35);
    display: flex; align-items: center; transition: color 0.15s; flex-shrink: 0;
}
.clip-icon-btn:hover { color: rgba(240,242,246,0.85); }
.send-btn {
    background: #5b5fc7; border: none; cursor: pointer;
    width: 42px; height: 42px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: background 0.15s; color: #fff;
}
.send-btn:hover { background: #4a4eb8; }

/* Streamlit chat_input: tornar invisível */
[data-testid="stChatInput"] {
    position: absolute !important; opacity: 0 !important;
    pointer-events: none !important; height: 0 !important;
}

/* Footer */
.app-footer {
    position: fixed; bottom: 0; left: 0; right: 0;
    text-align: center; padding: 4px 0 2px;
    font-size: 11px; color: rgba(240,242,246,0.2); z-index: 9997;
}

/* File uploader — fora da tela, invisível mas funcional */
[data-testid="stFileUploader"] {
    position: fixed !important;
    left: -9999px !important;
    top: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    opacity: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-header"><h1>Consulta Cadastral</h1></div>', unsafe_allow_html=True)

# ── JS: barra inferior personalizada + máscara ────────────────────────────────
st.components.v1.html("""
<script>
(function() {
  var pd = window.parent.document;
  if (pd.getElementById('rfb-custom-bar-script')) return;

  var script = pd.createElement('script');
  script.id = 'rfb-custom-bar-script';
  script.innerHTML = `
    var pendingFile = null;

    var CLIP_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>';
    var SEND_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>';
    var FILE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>';

    function mask(v) {
      v = v.replace(/\\\\D/g,'').slice(0,14);
      if (v.length>12) return v.replace(/(\\\\d{2})(\\\\d{3})(\\\\d{3})(\\\\d{4})(\\\\d+)/,'$1.$2.$3/$4-$5');
      if (v.length>8)  return v.replace(/(\\\\d{2})(\\\\d{3})(\\\\d{3})(\\\\d+)/,'$1.$2.$3/$4');
      if (v.length>5)  return v.replace(/(\\\\d{2})(\\\\d{3})(\\\\d+)/,'$1.$2.$3');
      if (v.length>2)  return v.replace(/(\\\\d{2})(\\\\d+)/,'$1.$2');
      return v;
    }

    function getFileLabel(name) {
      var ext = name.split('.').pop().toUpperCase();
      if (ext === 'XLSX' || ext === 'XLS') return 'Excel Spreadsheet';
      return 'CSV File';
    }

    function injectBar() {
      if (document.querySelector('.custom-bottom-bar')) return;

      var fileInput = document.createElement('input');
      fileInput.type = 'file'; fileInput.accept = '.csv,.xlsx,.xls';
      fileInput.style.display = 'none';
      document.body.appendChild(fileInput);
      fileInput.addEventListener('change', function() {
        var file = this.files[0]; if (!file) return;
        pendingFile = file; showChip(file); this.value = '';
      });

      var bar = document.createElement('div');
      bar.className = 'custom-bottom-bar';
      bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:9998;background:#0e1117;border-top:1px solid rgba(255,255,255,0.07);padding:12px 0 20px;';

      var inner = document.createElement('div');
      inner.style.cssText = 'max-width:800px;margin:0 auto;padding:0 24px;display:flex;align-items:center;gap:10px;';

      var wrapper = document.createElement('div');
      wrapper.style.cssText = 'flex:1;display:flex;align-items:center;background:#1a1d2e;border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0 4px;min-width:0;transition:border-color 0.2s;';
      wrapper.addEventListener('focusin',  function(){ this.style.borderColor='rgba(91,95,199,0.6)'; });
      wrapper.addEventListener('focusout', function(){ this.style.borderColor='rgba(255,255,255,0.1)'; });

      var clip = document.createElement('button');
      clip.innerHTML = CLIP_SVG;
      clip.style.cssText = 'background:transparent;border:none;cursor:pointer;padding:10px 8px 10px 12px;color:rgba(240,242,246,0.35);display:flex;align-items:center;flex-shrink:0;outline:none;transition:color 0.15s;';
      clip.addEventListener('mouseenter', function(){ if(!pendingFile) this.style.color='rgba(240,242,246,0.85)'; });
      clip.addEventListener('mouseleave', function(){ if(!pendingFile) this.style.color='rgba(240,242,246,0.35)'; });
      clip.addEventListener('click', function(e){
        e.preventDefault();
        if (pendingFile) return; 
        fileInput.click();
      });

      var textInput = document.createElement('input');
      textInput.type = 'text'; textInput.placeholder = '00.000.000/0000-00';
      textInput.style.cssText = 'flex:1;background:transparent;border:none;outline:none;color:#f0f2f6;font-family:Inter,sans-serif;font-size:15px;padding:12px 8px;min-width:0;';
      textInput.addEventListener('input', function() {
        if (pendingFile) return;
        var v = mask(this.value);
        if (this.value !== v) { var c=this.selectionStart+(v.length-this.value.length); this.value=v; try{this.setSelectionRange(c,c);}catch(e){} }
      });
      textInput.addEventListener('keydown', function(e) {
        if (e.key !== 'Enter') return;
        if (pendingFile) { sendFile(); } else if (this.value.trim()) { submitCNPJ(this.value); this.value=''; }
      });

      var send = document.createElement('button');
      send.innerHTML = SEND_SVG;
      send.style.cssText = 'background:#5b5fc7;border:none;cursor:pointer;width:42px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#fff;margin:4px;outline:none;transition:background 0.15s;';
      send.addEventListener('mouseenter', function(){ this.style.background='#4a4eb8'; });
      send.addEventListener('mouseleave', function(){ this.style.background='#5b5fc7'; });
      send.addEventListener('click', function() {
        if (pendingFile) {
          var email = textInput.value.trim();
          if (!email || !email.includes('@')) { textInput.style.borderBottom='1px solid #ff453a'; setTimeout(function(){ textInput.style.borderBottom=''; },1500); return; }
          sendFile(email);
        } else if (textInput.value.trim()) {
          submitCNPJ(textInput.value); textInput.value='';
        }
      });

      function showChip(file) {
        clip.style.color = 'rgba(240,242,246,0.12)';
        clip.style.cursor = 'not-allowed';
        textInput.value = '';
        textInput.placeholder = 'Para qual e-mail devemos enviar o resultado?';
        textInput.style.display = '';
        textInput.focus();

        var chip = document.createElement('div');
        chip.id = 'rfb-chip';
        chip.style.cssText = 'display:flex;align-items:center;gap:6px;flex-shrink:0;padding:6px 0 6px 6px;';

        var icon = document.createElement('div');
        icon.style.cssText = 'width:34px;height:34px;background:#0d3d21;border-radius:7px;display:flex;align-items:center;justify-content:center;flex-shrink:0;border:1px solid rgba(74,222,128,0.25);';
        icon.innerHTML = FILE_SVG;

        var info = document.createElement('div');
        info.style.cssText = 'min-width:0;overflow:hidden;max-width:140px;';
        info.innerHTML = '<div style="color:#f0f2f6;font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + file.name
          + '</div><div style="color:rgba(240,242,246,0.38);font-size:10px;letter-spacing:.8px;text-transform:uppercase;margin-top:1px;">' + getFileLabel(file.name) + '</div>';

        var xBtn = document.createElement('button');
        xBtn.innerHTML = '&times;';
        xBtn.style.cssText = 'background:transparent;border:none;color:rgba(240,242,246,0.35);cursor:pointer;font-size:20px;line-height:1;padding:4px 8px;flex-shrink:0;outline:none;transition:color 0.15s;';
        xBtn.addEventListener('mouseenter', function(){ this.style.color='rgba(240,242,246,0.85)'; });
        xBtn.addEventListener('mouseleave', function(){ this.style.color='rgba(240,242,246,0.35)'; });
        xBtn.addEventListener('click', function() {
          pendingFile = null;
          removeChip();
          textInput.focus();
        });

        chip.appendChild(icon); chip.appendChild(info); chip.appendChild(xBtn);
        wrapper.insertBefore(chip, textInput);
      }

      function removeChip() {
        var c = wrapper.querySelector('#rfb-chip');
        if (c) c.remove();
        textInput.placeholder = '00.000.000/0000-00';
        textInput.value = '';
        clip.style.color = 'rgba(240,242,246,0.35)';
        clip.style.cursor = 'pointer';
      }

      function sendFile(email) {
        if (!pendingFile) return;
        var file = pendingFile;
        pendingFile = null;
        removeChip();
        
        var ta = document.querySelector('[data-testid="stChatInputTextArea"]');
        if (ta) {
          var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
          setter.call(ta, '__email__:' + email);
          ta.dispatchEvent(new Event('input', {bubbles:true}));
          ta.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, bubbles:true}));
        }
        
        setTimeout(function() {
          var stInput = document.querySelector('[data-testid="stFileUploaderDropzoneInput"]');
          if (stInput) {
            var dt = new DataTransfer();
            dt.items.add(file);
            Object.defineProperty(stInput, 'files', { get: function(){ return dt.files; }, configurable: true });
            stInput.dispatchEvent(new Event('change', {bubbles:true}));
          }
        }, 900);
      }

      function submitCNPJ(val) {
        var ta = document.querySelector('[data-testid="stChatInputTextArea"]');
        if (!ta) return;
        var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
        setter.call(ta, val);
        ta.dispatchEvent(new Event('input', {bubbles:true}));
        ta.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, bubbles:true}));
      }

      wrapper.appendChild(clip); wrapper.appendChild(textInput); wrapper.appendChild(send);
      inner.appendChild(wrapper); bar.appendChild(inner); document.body.appendChild(bar);

      setInterval(function() {
        var ta = document.querySelector('[data-testid="stChatInputTextArea"]');
        if (!ta) return;
        var isRunning = ta.disabled;
        
        textInput.disabled = isRunning;
        send.disabled = isRunning;
        
        if (isRunning) {
          wrapper.style.opacity = '0.5';
          send.style.cursor = 'not-allowed';
          clip.style.cursor = 'not-allowed';
          textInput.style.cursor = 'not-allowed';
        } else {
          wrapper.style.opacity = '1';
          send.style.cursor = 'pointer';
          textInput.style.cursor = 'text';
          clip.style.cursor = pendingFile ? 'not-allowed' : 'pointer';
        }
      }, 200);
    }

    var obs = new MutationObserver(function() { injectBar(); });
    obs.observe(document.body, {childList:true, subtree:true});
    setTimeout(injectBar, 300);
  `;

  pd.body.appendChild(script);
})();
</script>
""", height=0)


# ── Estado ────────────────────────────────────────────────────────────────────
def _init():
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "Olá! Sou seu assistente de consulta de situação cadastral. "
                "Você pode digitar um **CNPJ único** ou fazer o upload de uma "
                "**planilha** (.csv, .xlsx) contendo CNPJs para processamento em lote."
            ),
        }]
    st.session_state.setdefault("show_upload", False)
    st.session_state.setdefault("download_csv", None)
    st.session_state.setdefault("pending_email", None)
    st.session_state.setdefault("uploader_key", 0)

_init()


def _fmt(cnpj: str) -> str:
    d = re.sub(r"\D", "", cnpj)
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 else cnpj


def _card_resultado(dados: dict) -> str:
    """Gera o HTML do card de resultado no estilo da referência."""
    cnpj = _fmt(dados.get("cnpj", ""))
    nome = dados.get("nome_empresarial", "NÃO INFORMADO")
    simples = dados.get("situacao_simples_nacional", "NÃO INFORMADO")
    simei = dados.get("situacao_simei", "NÃO INFORMADO")

    optante = "optante" in simples.lower() and "não" not in simples.lower()
    badge_cls = "badge-ativa" if optante else "badge-nao-optante"
    badge_dot = "●" if optante else "●"
    badge_txt = "Optante SN" if optante else "Não Optante"

    return f"""
<div class="result-card">
  <div class="result-card-header">
    <div>
      <div class="result-cnpj">🏢 {cnpj}</div>
      <div class="result-company">{nome}</div>
    </div>
    <span class="{badge_cls}">{badge_dot} {badge_txt}</span>
  </div>
  <hr class="result-divider"/>
  <div class="result-grid">
    <div>
      <div class="result-field-label">Razão Social</div>
      <div class="result-field-value">{nome}</div>
    </div>
    <div>
      <div class="result-field-label">Simples Nacional</div>
      <div class="result-field-value">{simples}</div>
    </div>
    <div>
      <div class="result-field-label">SIMEI</div>
      <div class="result-field-value">{simei}</div>
    </div>
    <div>
      <div class="result-field-label">CNPJ</div>
      <div class="result-field-value">{cnpj}</div>
    </div>
  </div>
</div>
"""


def _handle_upload(f, email: str | None = None):
    """Processa planilha inline com spinner — sem loop de rerun."""
    nome = f.name

    # Mensagem do usuário (sem emoji)
    st.session_state.messages.append({"role": "user", "content": nome})
    with st.chat_message("user", avatar="👤"):
        st.markdown(nome)

    try:
        df = pd.read_csv(f) if nome.endswith(".csv") else pd.read_excel(f)
    except Exception:
        msg = "Não foi possível ler o arquivo."
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg)
        return

    col = next((c for c in df.columns if "cnpj" in c.lower()), None)
    if not col:
        msg = f"Coluna CNPJ não encontrada. Colunas disponíveis: `{', '.join(df.columns)}`"
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg)
        return

    # Processa com spinner visível
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(f"Aguarde o processamento da planilha..."):
            res = processar_lote_planilha(df, col)

    if res["sucesso"]:
        r = res["resumo"]
        linhas = [f"Concluído! **{r['sucessos']}** com sucesso, **{r['erros']}** com erro."]
        
        # Enviar e-mail se solicitado
        if email:
            linhas.append(f"Enviando resultados para {email}...")
            
        msg = "\n\n".join(linhas)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg)
            
        st.session_state.download_csv = res["resultados_df"].to_csv(index=False, sep=";").encode("utf-8-sig")
        st.session_state.download_name = f"resultado_{int(time.time())}.csv"
        
        # Faz o envio efetivo do e-mail (usando st.toast para não travar a UI principal com logs feios)
        if email:
            if enviar_email_resultado(email, res["resultados_df"], r):
                st.toast(f"✅ E-mail enviado com sucesso para {email}!", icon="📧")
            else:
                st.toast(f"❌ Falha ao enviar e-mail para {email}. Verifique as credenciais SMTP no .env.", icon="⚠️")

    else:
        msg = res['erro']
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg)


# ── Histórico de mensagens ─────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("tipo") == "card":
            st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

if st.session_state.download_csv:
    st.download_button(
        "Baixar planilha de resultados",
        data=st.session_state.download_csv,
        file_name=st.session_state.download_name,
        mime="text/csv",
    )

# ── Upload nativo (key dinâmica previne re-processamento em loop) ─────────
uploaded = st.file_uploader(
    "Anexar planilha",
    type=["csv", "xlsx"],
    key=f"file_uploader_{st.session_state.uploader_key}",
)
if uploaded:
    email = st.session_state.get("pending_email")
    st.session_state.pending_email = None
    st.session_state.uploader_key += 1   # reset: próximo rerun não vê mais o arquivo
    _handle_upload(uploaded, email=email)
    st.rerun()

# ── Input ─────────────────────────────────────────────────────────────────
prompt = st.chat_input("00.000.000/0000-00")

# ── Processamento ─────────────────────────────────────────────────────────
if prompt:
    # Detecta prefixo de e-mail enviado pelo JS
    if prompt.startswith("__email__:"):
        email_value = prompt.replace("__email__:", "", 1).strip()
        st.session_state.pending_email = email_value
        st.rerun()

    else:
        cnpj_fmt = _fmt(prompt)
        st.session_state.messages.append({"role": "user", "content": cnpj_fmt})

        with st.chat_message("user", avatar="👤"):
            st.markdown(cnpj_fmt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Consultando..."):
                resultado = processar_cnpj_unico(prompt)

            if resultado["sucesso"]:
                intro = "Aqui estão os detalhes encontrados para o CNPJ solicitado:"
                card_html = _card_resultado(resultado["dados"])
                conteudo = intro + "\n\n" + card_html
                st.markdown(intro)
                st.markdown(card_html, unsafe_allow_html=True)
                st.session_state.messages.append({
                    "role": "assistant", "content": conteudo, "tipo": "card",
                })
            else:
                resposta = f"❌ {resultado.get('erro', 'Falha desconhecida.')}"
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})


