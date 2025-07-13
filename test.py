import os
from dotenv import load_dotenv
import streamlit as st
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Copy your Agent class and related functions here ---

def generate_ai_content(prompt):
    # ... (same as your original code)
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {str(e)}"

def complete_blog_post(title: str, content: str) -> str:
    # ... (same as your original code)
    try:
        os.makedirs("output", exist_ok=True)
        filename = f"output/{title.lower().replace(' ', '-')}.md"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        return "Task completed successfully"
    except Exception as e:
        return f"Error saving blog post: {str(e)}"

class Agent:
    def __init__(self, name: str, instructions, functions: list):
        self.name = name
        self.instructions = instructions
        self.functions = functions

    def generate_content(self, context):
        prompt = f"{self.instructions(context)}\n\nContext: {context}"
        return generate_ai_content(prompt)

def create_agents():
    return {
        "admin": Agent(
            name="Admin Agent",
            instructions=lambda ctx: f"""Initialize a blog post project comparing AI and non-AI solutions. 
            Focus on areas like efficiency, cost, accuracy, and human factors. Topic: {ctx.get('topic')}""",
            functions=["transfer_to_planner"]
        ),
        "planner": Agent(
            name="Planner Agent",
            instructions=lambda ctx: f"""Create a detailed outline comparing AI and non-AI approaches for: {ctx.get('topic')}
            Include sections like:
            1. Introduction to the debate
            2. Key comparison metrics
            3. Case studies/examples
            4. Pros and cons of each
            5. Future outlook
            6. Conclusion""",
            functions=["transfer_to_researcher"]
        ),
        "researcher": Agent(
            name="Researcher Agent",
            instructions=lambda ctx: f"""Provide comprehensive research comparing AI and non-AI for: {ctx.get('topic')}
            Include:
            - Statistical comparisons
            - Real-world examples
            - Expert opinions
            - Cost-benefit analyses
            - Ethical considerations""",
            functions=["transfer_to_writer"]
        ),
        "writer": Agent(
            name="Writer Agent",
            instructions=lambda ctx: f"""Write a detailed 1500+ word blog post comparing AI and non-AI solutions for: {ctx.get('topic')}
            Use the outline and research provided.
            Include:
            - Clear section headings
            - Data visualizations (describe them)
            - Balanced arguments
            - Practical recommendations""",
            functions=["transfer_to_editor"]
        ),
        "editor": Agent(
            name="Editor Agent",
            instructions=lambda ctx: f"""Edit this AI vs non-AI comparison post about {ctx.get('topic')}:
            - Ensure technical accuracy
            - Improve readability
            - Check argument balance
            - Verify citations
            - Optimize SEO elements""",
            functions=[complete_blog_post]
        )
    }

# --- Streamlit UI code ---

def run_streamlit_workflow():
    st.title("AI vs Non-AI Blog Post Generator")
    st.write("Compare AI and non-AI solutions with automated blog generation.")

    topic = st.text_input("Enter the blog post topic (AI vs non-AI comparison):", 
                         value="AI vs Human Customer Service: Which Performs Better?")
    run_button = st.button("Generate Blog Post")

    if run_button and topic:
        agents = create_agents()
        context = {"topic": topic, "content": {}}
        outputs = {}

        progress = st.progress(0)
        agent_steps = ["admin", "planner", "researcher", "writer", "editor"]

        for idx, agent_name in enumerate(agent_steps):
            agent = agents[agent_name]
            with st.spinner(f"{agent.name} working..."):
                result = agent.generate_content(context)
                context["content"][agent_name] = result
                outputs[agent_name] = result
                progress.progress((idx + 1) / len(agent_steps))
                st.markdown(f"### {agent.name} Output")
                st.code(result, language="markdown")

        # Save the final output
        final_result = complete_blog_post(
            title=topic,
            content=context["content"]["writer"]
        )
        st.success(final_result)
        st.markdown("#### Download your blog post:")
        filename = f"output/{topic.lower().replace(' ', '-')}.md"
        with open(filename, "r", encoding="utf-8") as file:
            st.download_button(
                label="Download Markdown",
                data=file.read(),
                file_name=f"{topic.lower().replace(' ', '-')}.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    run_streamlit_workflow()
