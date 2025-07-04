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
def blog_content(text):
    try:
        response = model.generate_content(text)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def Pdf_Extraction(uploaded) -> str:
    doc = fitz.open(stream=uploaded.read(), filetype="pdf")
    return "".join(p.get_text() for p in doc)

def Pdf_Que(pdf_text: str, question: str) -> str:
    pt = f"PDF Content:\n{pdf_text}\n\nQuestion: {question}"
    return model.generate_content(pt).text  #ask to Gemini model to ans the que based on the PDF content

# 🖥️ Streamlit interface
def working_apps():
    # 🎨 Load and place logo
    try:
        logo = Image.open("logo-1.png")
        st.sidebar.image(logo, width=250)
    except:
        st.warning("⚠️ Logo file not found. Please check the path.")
        
    st.title("🧠 JaiBharatAI")
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
        status = st.empty()
        frames = ["🧠", "🔠", "🪔", "📜", "🇮🇳", "🕉️", "🪄"]
        for i in range(14):
            frame = frames[i % len(frames)]
            status.markdown(f"<div style='font-size: 24px;'>{frame} JaiBharatAI is thinking...</div>", unsafe_allow_html=True)
            time.sleep(0.25)
        with st.spinner("Finalizing..."):
            result = blog_content(text)
        status.markdown("✅ <b>Content generated successfully!</b>", unsafe_allow_html=True)
        return result

    if option == "PDF Reader":
        st.header("📄 Chat with your PDF")
        uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
        if uploaded_file:
            pdf_text = Pdf_Extraction(uploaded_file)
            question = st.text_input("Ask a question about the PDF:")
            if question:
                with st.spinner("Thinking..."):
                    answer = Pdf_Que(pdf_text[:100000], question)
                    st.markdown("**Answer:**")
                    
                    # ✅ Custom styled, non-editable result box
                    st.markdown("📄 **Result**")
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #1e1e1e;
                            color: white;
                            padding: 1em;
                            border-radius: 8px;
                            border: 1px solid #444;
                            font-size: 15px;
                            font-family: 'Courier New', monospace;
                            max-height: 300px;
                            overflow-y: auto;
                            white-space: pre-wrap;">
                            {answer.strip()}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                        
    elif option == "Chat":
        st.header("Content Generator")
        st.info(f"Prompt example: {placeholder_map[task]}")

        st.session_state.setdefault("blog_output", "")

        # ✅ Correct: Inside form
        with st.form("blog_form", clear_on_submit=False):
            input = st.text_area(
                "Enter your text:",
                placeholder=placeholder_map[task],
                height=100,
                key="input"# session_state key
            )
            generate = st.form_submit_button("📝 Generate Content")

        # ✅ Submission handling
        if generate:
            if input.strip() == "":
                st.warning("🚨 Please enter text before generating.")
            else:
                result = Loding_process(input)
                st.session_state.blog_output = result
                st.success("✅ Output Generated")

        # ✅ Output display
        if "blog_output" in st.session_state and st.session_state.blog_output:
            st.markdown("📄 **Result**")

            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    color: white;
                    padding: 1em;
                    border-radius: 8px;
                    border: 1px solid #444;
                    font-size: 15px;
                    font-family: 'Courier New', monospace;
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;">
                    {st.session_state.blog_output.strip()}
                </div>
                """,
                unsafe_allow_html=True
            )

    elif option == "About":
        st.write('''### 🤖 About JaiBharat AI

* **JaiBharat AI** is a culturally rooted, AI-powered writing assistant designed to help creators, students, and professionals generate high-quality blog content in seconds.

* Built using **Google Gemini 1.5 Flash**, it blends the power of generative AI with the richness of Indian identity — supporting both **English and Hindi** inputs.

* Whether you're brainstorming blog titles, expanding ideas, or chatting with PDFs, JaiBharat AI is your intelligent co-writer — fast, creative, and always in your voice.

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
            st.markdown("📄 **Result**")

            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    color: white;
                    padding: 1em;
                    border-radius: 8px;
                    border: 1px solid #444;
                    font-size: 15px;
                    font-family: 'Courier New', monospace;
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;">
                    {st.session_state.blog_output.strip()}
                </div>
                """,
                unsafe_allow_html=True
            )

    elif task == "Create Sections":
        st.info("Prompt example: Create blog sections for the topic: Future of Robotics")
        text = st.text_area("Enter your text:",
                            placeholder=placeholder_map[task], 
                            height=100,disabled=True)        
        if st.button("📝 Generate Content"):
            if text.strip() == "":
                st.warning("Please enter a text before generating.")
            else:
                result = Loding_process(text)
                st.success("✅ Output Generated")
            st.markdown("📄 **Result**")

            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    color: white;
                    padding: 1em;
                    border-radius: 8px;
                    border: 1px solid #444;
                    font-size: 15px;
                    font-family: 'Courier New', monospace;
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;">
                    {st.session_state.blog_output.strip()}
                </div>
                """,
                unsafe_allow_html=True
            )

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
            st.markdown("📄 **Result**")

            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    color: white;
                    padding: 1em;
                    border-radius: 8px;
                    border: 1px solid #444;
                    font-size: 15px;
                    font-family: 'Courier New', monospace;
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;">
                    {st.session_state.blog_output.strip()}
                </div>
                """,
                unsafe_allow_html=True
            )
            
def main():
    st.set_page_config(page_title="JaiBharatAI", layout="centered")

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

        st.markdown("### 👋 Welcome to JaiBharat AI")
        st.markdown("""<div style="text-align: center; font-size: 17px; margin-top: 10px;">👇 <strong>Click “Continue” to Launch JaiBharat AI</strong></div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)  # Adds vertical space
        if st.button("🚀 Continue", key="continue"):
            st.session_state.continue_clicked = True
            st.rerun()


    else:
        working_apps()

if __name__ == "__main__":
    main()
                
                

