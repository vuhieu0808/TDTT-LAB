en | [vi](README.md)

# 🎓 Student Career Helper

## Overview
Desktop application to help recent graduates:
  - Find jobs that match current skills and knowledge
  - Generate a learning roadmap to reach a target job
  - Suggest practice projects to consolidate learning

## ✨ Features
### Job matching
  - Enter your skills and knowledge
  - System ranks jobs by fit score
  - Shows missing and matched items
### Roadmap generation
  - Enter a target job and your current skills/knowledge
  - Generates an ordered learning plan using dependency graphs
    - Topological sort to order items
    - Cycle detection; items in cycles are suggested to learn in parallel
    - Sort within groups by level and estimate learning time
  - Optional: request project suggestions from Google Gemini AI

## Dependencies:
- Python 3.8 or later
- Dart SDK 3.9 or later

## 🚀 Installation & run
### 0. Setup
- On project base folder, create `.env` file with API key (example in [.env.example](.env.example))
```
GOOGLE_API_KEY=AIzaSy....
```

- Ensure you already have Python installed and you are in a Python virtual environment 

- Install Python dependencies
```
pip install -r requirements.txt
```

### 0.5. About the precompiled data
- Data has been precompiled and saved in [assets](assets) directory. If you wish to regenerate on your own, continue to step 1. If you don't, jump to step 3

### 1. Fetch data from ESCO
- Ensure you already have Dart installed
- Navigate to [fetch-esco](fetch-esco) folder
- Install dependencies
```
dart pub get
```
- Run
```
dart run
```

Data is written is `data/` folder
- `data/data.json`: full job description
- `data/knowledge.json`: Unique list of knowledges appear in the dataset
- `data/skill.json`: Unique list of skills appear in the dataset

### 2. Prepare assets
- Navigate back to project base folder
- Run 
```
python ./make-assets/make-assets.py
```
On Linux you might need to run with `python3`

This operation will 
- copy the fetched ESCO data and copy to `assets` folder
- generate additional data from LLM, the write to `assets/knowledge2.json`

### 3. Run
- Navigate to project base folder
- Run 
```
python ./src/main_app.py
```
On Linux you might need to run with `python3`. The application's starting process can be very slow. Be patient!

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE).

## A.I. acknowledgement
- The project utilising Google Gemini (GenAI) to enrich dataset items and generate project suggestions via the [Google GenAI API](https://ai.google.dev/gemini-api/docs/libraries)
- Gemini 2.5 Flash/Pro, GPT-5 and Claude Sonnet 4.5 LLM provided by Github Copilot for general coding assistance