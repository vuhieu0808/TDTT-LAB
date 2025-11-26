from flask import Flask, request, jsonify
from flask_cors import CORS
from data_loader import DataLoader
from data_type import *
from job_matcher import JobMatcher 
from roadmap_generator import RoadmapGenerator
from ai_project_suggester import AIProjectSuggester

app = Flask(__name__)
CORS(app)
_data_loader: DataLoader
_job_matcher: JobMatcher
_roadmap_generator: RoadmapGenerator
_ai_project_suggester: AIProjectSuggester

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok"}), 200

@app.route('/get-job', methods=['GET'])
def get_job():
    job_name: str = request.args.get('name', '')
    job: Job | None = _data_loader.get_job_by_name(job_name)
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job.to_dict()), 200

@app.route('/get-knowledge', methods=['GET'])
def get_knowledge():
    knowledge_name: str = request.args.get('name', '')
    knowledge: Knowledge | None = _data_loader.get_knowledge_info(knowledge_name)
    if knowledge is None:
        return jsonify({"error": "Knowledge not found"}), 404

    return jsonify(knowledge.to_dict()), 200

@app.route('/search-job', methods=['GET'])
def search_jobs():
    keyword: str = request.args.get('keyword', '')
    limit: int = int(request.args.get('limit', '30'))
    job_name_list: List[str] = _data_loader.search_jobs(keyword, limit)
    return jsonify(job_name_list), 200

@app.route('/search-knowledge', methods=['GET'])
def search_knowledge():
    keyword: str = request.args.get('keyword', '')
    limit: int = int(request.args.get('limit', '30'))
    knowledge_name_list: List[str] = _data_loader.search_knowledges(keyword, limit)
    return jsonify(knowledge_name_list), 200

@app.route('/search-skill', methods=['GET'])
def search_skill():
    skill: str = request.args.get('keyword', '')
    limit: int = int(request.args.get('limit', '30'))
    skill_name_list: List[str] = _data_loader.search_skill(skill, limit)
    return jsonify(skill_name_list), 200

if __name__ == '__main__':
    _data_loader = DataLoader()
    app.run(port=6969)