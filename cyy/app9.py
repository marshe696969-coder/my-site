import streamlit as st
from PIL import Image
import stepic
from cryptography.fernet import Fernet
import base64, io, wave, hashlib

# 1. Page Config & CSS Fix
st.set_page_config(page_title="Cryptobot Security", layout="centered")

st.markdown("""
<style>
    /* إزالة أي حقول فارغة في الأعلى */
    .block-container { padding-top: 2rem !important; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* خلفية داكنة ثابتة وأنيقة */
    [data-testid="stAppViewContainer"] {
        background-color: #0f1117 !important;
    }

    /* البطاقة الزجاجية */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(108, 92, 231, 0.3);
        text-align: center;
    }

    /* تأثير الوميض والتحرك للشخصية */
    .breathing-char {
        animation: breathe 3s ease-in-out infinite;
        filter: drop-shadow(0 0 10px #6c5ce7);
    }
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.08); opacity: 1; }
    }

    h1, h2, h3 { color: #c9a6ff !important; text-shadow: 0 0 10px #6c5ce7; }
    p, label { color: white !important; }

    /* تنسيق الأزرار */
    .stButton>button { 
        background: linear-gradient(45deg, #6c5ce7, #8e44ad) !important; 
        color: white !important; border-radius: 12px; height: 50px; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(108,92,231,0.4); }
</style>
""", unsafe_allow_html=True)
def get_key(pwd): return base64.urlsafe_b64encode(hashlib.sha256(pwd.encode()).digest())
def hide_audio(file, data):
    with wave.open(file, 'rb') as aud:
        p, f = aud.getparams(), bytearray(aud.readframes(aud.getnframes()))
    bin_d = ''.join(format(b, '08b') for b in data) + '1111111111111110'
    for i in range(len(bin_d)): f[i] = (f[i] & 254) | int(bin_d[i])
    return bytes(f), p
def extract_audio(file):
    with wave.open(file, 'rb') as aud: f = bytearray(aud.readframes(aud.getnframes()))
    bits, dec = "", bytearray()
    for b in f:
        bits += str(b & 1); 
        if len(bits) == 8:
            dec.append(int(bits, 2)); 
            if dec.endswith(b'\xff\xfe'): break
            bits = ""
    return dec[:-2]
if "page" not in st.session_state: st.session_state.page = "welcome"

# الواجهة 1: Welcome
if st.session_state.page == "welcome":
    st.markdown("<div class='glass-card' style='margin-top:100px;'>", unsafe_allow_html=True)
    st.title("🛡️ Cryptobot")
    st.write("Welcome to the Ultimate Steganography Platform.")
    if st.button("Enter Platform 🚀"):
        st.session_state.page = "options"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# الواجهة 2: Options
elif st.session_state.page == "options":
    st.markdown("<div class='glass-card' style='margin-top:50px;'>", unsafe_allow_html=True)
    st.title("Select Media")
    col1, col2 = st.columns(2)
    if col1.button("🖼️ Image"): st.session_state.page = "img"; st.rerun()
    if col2.button("🎵 Audio"): st.session_state.page = "aud"; st.rerun()
    if st.button("⬅️ Exit"): st.session_state.page = "welcome"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# الواجهة 3: العمليات (هنا يتم إصلاح المربع الفارغ)
elif st.session_state.page in ["img", "aud"]:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Options"): 
        st.session_state.page = "options"; st.rerun()
    
    st.title("Image Mode" if st.session_state.page=="img" else "Audio Mode")
    mode = st.radio("Action:", ["Encrypt", "Decrypt"], horizontal=True)
    
    # هذه الحقول تظهر الآن فقط داخل البطاقة
    file = st.file_uploader("Upload File", type=["png" if st.session_state.page=="img" else "wav"])
    pwd = st.text_input("Security Key", type="password")

    if file and pwd:
        f = Fernet(get_key(pwd))
        if mode == "Encrypt":
            msg = st.text_area("Message")
            if st.button("Inject Data"):
                with st.spinner("Processing..."):
                    try:
                        if st.session_state.page == "img":
                            res = stepic.encode(Image.open(file).convert("RGB"), f.encrypt(msg.encode()))
                            buf = io.BytesIO(); res.save(buf, format="PNG")
                            st.image(res, caption="Result"); st.download_button("Download", buf.getvalue(), "secret.png")
                        else:
                            fr, p = hide_audio(file, f.encrypt(msg.encode()))
                            buf = io.BytesIO()
                            with wave.open(buf, 'wb') as w: w.setparams(p); w.writeframes(fr)
                            st.download_button("Download", buf.getvalue(), "secret.wav")
                        st.success("✅ Success!")
                    except: st.error("Error!")
        else:
            if st.button("Extract"):
                try:
                    if st.session_state.page == "img":
                        d = stepic.decode(Image.open(file))
                        st.success(f"Message: {f.decrypt(d if isinstance(d, bytes) else d.encode()).decode()}")
                    else:
                        st.success(f"Message: {f.decrypt(bytes(extract_audio(file))).decode()}")
                except: st.error("Access Denied!")
    st.markdown("</div>", unsafe_allow_html=True)

