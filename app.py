#!/usr/bin/env python3
"""
Feature Prioritization Framework - Web Interface
A Flask-based web application for the feature prioritization framework.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
from datetime import datetime
import os
from feature_prioritization_framework import FeaturePrioritizationFramework, FeatureMetrics

# Configure matplotlib for web use
plt.switch_backend('Agg')
sns.set_palette("husl")

app = Flask(__name__)
app.secret_key = 'feature_prioritization_secret_key'

# Global framework instance
framework = FeaturePrioritizationFramework()

@app.route('/')
def index():
    """Main page with feature input form"""
    return render_template('index.html')

@app.route('/add_feature', methods=['POST'])
def add_feature():
    """Add a feature to the framework"""
    try:
        # Get form data
        feature_name = request.form['feature_name']
        product_impact_score = float(request.form['product_impact_score'])
        revenue_potential = float(request.form['revenue_potential'])
        time_savings_hours = float(request.form['time_savings_hours'])
        development_cost = float(request.form['development_cost'])
        implementation_time_weeks = float(request.form['implementation_time_weeks'])
        user_impact_percentage = float(request.form['user_impact_percentage'])
        market_demand_score = float(request.form['market_demand_score'])
        technical_complexity = float(request.form['technical_complexity'])
        strategic_alignment = float(request.form['strategic_alignment'])
        risk_score = float(request.form['risk_score'])
        
        # Create feature metrics
        metrics = FeatureMetrics(
            feature_name=feature_name,
            product_impact_score=product_impact_score,
            revenue_potential=revenue_potential,
            time_savings_hours=time_savings_hours,
            development_cost=development_cost,
            implementation_time_weeks=implementation_time_weeks,
            user_impact_percentage=user_impact_percentage,
            market_demand_score=market_demand_score,
            technical_complexity=technical_complexity,
            strategic_alignment=strategic_alignment,
            risk_score=risk_score
        )
        
        # Add to framework
        framework.add_feature(metrics)
        
        flash(f'Feature "{feature_name}" added successfully!', 'success')
        return redirect(url_for('index'))
        
    except ValueError as e:
        flash(f'Error: {e}. Please enter valid numeric values.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display analysis results"""
    if not framework.features:
        flash('No features added yet. Please add some features first.', 'warning')
        return redirect(url_for('index'))
    
    # Get comparison data
    df = framework.compare_features()
    
    # Get individual analytics
    analytics = []
    for feature in framework.features:
        analytics.append(framework.get_feature_analytics(feature))
    
    return render_template('results.html', 
                         comparison_data=df.to_dict('records'),
                         analytics=analytics,
                         total_features=len(framework.features))

@app.route('/api/visualizations')
def get_visualizations():
    """Generate and return visualization images as base64"""
    if not framework.features:
        return jsonify({'error': 'No features to visualize'})
    
    try:
        # Generate visualizations
        images = generate_web_visualizations()
        return jsonify(images)
    except Exception as e:
        return jsonify({'error': str(e)})

def generate_web_visualizations():
    """Generate visualizations for web display"""
    df = framework.compare_features()
    images = {}
    
    # 1. Priority Score Comparison
    plt.figure(figsize=(10, 6))
    plt.barh(df['feature_name'], df['priority_score'], color='skyblue')
    plt.title('Priority Score Comparison', fontsize=14, fontweight='bold')
    plt.xlabel('Priority Score')
    plt.tight_layout()
    
    # Save to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    images['priority_comparison'] = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # 2. Viability vs ROI
    plt.figure(figsize=(10, 6))
    plt.scatter(df['viability_score'], df['roi_score'], s=100, alpha=0.7)
    plt.title('Viability vs ROI', fontsize=14, fontweight='bold')
    plt.xlabel('Viability Score')
    plt.ylabel('ROI Score')
    
    # Add feature names as annotations
    for i, row in df.iterrows():
        plt.annotate(row['feature_name'], 
                    (row['viability_score'], row['roi_score']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    images['viability_roi'] = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # 3. Risk vs Priority Matrix
    plt.figure(figsize=(10, 6))
    risk_levels = df['risk_level'].map({'LOW': 1, 'MEDIUM': 2, 'HIGH': 3})
    plt.scatter(risk_levels, df['priority_score'], s=100, alpha=0.7)
    plt.title('Risk vs Priority Score', fontsize=14, fontweight='bold')
    plt.xlabel('Risk Level')
    plt.ylabel('Priority Score')
    plt.xticks([1, 2, 3], ['LOW', 'MEDIUM', 'HIGH'])
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    images['risk_priority'] = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # 4. Recommendation Distribution
    plt.figure(figsize=(8, 8))
    recommendation_counts = df['recommendation'].value_counts()
    plt.pie(recommendation_counts.values, labels=recommendation_counts.index, autopct='%1.1f%%')
    plt.title('Recommendation Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    images['recommendation_distribution'] = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return images

@app.route('/export')
def export_results():
    """Export results to JSON"""
    if not framework.features:
        flash('No features to export', 'warning')
        return redirect(url_for('index'))
    
    try:
        filename = f"feature_prioritization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        framework.export_results(filename)
        flash(f'Results exported to {filename}', 'success')
    except Exception as e:
        flash(f'Export error: {e}', 'error')
    
    return redirect(url_for('results'))

@app.route('/clear')
def clear_features():
    """Clear all features"""
    framework.features = []
    flash('All features cleared', 'success')
    return redirect(url_for('index'))

@app.route('/demo')
def load_demo():
    """Load demo features"""
    from feature_prioritization_framework import create_sample_features
    
    # Clear existing features
    framework.features = []
    
    # Add demo features
    sample_features = create_sample_features()
    for feature in sample_features:
        framework.add_feature(feature)
    
    flash('Demo features loaded successfully!', 'success')
    return redirect(url_for('results'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 