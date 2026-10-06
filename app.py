import streamlit as st
import base64
import json
import os
from datetime import datetime
from openai import OpenAI

# ══════════════════════════════════════════════
#  🎨 تنظیمات ظاهر — تم روشن و شیک
# ══════════════════════════════════════════════
st.markdown("""
<style>
    /* فونت */
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif;
    }
    
    /* پس‌زمینه اصلی */
    .stApp {
        background: linear-gradient(135deg, #f8f9fb 0%, #eef2f7 100%);
    }
    
    /* متن‌ها */
    .stApp, .stMarkdown, .stChatMessage, p, h1, h2, h3, label {
        color: #1a1a2e !important;
    }
    
    /* عنوان اصلی */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    
    /* پیام کاربر */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, #e3f2fd 0%, #dbeafe 100%);
        border-radius: 18px;
        padding: 14px 18px;
        border: 1px solid #bfdbfe;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
    }
    
    /* پیام دستیار */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 18px;
        padding: 14px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    /* فیلد ورودی چت */
    .stChatInput textarea {
        color: #1a1a2e !important;
        background-color: #ffffff !important;
        border-radius: 14px !important;
        border: 2px solid #e2e8f0 !important;
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
    }
    .stChatInput textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* نوار کناری */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    /* دکمه‌ها */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        font-family: 'Vazirmatn', sans-serif;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
    }
    
    /* فایل آپلودر */
    [data-testid="stFileUploader"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 8px;
        border: 2px dashed #cbd5e1;
    }
    
    /* کدها */
    code {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 0.9em !important;
    }
    pre {
        background-color: #0f172a !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    pre code {
        background-color: transparent !important;
        color: #e2e8f0 !important;
    }
    
    /* جداکننده */
    hr {
        border-color: #e2e8f0;
    }
    
    /* متن‌های راهنما */
    .stCaption, small {
        color: #64748b !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  🔐 کلیدها — از Secrets خوانده می‌شوند
# ══════════════════════════════════════════════
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
PASSWORD = st.secrets["PASSWORD"]


# ══════════════════════════════════════════════
#  🤖 مدل‌ها — رایگان و به‌روز
# ══════════════════════════════════════════════
MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-vl-72b-instruct:free",
    "openrouter/free",
]

SYSTEM_PROMPT = (
    "تو یک دستیار هوشمند، دقیق و صمیمی برای برنامه‌نویسی و پاسخ به سوالات دانشی هستی. "
    "قوانین:\n"
    "۱. اگر کاربر فارسی نوشت، فارسی و ساده پاسخ بده.\n"
    "۲. اگر تصویر کد یا اسکرین‌شات بفرستد، دقیق تحلیل کن و راه‌حل بده.\n"
    "۳. کدها را همیشه داخل بلوک کد ``` قرار بده.\n"
    "۴. پاسخ‌ها را کوتاه، مفید و بدون حاشیه‌روی بده.\n"
    "۵. اگر از اینترنت اطلاعات می‌گیری، منبع را ذکر کن.\n"
    "۶. اگر چیزی را نمی‌دانی، صادقانه بگو نمی‌دانم."
)

# مسیر ذخیره تاریخچه
HISTORY_FILE = "chat_history.json"


# ══════════════════════════════════════════════
#  🛠 توابع کمکی
# ══════════════════════════════════════════════
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )


def load_history():
    """بارگذاری تاریخچه از فایل"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(messages):
    """ذخیره تاریخچه در فایل (بدون تصاویر)"""
    try:
        clean = []
        for m in messages:
            clean.append({
                "role": m["role"],
                "text": m.get("text", "")
            })
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(clean, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def init():
    if "messages" not in st.session_state:
        st.session_state.messages = load_history()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_model" not in st.session_state:
        st.session_state.current_model = MODELS[0]


def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; padding: 30px; background: white; border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08);'>
            <h1 style='font-size: 2.5rem; margin-bottom: 10px;'>🤖</h1>
            <h2 style='margin-bottom: 25px;'>چت‌بات شخصی</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        pwd = st.text_input("🔒 رمز عبور", type="password", placeholder="رمز را وارد کن...")
        if st.button("ورود", use_container_width=True):
            if pwd == PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ رمز اشتباه است")


def show_history():
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("img"):
                st.image(m["img"], width=300)
            st.markdown(m.get("text", ""))


def ask_stream(text, img_bytes=None, mime=None):
    """پاسخ Streaming — کلمه به کلمه"""
    client = get_client()
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]

    # تاریخچه
    for m in st.session_state.messages[-12:]:
        msgs.append({"role": m["role"], "content": m.get("text", "")})

    # پیام کاربر
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
                # 🌐 فعال‌سازی جستجوی وب
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
        page_title="چت‌بات شخصی من",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init()

    if not st.session_state.logged_in:
        login()
        return

    # ── هدر اصلی ──
    st.title("🤖 چت‌بات هوش مصنوعی شخصی")
    st.caption(f"🌟 مدل فعال: `{st.session_state.current_model}` — مجهز به جستجوی وب")

    # ── نوار کناری ──
    with st.sidebar:
        st.markdown("### 📤 تحلیل تصویر")
        st.caption("عکس کد یا اسکرین‌شات رو بفرست تا تحلیل کنم")
        
        up = st.file_uploader(
            "انتخاب تصویر",
            type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed",
        )
        if up:
            st.image(up, use_container_width=True)
            q = st.text_input("سوال درباره تصویر", value="این تصویر رو تحلیل کن")
            if st.button("🚀 ارسال تصویر", use_container_width=True):
                img = up.getvalue()
                mime = up.type or "image/png"
                st.session_state.messages.append(
                    {"role": "user", "text": q, "img": img}
                )
                with st.chat_message("user"):
                    st.image(img, width=300)
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
                save_history(st.session_state.messages)

        st.divider()

        # ── دکمه‌های کنترلی ──
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🧹 پاک کردن", use_container_width=True):
                st.session_state.messages = []
                save_history([])
                st.rerun()
        with col_b:
            if st.button("🚪 خروج", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.messages = []
                st.rerun()
        
        st.divider()
        st.caption("💡 ساخته شده با ❤️ برای خودم")

    # ── نمایش تاریخچه ──
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "سلام! 👋\n\n"
                "من دستیار شخصی تو هستم. می‌تونم:\n"
                "- 💻 به سوالات برنامه‌نویسی جواب بدم\n"
                "- 📷 عکس کد یا اسکرین‌شات رو تحلیل کنم\n"
                "- 🌐 از اینترنت اطلاعات به‌روز بگیرم\n"
                "- 📚 به سوالات دانشی پاسخ بدم\n\n"
                "هر سوالی داری بپرس! 🚀"
            )
    else:
        show_history()

    # ── ورودی چت ──
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
        save_history(st.session_state.messages)


main()
