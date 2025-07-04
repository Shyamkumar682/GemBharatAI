import time
import streamlit as st
import google.generativeai as genai
from PIL import ImageDraw, Image
import fitz  

# 🔐 Gemini API setup
API_KEY = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else None

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    st.error("❌ Gemini API key is missing. Please add it in Streamlit secrets to continue.")
    st.stop()
    

# 🧠 Blog generation function
def generate_blog_content(text):
    try:
        response = model.generate_content(text)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_pdf(uploaded) -> str:
    doc = fitz.open(stream=uploaded.read(), filetype="pdf")
    return "".join(p.get_text() for p in doc)

def ask_gemini(pdf_text: str, question: str) -> str:
    prompt = f"PDF Content:\n{pdf_text}\n\nQuestion: {question}"
    return model.generate_content(prompt).text

# 🖥️ Streamlit interface
def blog_app():
    # 🎨 Load and place logo
    try:
        logo = Image.open("logo.png")
        st.sidebar.image(logo, width=300)
    except:
        st.warning("⚠️ Logo file not found. Please check the path.")
        
    st.title("GemBharatAI")
    st.sidebar.title("Inspired by India and Gemini AI")
    
    with st.sidebar:
        if "option" not in st.session_state:
            st.session_state.option = "Chat"
        if "task" not in st.session_state:
            st.session_state.task = "Create Topics"

        st.markdown('<div class="sidebar-title">⚙️ Menu</div>', unsafe_allow_html=True)
        
        feature_icons = {
            "Chat": "🗪",
            "PDF Reader": "📑",
            "About": "🌐",
            "Features": "✨"
        }

        st.session_state.option = st.radio(
            label="",
            options=list(feature_icons.keys()),
            index=list(feature_icons.keys()).index(st.session_state.option),
            label_visibility="collapsed"
        )

        if st.session_state.option == "Chat":
            st.markdown('<div class="sidebar-title" style="margin-top:8px;">🛠️ Tasks Creation</div>', unsafe_allow_html=True)
            task_icons = {
                "Create Topics": "📝",
                "Create Sections": "📑",
                "Explain Content": "💡"
            }
            st.session_state.task = st.radio(
                label="",
                options=list(task_icons.keys()),
                index=list(task_icons.keys()).index(st.session_state.task),
                label_visibility="collapsed",
                key="task_radio"
            )

        elif st.session_state.option == "Features":
            st.markdown('<div class="sidebar-title" style="margin-top:8px;">✨ Special Features</div>', unsafe_allow_html=True)
            features_list = [
                "⚡ Gemini Integreated",
                "🚀 Quick Blog Generation",
                "🧠 AI-Powered Creator",
                "📄 PDF Chat",
                "💬 Hindi + English and 5+ Language Support",
                "🎯 Any Topic, Any Style",
                "📅 No Idea Required"
            ]
            for term in features_list:
                st.markdown(f'<div class="sidebar-term">{term}</div>', unsafe_allow_html=True)

        st.markdown('---')
        st.markdown('<div style="color: gray; font-size: 13px;">Designed by Shyam Kumar</div>', unsafe_allow_html=True)

    # --- Main Content ---
    option = st.session_state.option
    task = st.session_state.get("task", "")    # --- TOP OPTIONS ---
    placeholder_map = {
        "Create Topics": "e.g. Create blog post titles about Artificial Intelligence in education.",
        "Create Sections": "e.g. Create blog sections for the topic: Future of Robotics",
        "Explain Content": "e.g. Expand this section: Role of AI in autonomous vehicles"
        }
    
    def Loding_process(text):
        with st.spinner("⏳ Generating content..."):
            progressing = st.progress(0)
            for i in range(100):
                time.sleep(0.08)
                progressing.progress(i + 1)
            result = generate_blog_content(text)
        return result

    if option == "PDF Reader":
        
            st.header("📄 Chat with your PDF")
            uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
            if uploaded_file:
                pdf_text = extract_text_from_pdf(uploaded_file)
                question = st.text_input("Ask a question about the PDF:")
                if question:
                    with st.spinner("Thinking..."):
                        answer = ask_gemini(pdf_text[:100000], question)
                        st.markdown("**Answer:**")
                        st.write(answer)  
    elif option == "Chat":
        st.header("Content Generator")
        st.info(f"Prompt example: {placeholder_map[task]}")

        st.session_state.setdefault("blog_input", "")
        st.session_state.setdefault("blog_output", "")

        with st.form("blog_form", clear_on_submit=False):
            blog_input = st.text_area(
                "Enter your text:",
                value=st.session_state.blog_input,
                placeholder=placeholder_map[task],
                height=100,
                key="blog_input_area"
            )

            col1, col2 = st.columns([1, 1])
            generate = col1.form_submit_button("📝 Generate Content")

        if generate:
            if blog_input.strip() == "":
                st.warning("🚨 Please enter a text before generating.")
            else:
                st.session_state.blog_input = blog_input
                result = Loding_process(blog_input)
                st.session_state.blog_output = result
                st.success("✅ Output Generated")

        if st.session_state.blog_output:
            st.text_area("📄 Result", value=st.session_state.blog_output.strip(), height=300)

    elif option == "About":
        st.write('''### 🤖 About GemBharat AI

* **GemBharat AI** is a culturally rooted, AI-powered writing assistant designed to help creators, students, and professionals generate high-quality blog content in seconds.

* Built using **Google Gemini 1.5 Flash**, it blends the power of generative AI with the richness of Indian identity — supporting both **English and Hindi** inputs.

* Whether you're brainstorming blog titles, expanding ideas, or chatting with PDFs, GemBharat AI is your intelligent co-writer — fast, creative, and always in your voice.

---

**Key Features:**
-  Gemini-powered content generation
-  Chat with your PDFs
-  Hinglish + Hindi + English support
-  Instant blog writing with structured prompts
-  Inspired by Indian creators, for Indian creators

---

**Made with ❤️ by Shyam Kumar**  
_“Technology rooted in culture is the future.”_''')
        
    elif task == "Create Topics":
        st.info("Prompt example: Create blog post titles about Artificial Intelligence in education.")
        text = st.text_area("Enter your text:", 
                            placeholder=placeholder_map[task], 
                            height=100)        
        if st.button("📝 Generate Content"):
            if text.strip() == "":
                st.warning("🚨 Please enter a text before generating.")
            else:
                result = Loding_process(text)
                st.success("✅ Output Generated")
                st.text_area("📄 Result", value=result.strip(), height=300)

    elif task == "Create Sections":
        st.info("Prompt example: Create blog sections for the topic: Future of Robotics")
        text = st.text_area("Enter your text:",
                            placeholder=placeholder_map[task], 
                            height=100)        
        if st.button("📝 Generate Content"):
            if text.strip() == "":
                st.warning("Please enter a text before generating.")
            else:
                result = Loding_process(text)
                st.success("✅ Output Generated")
                st.text_area("📄 Result", value=result.strip(), height=300)

    elif task == "Explain Content":
        st.info("Prompt example: Expand this blog section: Role of AI in transportation")
        text = st.text_area("Enter your text:", 
                            placeholder=placeholder_map[task], 
                            height=100)
        if st.button("📝 Generate Content"):
            if text.strip() == "":
                st.warning("Please enter a text before generating.")
            else:
                result = Loding_process(text)
                st.success("✅ Output Generated")
                st.text_area("📄 Result", value=result.strip(), height=300)
def main():
    st.set_page_config(page_title="GemBharatAI", layout="centered")

    if "continue_clicked" not in st.session_state:
        st.session_state.continue_clicked = False

    if not st.session_state.continue_clicked:
        st.markdown("""
            <style>
            div.stButton > button {
                background-color: #ff4b4b;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 0.5em 1em;
                animation: pulse 1.5s infinite;
                border: none;
            }

            div.stButton > button:hover {
                background-color: #e04040;
                color: white;
                box-shadow: 0 0 12px rgba(255,75,75,0.6);
                transform: scale(1.02);
                transition: 0.3s ease;
            }

            @keyframes pulse {
                0% {box-shadow: 0 0 0 0 rgba(255,75,75, 0.5);}
                70% {box-shadow: 0 0 0 10px rgba(255,75,75, 0);}
                100% {box-shadow: 0 0 0 0 rgba(255,75,75, 0);}
            }
            </style>
        """, unsafe_allow_html=True)

        try:
            logo = Image.open("logo.png")
            st.image(logo, width=300)
        except:
            st.warning("⚠️ Logo not found.")

        st.markdown("### 👋 Welcome to GemBharat AI")
        st.markdown("Your intelligent co-writer awaits below.")
        st.markdown("""<div style="text-align: center; font-size: 17px; margin-top: 10px;">👇 <strong>Click “Continue” to Launch GemBharat AI</strong></div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)  # Adds vertical space
       
            if st.form_submit_button("🚀 Continue", key="continue_hidden"):
                st.session_state.continue_clicked = True
                st.rerun()

    else:
        blog_app()

if __name__ == "__main__":
    main()
                

