import gradio as gr
from pathlib import Path
from openai import OpenAI
from PyPDF2 import PdfReader

# Initialize the OpenAI client
client = OpenAI(
    api_key="api-key"
)

# Output directory for presentations
output_dir = Path(r"C:\TTS")
output_dir.mkdir(parents=True, exist_ok=True)


def process_file(file):
    """
    Reads and returns the content of a .txt or .pdf file.
    """
    try:
        if not file:
            print("No file uploaded. Proceeding with only the question...")
            return None  # No file content if no file is uploaded

        file_path = Path(file.name)
        if file_path.suffix == ".txt":
            print("Processing a .txt file...")
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_path.suffix == ".pdf":
            print("Processing a .pdf file...")
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() for page in reader.pages])
        else:
            print("Unsupported file format detected.")
            return "Unsupported file format. Please upload a .txt or .pdf file."
    except Exception as e:
        print(f"Error while processing file: {e}")
        return f"Error processing file: {e}"


def generate_ta_response(content, question):
    """
    Generate a Teaching Assistant-style response using OpenAI.
    """
    try:
        print("Generating a Teaching Assistant-style response...")
        combined_content = (
            question if not content else f"{content}\n\nUser's Question: {question}"
        )
        messages = [
            {
                "role": "system",
                "content": "You are an engaging and knowledgeable podcast host. Answer questions in a clear and instructional tone, providing step-by-step guidance.",
            },
            {"role": "user", "content": combined_content},
        ]
        response = client.chat.completions.create(
            model="gpt-4o",  # Use 'gpt-3.5-turbo' if 'gpt-4o' is not available
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating Teaching Assistant response: {e}")
        return f"Error generating TA response: {e}"


def save_tts_audio(ta_script):
    """
    Generate TTS audio for the Teaching Assistant response and save it.
    """
    try:
        print("Generating TTS audio...")
        speech_file_path = output_dir / "ta_explanation_audio.mp3"
        tts_response = client.audio.speech.create(
            model="tts-1", voice="alloy", input=ta_script
        )
        tts_response.stream_to_file(speech_file_path)
        print(f"TTS audio saved at: {speech_file_path}")
        return speech_file_path
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        return f"Error generating TTS audio: {e}"


def generate_reveal_js(ta_script):
    """
    Generate a stylish Reveal.js HTML presentation for the given TA response.
    """
    try:
        print("Generating Reveal.js HTML presentation...")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a creative and detail-oriented presentation designer skilled in Reveal.js. "
                    "Generate an aesthetically pleasing, modern, and highly engaging Reveal.js HTML presentation for the following explanation. "
                    "Use the 'moon' theme for a stylish look. Add animations for slide transitions (e.g., fade, zoom, or convex) "
                    "and text appearance (e.g., fade-in, slide-up). Incorporate cool and vibrant colors like blues, purples, and gradients "
                    "for slide backgrounds and elements. Ensure a clean layout with readable fonts, proper spacing, and elegant transitions. "
                    "Provide subtle visual effects like shadows or transparent overlays for a dynamic feel."
                ),
            },
            {"role": "user", "content": ta_script},
        ]
        response = client.chat.completions.create(
            model="gpt-4o",  # Use 'gpt-3.5-turbo' if 'gpt-4o' is not available
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating Reveal.js presentation: {e}")
        return f"Error generating Reveal.js presentation: {e}"


def embed_audio_in_reveal(reveal_script, speech_file_path):
    """
    Embed continuous audio playback into the Reveal.js HTML structure.
    """
    print("Embedding audio into Reveal.js presentation...")
    continuous_audio_html = f"""
    <audio id="background-audio" loop autoplay>
        <source src="{speech_file_path.name}" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
    <script>
        const audio = document.getElementById('background-audio');
        document.addEventListener('click', () => {{
            if (audio.paused) {{
                audio.play();
            }}
        }});
        Reveal.on('ready', () => {{
            if (audio.paused) {{
                audio.play().catch((err) => {{
                    console.log('Autoplay blocked. Audio will play after user interaction.');
                }});  
            }}
        }});
        Reveal.on('slidechanged', () => {{
            if (audio.paused) {{
                audio.play();
            }}
        }}); 
    </script>
    """
    return reveal_script.replace("</body>", f"{continuous_audio_html}\n</body>")


def save_reveal_presentation(reveal_script):
    """
    Save the generated Reveal.js presentation as an HTML file.
    """
    try:
        print("Saving Reveal.js presentation...")
        output_path = output_dir / "presentation.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(reveal_script)
        print(f"Reveal.js presentation saved at: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"Error saving Reveal.js presentation: {e}")
        return f"Error saving presentation: {e}"


def create_presentation(file, question):
    """
    Main function to process the file, handle the question, and create a presentation.
    """
    print("Processing the uploaded file (if any)...")
    file_content = process_file(file)

    if file_content == "Unsupported file format. Please upload a .txt or .pdf file.":
        return file_content, None

    # Generate TA response with the question
    ta_script = generate_ta_response(file_content, question)
    if "Error" in ta_script:
        return ta_script, None

    # Generate TTS audio
    speech_file_path = save_tts_audio(ta_script)
    if "Error" in str(speech_file_path):
        return speech_file_path, None

    # Generate Reveal.js presentation
    reveal_script = generate_reveal_js(ta_script)
    if "Error" in reveal_script:
        return reveal_script, None

    # Embed audio and save the presentation
    reveal_script = embed_audio_in_reveal(reveal_script, speech_file_path)
    presentation_path = save_reveal_presentation(reveal_script)
    if "Error" in presentation_path:
        return presentation_path, None

    return (
        f"Presentation generated successfully! You can download it below.",
        presentation_path,
    )


# Gradio interface
def gradio_interface(file, question):
    """
    Gradio interface handler.
    """
    result_message, presentation_path = create_presentation(file, question)
    download_link = (
        f"<a href='file/{presentation_path}' download>Download Your Presentation</a>"
        if presentation_path
        else ""
    )
    return result_message, download_link


# Launch Gradio app
with gr.Blocks() as app:
    gr.Markdown("# AI-Powered Stylish Presentation Generator")
    gr.Markdown(
        "Upload a .txt or .pdf file (optional) and ask a question related to it. "
        "This tool will generate a stylish presentation with continuous audio using Reveal.js."
    )

    with gr.Row():
        file_input = gr.File(label="Upload your file (.txt or .pdf)")
        question_input = gr.Textbox(label="Enter your question (required)")
        submit_button = gr.Button("Generate Presentation")

    output_message = gr.Textbox(label="Status", interactive=False)
    download_output = gr.HTML()

    submit_button.click(
        gradio_interface,
        inputs=[file_input, question_input],
        outputs=[output_message, download_output],
    )

app.launch()
