import gradio as gr
import requests
import json


API_URL = "http://127.0.0.1:8001/search"


def perform_search(query, top_k, initial_k):
    if not query.strip():
        return ""

    payload = {"query": query, "top_k": int(top_k), "initial_k": int(initial_k)}

    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()

        results = data.get("results", [])

        html = ""

        for item in results:
            meta = item["meta"]
            title = meta.get("title", "")
            authors = meta.get("authors", "")
            categories = meta.get("categories", "")
            date = meta.get("update_date", "")
            abstract = meta.get("abstract", "")[:350] + "..."

            html += f"""
            <div style='padding:15px 0; border-bottom:1px solid #ddd;'>
                <div style='font-size:20px; font-weight:600;'>
                    <a href="https://arxiv.org/abs/{item['id']}" 
                       target="_blank" 
                       style='color:#0047ab; text-decoration:none;'>
                        {title}
                    </a>
                </div>

                <div style='font-size:14px; color:#444; margin-top:4px;'>
                    {authors}
                </div>

                <div style='font-size:13px; color:#777; margin-top:3px;'>
                    {categories} &nbsp;·&nbsp; {date}
                </div>

                <div style='font-size:14px; margin-top:10px; line-height:1.5; color:#222;'>
                    {abstract}
                </div>
            </div>
            """

        return html

    except Exception as e:
        return f"<div>Error: {str(e)}</div>"


light_css = """
<style>
body, .gradio-container {
    background: white !important;
    color: black !important;
}

input, textarea {
    background: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
}

.gr-button {
    background: #e6e6e6 !important;
    color: #000 !important;
    border: 1px solid #bbb !important;
}

.gr-button:hover {
    background: #dcdcdc !important;
}
</style>
"""


with gr.Blocks(title="Retrieval-система по статьям с arXiv") as demo:

    gr.HTML(light_css)

    gr.Markdown("<h1 style='color:#000;'>Retrieval-система по статьям с arXiv</h1>")

    with gr.Row():
        topk = gr.Slider(
            1,
            10,
            value=5,
            step=1,
            label="Top-K",
            info="Сколько статей показать в результате",
        )
        initk = gr.Slider(
            5,
            200,
            value=15,
            step=5,
            label="Initial-K",
            info="Сколько кандидатов отбирается перед реранкингом",
        )

    query_box = gr.Textbox(placeholder="Search papers...", label="", lines=1)

    output = gr.HTML()

    query_box.submit(perform_search, inputs=[query_box, topk, initk], outputs=output)


demo.launch(server_name="127.0.0.1", server_port=7861)
