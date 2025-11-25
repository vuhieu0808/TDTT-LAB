import datetime
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
import time
import shutil

API_KEY: str | None = ""

def copy_assets_file(src: str, dst: str):
    try:
        shutil.copy2(src, dst)
        print(f"Copied '{src}' to '{dst}'")
    except FileNotFoundError:
        print(f"Source file '{src}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    

def copy_assets():
    copy_assets_file('fetch-esco/data/data.json', 'assets/data.json')
    copy_assets_file('fetch-esco/data/skill.json', 'assets/skill.json')
    copy_assets_file('fetch-esco/data/knowledge.json', 'assets/knowledge.json')

def call_llm(model: str, thinking_budget: int, temperature: float) -> bool:
    print(f"Calling LLM with model: {model}, thinking_budget: {thinking_budget}, temperature: {temperature}")

    system_instruction = '''
    You are a sophisticated AI expert in IT skill taxonomy and curriculum design. Your task is to process a list of IT skill names and enrich it into a structured JSON format. You will analyze each skill and determine its proficiency level, key components, and essential prerequisites based on common industry standards.
    '''

    whole_knowledge_data = ""
    with open('assets/knowledge.json', 'r') as file:
        whole_knowledge_data = file.read()

    prompt = f'''
        {whole_knowledge_data}

        Generate a JSON array where each main skill is an object with the following structure:
        {{
        "knowledge": "<skill_name>",
        "level": "<level, from 1 to 10>",
        "detailed": ["List of detailed knowledge areas related to the main knowledge, like framework, library, protocols, ... Eg for 'JavaScript Framework' it could be ['React', 'Node.js', 'Vue.js']"],
        "prerequisites": ["<list_of_prerequisite_skills. Only main skill is needed here, no detailed knowledge areas>"]
        }}

        FIELD DEFINITIONS & CONSTRAINTS:
        skill (string): The name of the skill, copied exactly from the input.
        level (integer): An integer from 1 to 10 representing the typical proficiency level required for a professional role centered around this skill. Use this scale for consistency:
        1-2: Foundational/Academic knowledge.
        3-4: Junior-level proficiency; can perform basic tasks with supervision.
        5-6: Mid-level/Professional proficiency; can work independently on most tasks.
        7-8: Senior-level/Advanced proficiency; can lead projects and mentor others.
        9-10: Expert/Architect-level mastery; recognized as a thought leader, can innovate and set strategy.
        detailed (array of strings): A list of 5 to 7 of the most critical sub-skills, technologies, or core concepts that define this skill. Be specific and focus on the most important components.
        prerequisites (array of strings): A list of 1 to 3 direct, foundational skills required before someone can effectively learn the main skill. Only list the absolute most important prerequisites. Do not make up the main skill that are not in the provided list.
        prerequisites should not form a cycle. If a cycle is formed, make all the prerequisites in the cycle the same level.

        Only include smaller skills that are relevant to IT professionals and exclude any non-IT related skills. 
        Do not make up the main skill that are not in the provided list.
        Output in JSON format. Only output like a JSON file. Do not include any Markdown elements or code blocks.
    '''

    # print(prompt)

    client = genai.Client(api_key=API_KEY)

    start_time = time.perf_counter()
    try:
        response = client.models.generate_content(
            model=model, 
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                thinking_config=genai.types.ThinkingConfig(thinking_budget=thinking_budget)
            ),
        )
    except errors.ServerError as e:
        print(f"Server error: {e}")
        return False
    except Exception as e:
        print(f"An error occured: {e}")
        return False
    finally:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"LLM call took {execution_time:.2f} seconds")

    try:
        filename: str = f"knowledge2.json"
        with open(filename, 'w') as file:
            file.write(response.text)
        print(f"Data written to assets/knowledge2.json")
    except IOError as e:
        print(f"File IO error occurred: {e}")
        exit(1)
    return True

if __name__ == "__main__":
    print(os.getcwd())
    load_dotenv(".env")
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("GEMINI_API_KEY not found in .env")
        exit(1)
        
    copy_assets()

    if(not call_llm("gemini-flash-latest", 8192, 0.8)):
        print("Call failed, retrying...")
        if(not call_llm("gemini-flash-lite-latest", 0, 0.95)):
            print("Fatal error, exit now")
            exit(1)



    
    