import streamlit as st
import base64
from openai import OpenAI
# ── تنظیمات ظاهر ──
st.markdown("""
<style>
    /* پس‌زمینه روشن */
    .stApp {
        background-color: #ffffff;
    }
    
    /* متن‌ها تیره */
    .stApp, .stMarkdown, .stChatMessage {
        color: #1a1a1a !important;
    }
    
    /* پیام کاربر */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #e3f2fd;
        border-radius: 12px;
        padding: 10px;
    }
    
    /* پیام دستیار */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #f5f5f5;
        border-radius: 12px;
        padding: 10px;
    }
    
    /* فیلد ورودی چت */
    .stChatInput textarea {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }
    
    /* نوار کناری */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
    }
    
    /* دکمه‌ها */
    .stButton > button {
        background-color: #1976d2;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)
# ============================
#  فقط این دو خط را عوض کن:
# ============================
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
PASSWORD = st.secrets["PASSWORD"]
# ============================
MODELS = ["openrouter/free"]
SYSTEM_PROMPT = (
    "تو یک دستیار هوشمند برای برنامه‌نویسی و پاسخ به سوالات هستی. "
    "اگر کاربر فارسی نوشت، فارسی و ساده پاسخ بده. "
    "اگر تصویر کد بفرستد، دقیق تحلیل کن و راه‌حل بده. "
    "کدها را داخل بلوک کد قرار بده."
)


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


def login():
    st.title("🔐 ورود به چت‌بات")
    pwd = st.text_input("رمز", type="password")
    if st.button("ورود"):
        if pwd == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("رمز اشتباه است")


def show_history():
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("img"):
                st.image(m["img"])
            st.markdown(m.get("text", ""))


def ask(text, img_bytes=None, mime=None):
    client = get_client()
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]

    for m in st.session_state.messages[-12:]:
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
            r = client.chat.completions.create(model=model, messages=msgs)
            return r.choices[0].message.content or "پاسخ خالی"
        except Exception as e:
            last_err = e
            continue
    raise last_err


def main():
    st.set_page_config(page_title="چت‌بات من", page_icon="🤖", layout="wide")
    init()

    if not st.session_state.logged_in:
        login()
        return

    st.title("🤖 چت‌بات هوش مصنوعی")

    if st.button("🧹 پاک کردن"):
        st.session_state.messages = []
        st.rerun()

    show_history()

    # ── چت متنی ──
    text = st.chat_input("پیام بنویس...")
    if text:
        st.session_state.messages.append({"role": "user", "text": text})
        with st.chat_message("user"):
            st.markdown(text)
        with st.chat_message("assistant"):
            with st.spinner("در حال فکر کردن..."):
                try:
                    ans = ask(text)
                except Exception as e:
                    ans = f"خطا: {e}"
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "text": ans})

    # ── تحلیل تصویر ──
    with st.sidebar:
        st.header("📤 تحلیل تصویر")
        up = st.file_uploader("عکس بفرست", type=["png", "jpg", "jpeg", "webp"])
        if up:
            st.image(up)
            q = st.text_input("سوال", value="این تصویر را تحلیل کن")
            if st.button("🚀 تحلیل"):
                img = up.getvalue()
                mime = up.type or "image/png"
                st.session_state.messages.append(
                    {"role": "user", "text": q, "img": img}
                )
                with st.chat_message("user"):
                    st.image(img)
                    st.markdown(q)
                with st.chat_message("assistant"):
                    with st.spinner("در حال تحلیل..."):
                        try:
                            ans = ask(q, img, mime)
                        except Exception as e:
                            ans = f"خطا: {e}"
                    st.markdown(ans)
                    st.session_state.messages.append(
                        {"role": "assistant", "text": ans}
                    )

        st.divider()
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()


main()
