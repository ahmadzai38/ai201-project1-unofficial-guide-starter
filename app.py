import sys
from pathlib import Path

import gradio as gr

# Allow app.py to import files from src/
sys.path.append(str(Path(__file__).parent / "src"))

from generate import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    try:
        result = ask(question)

        answer = result["answer"]

        sources = "\n".join(
            f"- {source}" for source in result["sources"]
        )

        return answer, sources

    except Exception as e:
        return f"Error: {str(e)}", ""


with gr.Blocks() as demo:
    gr.Markdown("# The Unofficial Guide to Queens College CS Professors")
    gr.Markdown(
        "Ask a question about Queens College Computer Science professors, courses, exams, workload, or student advice."
    )

    question = gr.Textbox(
        label="Your question",
        placeholder="Example: What do students say about Jackson Yeh's CSCI240 exams and project?",
        lines=2,
    )

    ask_button = gr.Button("Ask")

    answer = gr.Textbox(label="Answer", lines=10)
    sources = gr.Textbox(label="Sources", lines=6)

    ask_button.click(
        handle_query,
        inputs=question,
        outputs=[answer, sources],
    )

    question.submit(
        handle_query,
        inputs=question,
        outputs=[answer, sources],
    )


demo.launch()