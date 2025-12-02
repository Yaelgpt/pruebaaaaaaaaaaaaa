# components/tts.py
from streamlit.components.v1 import html as st_html

def mostrar_tts_bar(center=True):
    pos = "left:50%;transform:translateX(-50%);" if center else "left:12px;"
    ui = (
        '<div id="tts_bar" aria-live="polite" '
        'style="position:fixed; ' + pos + ' bottom:12px; z-index:9999"></div>'
        """
<script>
(function(){
  const synth = window.speechSynthesis;
  if(!synth) return;

  const bar = document.getElementById('tts_bar');
  if(!bar) return;
  if(bar.dataset.ready === '1') return;

  bar.innerHTML = `
    <style>
      .tts-wrap{background:rgba(28,28,33,.95);color:#fff;padding:8px 12px;border-radius:10px;
                font:14px system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
                box-shadow:0 2px 16px rgba(0,0,0,.25);display:flex;gap:10px;align-items:center}
      .tts-btn{background:#1f2937;border:1px solid #3f3f46;color:#fff;border-radius:6px;cursor:pointer;padding:6px 10px}
      .tts-sl{width:140px}
      .tts-sel{background:#111827;color:#fff;border:1px solid #374151;border-radius:6px;padding:4px}
    </style>
    <div class="tts-wrap">
      <button class="tts-btn" id="tts_sel">Leer selección</button>
      <button class="tts-btn" id="tts_all">Leer página</button>
      <button class="tts-btn" id="tts_stop">Detener</button>
      <span>Voz</span>
      <select id="tts_voice" class="tts-sel"></select>
      <span>Velocidad</span><input id="tts_rate" class="tts-sl" type="range" min="0.5" max="1.75" step="0.05" value="1">
      <span>Volumen</span><input id="tts_vol" class="tts-sl" type="range" min="0" max="1" step="0.05" value="1">
    </div>
  `;

  bar.dataset.ready = '1';

  const voiceSel = document.getElementById('tts_voice');
  const rate = document.getElementById('tts_rate');
  const vol  = document.getElementById('tts_vol');

  function loadVoices(){
    const voices = synth.getVoices();
    voiceSel.innerHTML = "";
    const ordered = [...voices].sort((a,b)=>(a.lang.startsWith('es')?0:1)-(b.lang.startsWith('es')?0:1));
    ordered.forEach(v=>{
      const o = document.createElement('option');
      o.value = v.name; o.textContent = v.name + " " + v.lang;
      if(v.default) o.selected = true;
      voiceSel.appendChild(o);
    });
  }
  loadVoices();
  if('onvoiceschanged' in speechSynthesis){
    speechSynthesis.onvoiceschanged = loadVoices;
  }

  function speak(txt){
    if(!txt || !txt.trim()) return;
    const u = new SpeechSynthesisUtterance(txt.trim());
    const v = synth.getVoices().find(x => x.name === voiceSel.value);
    if(v) u.voice = v;
    u.rate = parseFloat(rate.value || "1");
    u.volume = parseFloat(vol.value || "1");
    synth.cancel();
    synth.speak(u);
  }

  document.getElementById('tts_sel').onclick = () => speak(String(window.getSelection()));
  document.getElementById('tts_all').onclick = () => {
    const clone = document.body.cloneNode(true);
    clone.querySelectorAll('#tts_bar,script,style,link,svg,[aria-live],[role="navigation"]').forEach(n => n.remove());
    speak(clone.innerText.replace(/\\s+/g,' ').trim());
  };
  document.getElementById('tts_stop').onclick = () => synth.cancel();
})();
</script>
"""
    )
    st_html(ui, height=0, scrolling=False)

def ocultar_tts_bar():
    st_html('<script>const b=document.getElementById("tts_bar"); if(b) b.remove();</script>', height=0)
