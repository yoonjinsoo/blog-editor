from flask import Blueprint, jsonify, request
from typing import Dict, List
from ..services.fact_extractor import FactExtractor
from ..services.content_analyzer import ContentAnalyzer
from ..services.quality_checker import QualityChecker

api = Blueprint('api', __name__)
fact_extractor = FactExtractor()
content_analyzer = ContentAnalyzer()
quality_checker = QualityChecker()

@api.route('/api/factual-contents', methods=['GET'])
def get_factual_contents():
    filters = {
        'min_factual_score': float(request.args.get('minFactualScore', 0.7)),
        'min_relevance_score': float(request.args.get('minRelevanceScore', 0.7)),
        'categories': request.args.getlist('selectedCategories[]'),
        'date_range': {
            'start': request.args.get('dateRange[start]'),
            'end': request.args.get('dateRange[end]')
        }
    }
    
    contents = content_analyzer.get_filtered_contents(filters)
    return jsonify(contents)

@api.route('/api/content-metrics/<content_id>', methods=['GET'])
def get_content_metrics(content_id: str):
    metrics = content_analyzer.analyze_content_metrics(content_id)
    return jsonify(metrics)

@api.route('/api/extracted-facts/<content_id>', methods=['GET'])
def get_extracted_facts(content_id: str):
    facts = fact_extractor.extract_facts_from_content(content_id)
    return jsonify(facts)

@api.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    stats = {
        'total_articles': content_analyzer.get_total_articles(),
        'high_quality_articles': content_analyzer.get_high_quality_articles(),
        'fact_distribution': fact_extractor.get_fact_distribution(),
        'source_distribution': content_analyzer.get_source_distribution()
    }
    return jsonify(stats)

@api.route('/api/facts/<fact_id>/verify', methods=['PUT'])
def update_fact_verification(fact_id: str):
    data = request.get_json()
    fact_extractor.update_fact_verification(fact_id, data['verified'])
    return jsonify({'status': 'success'})

@api.route('/api/export-facts', methods=['GET'])
def export_verified_facts():
    format_type = request.args.get('format', 'json')
    facts = fact_extractor.export_verified_facts(format_type)
    return jsonify(facts)
