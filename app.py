import streamlit as st
import base64
from openai import OpenAI

# ══════════════════════════════════════════════
#  🎨 CSS حرفه‌ای — تم روشن، شیک، مدرن
# ══════════════════════════════════════════════
st.markdown("""
<style>
    /* فونت */
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
    }
    
    /* مخفی کردن منوی Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* پس‌زمینه اصلی */
    .stApp {
        background: #f7f8fc;
    }
    
    /* کانتینر اصلی */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 900px !important;
    }
    
    /* عنوان */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    /* زیرعنوان */
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    
    /* پیام کاربر */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p,
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stMarkdown {
        color: #ffffff !important;
    }
    
    /* پیام دستیار */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background: #ffffff;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    /* آواتار */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        background: #ffffff !important;
    }
    
    /* فیلد ورودی چت */
    .stChatInput {
        position: sticky;
        bottom: 20px;
        background: #f7f8fc;
        padding-top: 10px;
    }
    .stChatInput textarea {
        color: #1a1a2e !important;
        background: #ffffff !important;
        border-radius: 24px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 15px !important;
        padding: 14px 20px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.2s ease;
    }
    .stChatInput textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* دکمه‌ها */
    .stButton > button {
        background: #ffffff;
        color: #475569 !important;
        border-radius: 12px;
        border: 1.5px solid #e2e8f0;
        padding: 8px 16px;
        font-weight: 500;
        font-family: 'Vazirmatn', sans-serif;
        transition: all 0.2s ease;
        font-size: 0.85rem;
    }
    .stButton > button:hover {
        background: #f8fafc;
        border-color: #667eea;
        color: #667eea !important;
        transform: translateY(-1px);
    }
    
    /* فایل آپلودر */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 14px;
        padding: 10px;
        border: 1.5px dashed #cbd5e1;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
    }
    
    /* کد */
    code {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 0.88em !important;
        font-family: 'Consolas', 'Monaco', monospace !important;
    }
    pre {
        background: #0f172a !important;
        border-radius: 14px !important;
        padding: 18px !important;
        border: 1px solid #1e293b !important;
        overflow-x: auto;
    }
    pre code {
        background: transparent !important;
        color: #e2e8f0 !important;
        font-size: 0.88em !important;
    }
    
    /* سایدبار */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
    }
    
    /* دکمه ورود */
    .login-btn button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* کارت لاگین */
    .login-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 40px 30px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
        text-align: center;
        max-width: 400px;
        margin: 40px auto;
    }
    
    /* جداکننده */
    hr {
        border-color: #e2e8f0;
        margin: 16px 0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Caption */
    .stCaption, small {
        color: #94a3b8 !important;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  🔐 کلیدها
# ══════════════════════════════════════════════
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
PASSWORD = st.secrets["PASSWORD"]


# ══════════════════════════════════════════════
#  🤖 مدل‌ها — سریع‌ترین‌های رایگان
# ══════════════════════════════════════════════
MODELS = [
    "google/gemini-2.0-flash-exp:free",       # سریع‌ترین
    "qwen/qwen-2.5-vl-72b-instruct:free",    # تصویرخوان
    "openrouter/free",
]

SYSTEM_PROMPT = (
    "تو یک دستیار هوشمند، دقیق و صمیمی برای برنامه‌نویسی و پاسخ به سوالات دانشی هستی. "
    "قوانین:\n"
    "۱. اگر کاربر فارسی نوشت، فارسی و ساده پاسخ بده.\n"
    "۲. اگر تصویر کد یا اسکرین‌شات بفرستد، دقیق تحلیل کن.\n"
    "۳. کدها را همیشه داخل ``` قرار بده.\n"
    "۴. پاسخ‌ها کوتاه، مفید و بدون حاشیه‌روی.\n"
    "۵. اگر چیزی را نمی‌دانی، صادقانه بگو."
)


# ══════════════════════════════════════════════
#  🛠 توابع
# ══════════════════════════════════════════════
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )


def init():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_model" not in st.session_state:
        st.session_state.current_model = MODELS[0]


def login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class='login-card'>
            <div style='font-size: 3rem; margin-bottom: 10px;'>🤖</div>
            <h2 style='margin: 0 0 8px 0; color: #1a1a2e;'>چت‌بات شخصی</h2>
            <p style='color: #94a3b8; font-size: 0.9rem; margin-bottom: 24px;'>
                دستیار هوشمند برنامه‌نویسی
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        pwd = st.text_input(
            "رمز عبور",
            type="password",
            placeholder="رمز را وارد کنید...",
            label_visibility="collapsed",
        )
        
        st.markdown("<div class='login-btn'>", unsafe_allow_html=True)
        if st.button("🔓 ورود", use_container_width=True):
            if pwd == PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ رمز اشتباه است")
        st.markdown("</div>", unsafe_allow_html=True)


def show_history():
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("img"):
                st.image(m["img"], width=280)
            st.markdown(m.get("text", ""))


def ask_stream(text, img_bytes=None, mime=None):
    """پاسخ Streaming"""
    client = get_client()
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]

    for m in st.session_state.messages[-10:]:
        msgs.append({"role": m["role"], "content": m.get("text", "")})

    if img_bytes:
        b64 = base64.b64encode(img_bytes).decode()
        content = [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        ]
        msgs.append({"role": "user", "content": content})
    else:
        msgs.append({"role": "user", "content": text})

    last_err = None
    for model in MODELS:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=msgs,
                stream=True,
                extra_body={
                    "plugins": [{"id": "web", "max_results": 3}],
                },
            )
            st.session_state.current_model = model
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return
        except Exception as e:
            last_err = e
            continue
    yield f"❌ خطا در همه مدل‌ها: {last_err}"


def main():
    st.set_page_config(
        page_title="چت‌بات شخصی",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    init()

    if not st.session_state.logged_in:
        login()
        return

    # ── هدر ──
    st.markdown("""
    <h1>🤖 چت‌بات هوش مصنوعی</h1>
    <p class='subtitle'>دستیار شخصی برنامه‌نویسی و دانش</p>
    """, unsafe_allow_html=True)

    # ── سایدبار ──
    with st.sidebar:
        st.markdown("### ⚙️ تنظیمات")
        
        st.caption(f"🌟 مدل فعال:\n`{st.session_state.current_model}`")
        st.caption("🌐 جستجوی وب: فعال")
        
        st.divider()
        
        if st.button("🧹 پاک کردن گفتگو", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.caption("💡 ساخته شده با ❤️")

    # ── پیام خوش‌آمد ──
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "سلام! 👋\n\n"
                "من دستیار شخصی تو هستم. چطور می‌تونم کمکت کنم؟\n\n"
                "💻 **برنامه‌نویسی** — سوال کد داری؟\n"
                "📷 **تحلیل تصویر** — از دکمه 📎 پایین استفاده کن\n"
                "🌐 **اطلاعات به‌روز** — از اینترنت جستجو می‌کنم\n"
            )
    else:
        show_history()

    # ── آپلود تصویر (بالای فیلد چت) ──
    with st.expander("📎 ارسال تصویر", expanded=False):
        up = st.file_uploader(
            "عکس کد یا اسکرین‌شات",
            type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed",
        )
        if up:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(up, use_container_width=True)
            with col2:
                q = st.text_input(
                    "سوال درباره تصویر",
                    value="این تصویر رو تحلیل کن",
                )
                if st.button("🚀 ارسال", use_container_width=True):
                    img = up.getvalue()
                    mime = up.type or "image/png"
                    st.session_state.messages.append(
                        {"role": "user", "text": q, "img": img}
                    )
                    with st.chat_message("user"):
                        st.image(img, width=280)
                        st.markdown(q)
                    with st.chat_message("assistant"):
                        try:
                            ans = st.write_stream(ask_stream(q, img, mime))
                        except Exception as e:
                            ans = f"خطا: {e}"
                            st.markdown(ans)
                    st.session_state.messages.append(
                        {"role": "assistant", "text": ans}
                    )
                    st.rerun()

    # ── چت متنی ──
    text = st.chat_input("پیامت رو بنویس...")
    if text:
        st.session_state.messages.append({"role": "user", "text": text})
        with st.chat_message("user"):
            st.markdown(text)

        with st.chat_message("assistant"):
            try:
                ans = st.write_stream(ask_stream(text))
            except Exception as e:
                ans = f"خطا: {e}"
                st.markdown(ans)

        st.session_state.messages.append({"role": "assistant", "text": ans})


main()
