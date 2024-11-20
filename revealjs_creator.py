import os
from openai import OpenAI
from pathlib import Path

# Initialize the OpenAI client
client = OpenAI(
    api_key='api-key'
)

def get_user_input():
    """
    Get user input for the Teaching Assistant prompt.
    """
    return input("Please enter your question or prompt for the Teaching Assistant: ")

def generate_ta_response(client, user_message):
    """
    Generate the Teaching Assistant-style response using OpenAI API.
    """
    messages = [
        {"role": "system", "content": "You are an engaging and knowledgeable podcast host. Answer questions in a clear and instructional tone, providing step-by-step guidance."},
        {"role": "user", "content": user_message}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use 'gpt-3.5-turbo' if 'gpt-4o' is not available
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error generating Teaching Assistant response: {e}")

def save_tts_audio(client, ta_script, output_dir):
    """
    Generate TTS audio for the Teaching Assistant response and save it.
    """
    try:
        speech_file_path = output_dir / "ta_explanation_audio.mp3"
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ta_script
        )
        tts_response.stream_to_file(speech_file_path)
        return speech_file_path
    except Exception as e:
        raise RuntimeError(f"Error generating TTS audio: {e}")

def generate_reveal_js(client, ta_script):
    """
    Generate a Reveal.js HTML presentation for the Teaching Assistant response.
    """
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
        {"role": "user", "content": ta_script}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use 'gpt-3.5-turbo' if 'gpt-4o' is not available
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error generating Reveal.js presentation: {e}")

def embed_audio_in_reveal(reveal_script, speech_file_path):
    """
    Embed continuous audio playback into the Reveal.js HTML structure.
    """
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

def save_reveal_presentation(reveal_script, output_dir):
    """
    Save the final Reveal.js presentation HTML to the output directory.
    """
    reveal_file_path = output_dir / "ta_explanation_presentation.html"
    try:
        with open(reveal_file_path, "w", encoding="utf-8") as f:
            f.write(reveal_script)
        return reveal_file_path
    except Exception as e:
        raise RuntimeError(f"Error saving Reveal.js presentation: {e}")

def main():
    # Set up the output directory
    output_dir = Path(r"C:\TTS")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Get user input and generate response
        user_message = get_user_input()
        ta_script = generate_ta_response(client, user_message)
        print("\nGenerated Explanation (Teaching Assistant Style):\n")
        print(ta_script)

        # Generate and save TTS audio
        speech_file_path = save_tts_audio(client, ta_script, output_dir)
        print(f"\nAudio saved successfully at: {speech_file_path}")

        # Generate Reveal.js presentation
        reveal_script = generate_reveal_js(client, ta_script)

        # Embed audio and save the presentation
        reveal_script = embed_audio_in_reveal(reveal_script, speech_file_path)
        reveal_file_path = save_reveal_presentation(reveal_script, output_dir)
        print(f"\nReveal.js presentation saved successfully at: {reveal_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
