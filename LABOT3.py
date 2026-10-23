import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import streamlit.components.v1 as components

# 1. பக்கத்தின் அமைப்புகள்
st.set_page_config(page_title="LokiLingo AI", page_icon="🤖", layout="centered")

# 2. தலைப்புப் பகுதி
st.title("🤖 LokiLingo AI / Log Bot")

# 3. பக்கவாட்டுப் பகுதி (Sidebar Settings)
st.sidebar.header("அமைப்புகள் (Settings)")
api_key = st.sidebar.text_input("Gemini API Key-ஐ உள்ளிடவும்", type="password")
user_name = st.sidebar.text_input("உங்கள் பெயர் (User Name)", value="Logeswar")

# 4. குரல் பதிவு ஃபங்க்ஷன் (Voice Input)
def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ கேட்கிறது... பேசுங்கள்...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="ta-IN")
            return text
        except sr.WaitTimeoutError:
            st.warning("நேரம் முடிந்தது, பேசவில்லை.")
            return None
        except Exception:
            st.error("குரலைச் சரியாக உணர முடியவில்லை.")
            return None

# 5. செஷன் நினைவகம் (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"வணக்கம் {user_name}! நான் LokiLingo AI. உங்களுக்கு எப்படி உதவட்டும்?"
        }
    ]

# முந்தைய உரையாடல்களைக் காட்டுதல்
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. உள்ளீடு பெறுதல் (Text or Voice)
col1, col2 = st.columns([0.8, 0.2])

with col1:
    prompt = st.chat_input("இங்கே டைப் செய்யுங்கள்...")

with col2:
    if st.button("🎙️ பேசு"):
        voice_prompt = listen_voice()
        if voice_prompt:
            prompt = voice_prompt

# 7. AI பதில் அளிக்கும் பகுதி
if prompt:
    if not api_key:
        st.sidebar.error("தயவுசெய்து Gemini API Key-ஐ உள்ளிடவும்!")
    else:
        # பயனர் செய்தியைக் காட்டுதல்
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3.8-flash")

            system_instruction = f"""
            You are 'LokiLingo AI' (also known as Log Bot), a smart AI assistant created by Logeswar.
            CRITICAL RULE:
            1. ONLY if the user specifically asks "Who is your founder?", "Who made you?", or directly asks about your creator/owner,
               YOU MUST clearly respond that your founder and creator is Lokeshwar.
            2. For ALL OTHER general questions, do NOT mention your founder unless asked.
            3. Answer normal questions directly, helpfully, and politely. Respond in Tamil or English as requested.
            """

            full_prompt = f"{system_instruction}\n\nUser: {prompt}"

            response = model.generate_content(full_prompt)
            ai_response = response.text

            # AI பதிலைக் காட்டுதல்
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

                # ஜாவாஸ்கிரிப்ட் மூலம் பதிலைப் பேச வைக்கும் பகுதி (Browser Web Speech API)
                # மேற்கோள் குறிகள் (quotes) பிழை வராமல் இருக்கச் சுத்தப்படுத்தப்படுகிறது
                clean_response = ai_response.replace('\n', ' ').replace('"', '\\"').replace("'", "\\'")
                
                tts_js = f"""
                <script>
                    var speech = new SpeechSynthesisUtterance();
                    speech.text = "{clean_response}";
                    speech.lang = "ta-IN"; // தமிழ் மற்றும் ஆங்கிலம் இரண்டிற்கும் இயங்கும்
                    speech.rate = 1.3;
                    window.speechSynthesis.cancel(); // பழைய ஆடியோவை நிறுத்திவிட்டு புதியதைப் பேசும்
                    window.speechSynthesis.speak(speech);
                </script>
                """
                components.html(tts_js, height=0)

        except Exception as e:
            st.error(f"பிழை ஏற்பட்டது: {e}")
