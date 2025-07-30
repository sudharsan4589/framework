#!/usr/bin/env python3
"""
Feature Prioritization Framework Tool
A comprehensive tool for evaluating feature viability based on product impact, 
revenue generation, and time savings.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import sys
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ImpactLevel(Enum):
    """Impact level enumeration for scoring"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class FeatureMetrics:
    """Data class for feature metrics"""
    feature_name: str
    product_impact_score: float  # 1-10 scale
    revenue_potential: float  # Expected revenue in currency
    time_savings_hours: float  # Hours saved per week
    development_cost: float  # Development cost in currency
    implementation_time_weeks: float  # Weeks to implement
    user_impact_percentage: float  # Percentage of users affected
    market_demand_score: float  # 1-10 scale
    technical_complexity: float  # 1-10 scale
    strategic_alignment: float  # 1-10 scale
    risk_score: float  # 1-10 scale (lower is better)

class FeaturePrioritizationFramework:
    """Main framework class for feature prioritization"""
    
    def __init__(self):
        self.features = []
        self.weights = {
            'product_impact': 0.25,
            'revenue_potential': 0.30,
            'time_savings': 0.15,
            'user_impact': 0.10,
            'market_demand': 0.10,
            'strategic_alignment': 0.05,
            'technical_complexity': -0.05,  # Negative weight
            'risk_score': -0.10  # Negative weight
        }
        
    def add_feature(self, metrics: FeatureMetrics) -> None:
        """Add a feature to the evaluation framework"""
        self.features.append(metrics)
        
    def calculate_roi_score(self, metrics: FeatureMetrics) -> float:
        """Calculate ROI score based on revenue and cost"""
        if metrics.development_cost <= 0:
            return 0
        return (metrics.revenue_potential / metrics.development_cost) * 100
        
    def calculate_time_efficiency_score(self, metrics: FeatureMetrics) -> float:
        """Calculate time efficiency score"""
        # Normalize time savings (assuming 40 hours per week as baseline)
        normalized_time_savings = min(metrics.time_savings_hours / 40, 1.0)
        return normalized_time_savings * 10
        
    def calculate_viability_score(self, metrics: FeatureMetrics) -> float:
        """Calculate overall viability score"""
        scores = {
            'product_impact': metrics.product_impact_score,
            'revenue_potential': min(metrics.revenue_potential / 10000, 10),  # Normalize to 10k max
            'time_savings': self.calculate_time_efficiency_score(metrics),
            'user_impact': metrics.user_impact_percentage / 10,  # Convert percentage to 0-10 scale
            'market_demand': metrics.market_demand_score,
            'strategic_alignment': metrics.strategic_alignment,
            'technical_complexity': 11 - metrics.technical_complexity,  # Invert for positive scoring
            'risk_score': 11 - metrics.risk_score  # Invert for positive scoring
        }
        
        weighted_score = sum(scores[key] * self.weights[key] for key in scores.keys())
        return min(max(weighted_score, 0), 10)  # Clamp between 0-10
        
    def calculate_priority_score(self, metrics: FeatureMetrics) -> float:
        """Calculate priority score considering viability and implementation factors"""
        viability = self.calculate_viability_score(metrics)
        roi = self.calculate_roi_score(metrics)
        
        # Implementation efficiency (faster implementation = higher score)
        implementation_efficiency = max(0, 10 - metrics.implementation_time_weeks)
        
        # Combined score
        priority_score = (viability * 0.4 + roi * 0.3 + implementation_efficiency * 0.3)
        return min(max(priority_score, 0), 10)
        
    def get_feature_analytics(self, metrics: FeatureMetrics) -> Dict:
        """Get comprehensive analytics for a feature"""
        return {
            'feature_name': metrics.feature_name,
            'viability_score': round(self.calculate_viability_score(metrics), 2),
            'priority_score': round(self.calculate_priority_score(metrics), 2),
            'roi_score': round(self.calculate_roi_score(metrics), 2),
            'time_efficiency_score': round(self.calculate_time_efficiency_score(metrics), 2),
            'product_impact_level': self._get_impact_level(metrics.product_impact_score),
            'risk_level': self._get_risk_level(metrics.risk_score),
            'recommendation': self._get_recommendation(metrics),
            'key_metrics': {
                'revenue_potential': metrics.revenue_potential,
                'time_savings_per_week': metrics.time_savings_hours,
                'development_cost': metrics.development_cost,
                'implementation_time': f"{metrics.implementation_time_weeks} weeks",
                'user_impact': f"{metrics.user_impact_percentage}%"
            }
        }
        
    def _get_impact_level(self, score: float) -> str:
        """Get impact level based on score"""
        if score >= 8:
            return "CRITICAL"
        elif score >= 6:
            return "HIGH"
        elif score >= 4:
            return "MEDIUM"
        else:
            return "LOW"
            
    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score"""
        if score <= 3:
            return "LOW"
        elif score <= 6:
            return "MEDIUM"
        else:
            return "HIGH"
            
    def _get_recommendation(self, metrics: FeatureMetrics) -> str:
        """Get recommendation based on scores"""
        viability = self.calculate_viability_score(metrics)
        priority = self.calculate_priority_score(metrics)
        
        if viability >= 8 and priority >= 8:
            return "STRONGLY RECOMMEND"
        elif viability >= 6 and priority >= 6:
            return "RECOMMEND"
        elif viability >= 4 and priority >= 4:
            return "CONSIDER"
        else:
            return "NOT RECOMMENDED"
            
    def compare_features(self) -> pd.DataFrame:
        """Compare all features and return a DataFrame"""
        if not self.features:
            return pd.DataFrame()
            
        comparison_data = []
        for feature in self.features:
            analytics = self.get_feature_analytics(feature)
            comparison_data.append(analytics)
            
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('priority_score', ascending=False)
        return df
        
    def generate_visualizations(self, save_path: str = None) -> None:
        """Generate comprehensive visualizations"""
        if not self.features:
            print("No features to visualize")
            return
            
        df = self.compare_features()
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Feature Prioritization Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Priority Score Comparison
        axes[0, 0].barh(df['feature_name'], df['priority_score'], color='skyblue')
        axes[0, 0].set_title('Priority Score Comparison')
        axes[0, 0].set_xlabel('Priority Score')
        
        # 2. Viability vs ROI
        axes[0, 1].scatter(df['viability_score'], df['roi_score'], s=100, alpha=0.7)
        axes[0, 1].set_title('Viability vs ROI')
        axes[0, 1].set_xlabel('Viability Score')
        axes[0, 1].set_ylabel('ROI Score')
        
        # Add feature names as annotations
        for i, row in df.iterrows():
            axes[0, 1].annotate(row['feature_name'], 
                               (row['viability_score'], row['roi_score']),
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 3. Time Efficiency vs Product Impact
        axes[0, 2].scatter(df['key_metrics'].apply(lambda x: x['time_savings_per_week']), 
                           df['key_metrics'].apply(lambda x: x['revenue_potential']), 
                           s=100, alpha=0.7)
        axes[0, 2].set_title('Time Savings vs Revenue Potential')
        axes[0, 2].set_xlabel('Time Savings (hours/week)')
        axes[0, 2].set_ylabel('Revenue Potential')
        
        # 4. Risk vs Reward Matrix
        risk_levels = df['risk_level'].map({'LOW': 1, 'MEDIUM': 2, 'HIGH': 3})
        axes[1, 0].scatter(risk_levels, df['priority_score'], s=100, alpha=0.7)
        axes[1, 0].set_title('Risk vs Priority Score')
        axes[1, 0].set_xlabel('Risk Level')
        axes[1, 0].set_ylabel('Priority Score')
        axes[1, 0].set_xticks([1, 2, 3])
        axes[1, 0].set_xticklabels(['LOW', 'MEDIUM', 'HIGH'])
        
        # 5. Recommendation Distribution
        recommendation_counts = df['recommendation'].value_counts()
        axes[1, 1].pie(recommendation_counts.values, labels=recommendation_counts.index, autopct='%1.1f%%')
        axes[1, 1].set_title('Recommendation Distribution')
        
        # 6. Feature Metrics Heatmap
        metrics_for_heatmap = df[['viability_score', 'priority_score', 'roi_score', 'time_efficiency_score']]
        sns.heatmap(metrics_for_heatmap.T, annot=True, cmap='YlOrRd', ax=axes[1, 2])
        axes[1, 2].set_title('Feature Metrics Heatmap')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        else:
            plt.show()
            
    def export_results(self, filename: str = None) -> None:
        """Export results to JSON file"""
        if not self.features:
            print("No features to export")
            return
            
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_features': len(self.features),
            'framework_weights': self.weights,
            'feature_analytics': [self.get_feature_analytics(feature) for feature in self.features],
            'comparison_data': self.compare_features().to_dict('records')
        }
        
        if not filename:
            filename = f"feature_prioritization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"Results exported to {filename}")

def create_sample_features() -> List[FeatureMetrics]:
    """Create sample features for demonstration"""
    return [
        FeatureMetrics(
            feature_name="Advanced Analytics Dashboard",
            product_impact_score=8.5,
            revenue_potential=50000,
            time_savings_hours=15,
            development_cost=25000,
            implementation_time_weeks=8,
            user_impact_percentage=75,
            market_demand_score=9.0,
            technical_complexity=7.0,
            strategic_alignment=9.0,
            risk_score=4.0
        ),
        FeatureMetrics(
            feature_name="Mobile App Integration",
            product_impact_score=7.0,
            revenue_potential=35000,
            time_savings_hours=8,
            development_cost=15000,
            implementation_time_weeks=6,
            user_impact_percentage=60,
            market_demand_score=8.5,
            technical_complexity=6.0,
            strategic_alignment=8.0,
            risk_score=5.0
        ),
        FeatureMetrics(
            feature_name="Automated Reporting System",
            product_impact_score=6.5,
            revenue_potential=20000,
            time_savings_hours=20,
            development_cost=12000,
            implementation_time_weeks=4,
            user_impact_percentage=85,
            market_demand_score=7.5,
            technical_complexity=4.0,
            strategic_alignment=7.0,
            risk_score=3.0
        ),
        FeatureMetrics(
            feature_name="AI-Powered Chatbot",
            product_impact_score=9.0,
            revenue_potential=80000,
            time_savings_hours=25,
            development_cost=40000,
            implementation_time_weeks=12,
            user_impact_percentage=90,
            market_demand_score=9.5,
            technical_complexity=9.0,
            strategic_alignment=9.5,
            risk_score=7.0
        )
    ]

def main():
    """Main function to run the framework"""
    parser = argparse.ArgumentParser(description='Feature Prioritization Framework')
    parser.add_argument('--demo', action='store_true', help='Run with demo data')
    parser.add_argument('--export', type=str, help='Export results to file')
    parser.add_argument('--visualize', type=str, help='Save visualization to file')
    
    args = parser.parse_args()
    
    # Initialize framework
    framework = FeaturePrioritizationFramework()
    
    if args.demo:
        # Add sample features
        sample_features = create_sample_features()
        for feature in sample_features:
            framework.add_feature(feature)
            
        print("=== Feature Prioritization Framework Demo ===\n")
        
        # Display results
        df = framework.compare_features()
        print("Feature Comparison Results:")
        print("=" * 80)
        print(df.to_string(index=False))
        print("\n" + "=" * 80)
        
        # Generate visualizations
        if args.visualize:
            framework.generate_visualizations(args.visualize)
        else:
            framework.generate_visualizations()
            
        # Export results
        if args.export:
            framework.export_results(args.export)
        else:
            framework.export_results()
            
    else:
        print("Feature Prioritization Framework")
        print("=" * 40)
        print("Enter feature details (or press Enter to skip):")
        
        while True:
            try:
                feature_name = input("\nFeature name (or 'quit' to exit): ").strip()
                if feature_name.lower() == 'quit':
                    break
                if not feature_name:
                    continue
                    
                # Get feature metrics
                metrics = FeatureMetrics(
                    feature_name=feature_name,
                    product_impact_score=float(input("Product impact score (1-10): ")),
                    revenue_potential=float(input("Revenue potential (currency): ")),
                    time_savings_hours=float(input("Time savings per week (hours): ")),
                    development_cost=float(input("Development cost (currency): ")),
                    implementation_time_weeks=float(input("Implementation time (weeks): ")),
                    user_impact_percentage=float(input("User impact percentage (0-100): ")),
                    market_demand_score=float(input("Market demand score (1-10): ")),
                    technical_complexity=float(input("Technical complexity (1-10): ")),
                    strategic_alignment=float(input("Strategic alignment (1-10): ")),
                    risk_score=float(input("Risk score (1-10, lower is better): "))
                )
                
                framework.add_feature(metrics)
                print(f"\n✓ Feature '{feature_name}' added successfully!")
                
            except ValueError as e:
                print(f"Error: {e}. Please enter valid numeric values.")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
                
        if framework.features:
            print("\n" + "=" * 50)
            print("ANALYSIS RESULTS")
            print("=" * 50)
            
            df = framework.compare_features()
            print(df.to_string(index=False))
            
            # Show individual feature analytics
            print("\n" + "=" * 50)
            print("DETAILED FEATURE ANALYTICS")
            print("=" * 50)
            
            for feature in framework.features:
                analytics = framework.get_feature_analytics(feature)
                print(f"\n📊 {analytics['feature_name']}")
                print(f"   Viability Score: {analytics['viability_score']}/10")
                print(f"   Priority Score: {analytics['priority_score']}/10")
                print(f"   ROI Score: {analytics['roi_score']}")
                print(f"   Recommendation: {analytics['recommendation']}")
                print(f"   Risk Level: {analytics['risk_level']}")
                
            # Generate visualizations
            framework.generate_visualizations()
            
            # Export results
            framework.export_results()

if __name__ == "__main__":
    main() 