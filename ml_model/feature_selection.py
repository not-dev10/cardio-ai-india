"""
Feature Selection Module
Implements three methods from IEEE research [3]:
1. Chi-square test (categorical features)
2. ANOVA F-test (continuous features)
3. Mutual Information (non-linear relationships)
"""
import numpy as np
import pandas as pd
from sklearn.feature_selection import (
    chi2, f_classif, mutual_info_classif,
    SelectKBest, SelectPercentile
)
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
from config import LOGS_DIR
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureSelector:
    """
    Feature selection using multiple methods
    Based on IEEE research on heart disease prediction
    """
    
    def __init__(self, k_features=10):
        """
        Initialize feature selector
        
        Args:
            k_features: Number of top features to select
        """
        self.k_features = k_features
        self.selected_features = {}
        self.feature_scores = {}
        
    def chi_square_selection(self, X, y, feature_names):
        """
        Chi-square test for categorical feature selection
        
        Best for: Categorical features and classification
        Measures: Dependence between feature and target
        
        Args:
            X: Features (must be non-negative)
            y: Target variable
            feature_names: List of feature names
            
        Returns:
            dict: Selected features with scores
        """
        logger.info("Performing Chi-square feature selection...")
        
        # Ensure non-negative values (chi2 requirement)
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Compute chi-square scores
        chi_scores, p_values = chi2(X_scaled, y)
        
        # Create results dataframe
        results = pd.DataFrame({
            'feature': feature_names,
            'chi2_score': chi_scores,
            'p_value': p_values
        }).sort_values('chi2_score', ascending=False)
        
        # Select top k features
        top_features = results.head(self.k_features)
        
        logger.info(f"Chi-square: Top {self.k_features} features selected")
        logger.info(f"\n{top_features}")
        
        self.feature_scores['chi_square'] = results
        self.selected_features['chi_square'] = top_features['feature'].tolist()
        
        return top_features
    
    def anova_f_selection(self, X, y, feature_names):
        """
        ANOVA F-test for continuous feature selection
        
        Best for: Continuous features and classification
        Measures: Linear dependency between feature and target
        
        Args:
            X: Features
            y: Target variable
            feature_names: List of feature names
            
        Returns:
            dict: Selected features with scores
        """
        logger.info("Performing ANOVA F-test feature selection...")
        
        # Compute F-scores
        f_scores, p_values = f_classif(X, y)
        
        # Create results dataframe
        results = pd.DataFrame({
            'feature': feature_names,
            'f_score': f_scores,
            'p_value': p_values
        }).sort_values('f_score', ascending=False)
        
        # Select top k features
        top_features = results.head(self.k_features)
        
        logger.info(f"ANOVA F-test: Top {self.k_features} features selected")
        logger.info(f"\n{top_features}")
        
        self.feature_scores['anova_f'] = results
        self.selected_features['anova_f'] = top_features['feature'].tolist()
        
        return top_features
    
    def mutual_info_selection(self, X, y, feature_names):
        """
        Mutual Information for feature selection
        
        Best for: Capturing non-linear relationships
        Measures: Mutual dependence between feature and target
        
        Args:
            X: Features
            y: Target variable
            feature_names: List of feature names
            
        Returns:
            dict: Selected features with scores
        """
        logger.info("Performing Mutual Information feature selection...")
        
        # Compute mutual information scores
        mi_scores = mutual_info_classif(X, y, random_state=42)
        
        # Create results dataframe
        results = pd.DataFrame({
            'feature': feature_names,
            'mi_score': mi_scores
        }).sort_values('mi_score', ascending=False)
        
        # Select top k features
        top_features = results.head(self.k_features)
        
        logger.info(f"Mutual Information: Top {self.k_features} features selected")
        logger.info(f"\n{top_features}")
        
        self.feature_scores['mutual_info'] = results
        self.selected_features['mutual_info'] = top_features['feature'].tolist()
        
        return top_features
    
    def ensemble_feature_selection(self, X, y, feature_names):
        """
        Ensemble feature selection combining all three methods
        
        Features are ranked by:
        1. Frequency of appearance in top-k across methods
        2. Average rank across methods
        
        Args:
            X: Features
            y: Target variable
            feature_names: List of feature names
            
        Returns:
            list: Final selected features
        """
        logger.info("\n" + "="*70)
        logger.info("ENSEMBLE FEATURE SELECTION")
        logger.info("="*70)
        
        # Run all three methods
        self.chi_square_selection(X, y, feature_names)
        self.anova_f_selection(X, y, feature_names)
        self.mutual_info_selection(X, y, feature_names)
        
        # Count frequency of each feature across methods
        all_selected = (
            self.selected_features['chi_square'] +
            self.selected_features['anova_f'] +
            self.selected_features['mutual_info']
        )
        
        feature_frequency = pd.Series(all_selected).value_counts()
        
        # Calculate average rank across methods
        feature_ranks = {}
        for feature in feature_names:
            ranks = []
            
            # Chi-square rank
            chi_rank = self.feature_scores['chi_square'][
                self.feature_scores['chi_square']['feature'] == feature
            ].index[0] if feature in self.feature_scores['chi_square']['feature'].values else len(feature_names)
            ranks.append(chi_rank)
            
            # ANOVA rank
            anova_rank = self.feature_scores['anova_f'][
                self.feature_scores['anova_f']['feature'] == feature
            ].index[0] if feature in self.feature_scores['anova_f']['feature'].values else len(feature_names)
            ranks.append(anova_rank)
            
            # MI rank
            mi_rank = self.feature_scores['mutual_info'][
                self.feature_scores['mutual_info']['feature'] == feature
            ].index[0] if feature in self.feature_scores['mutual_info']['feature'].values else len(feature_names)
            ranks.append(mi_rank)
            
            feature_ranks[feature] = np.mean(ranks)
        
        # Create ensemble results
        ensemble_results = pd.DataFrame({
            'feature': feature_names,
            'frequency': [feature_frequency.get(f, 0) for f in feature_names],
            'avg_rank': [feature_ranks[f] for f in feature_names]
        }).sort_values(['frequency', 'avg_rank'], ascending=[False, True])
        
        # Select top k features
        final_features = ensemble_results.head(self.k_features)['feature'].tolist()
        
        logger.info("\n" + "="*70)
        logger.info("FINAL ENSEMBLE SELECTION")
        logger.info("="*70)
        logger.info(f"\n{ensemble_results.head(self.k_features)}")
        
        self.selected_features['ensemble'] = final_features
        
        # Visualize
        self.visualize_feature_selection(ensemble_results)
        
        return final_features
    
    def visualize_feature_selection(self, ensemble_results):
        """
        Visualize feature selection results
        
        Args:
            ensemble_results: DataFrame with ensemble results
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Chi-square scores
        top_chi = self.feature_scores['chi_square'].head(self.k_features)
        axes[0, 0].barh(top_chi['feature'], top_chi['chi2_score'])
        axes[0, 0].set_xlabel('Chi-square Score')
        axes[0, 0].set_title('Top Features by Chi-square Test')
        axes[0, 0].invert_yaxis()
        
        # 2. ANOVA F-scores
        top_anova = self.feature_scores['anova_f'].head(self.k_features)
        axes[0, 1].barh(top_anova['feature'], top_anova['f_score'])
        axes[0, 1].set_xlabel('F-score')
        axes[0, 1].set_title('Top Features by ANOVA F-test')
        axes[0, 1].invert_yaxis()
        
        # 3. Mutual Information scores
        top_mi = self.feature_scores['mutual_info'].head(self.k_features)
        axes[1, 0].barh(top_mi['feature'], top_mi['mi_score'])
        axes[1, 0].set_xlabel('Mutual Information Score')
        axes[1, 0].set_title('Top Features by Mutual Information')
        axes[1, 0].invert_yaxis()
        
        # 4. Ensemble results
        top_ensemble = ensemble_results.head(self.k_features)
        axes[1, 1].barh(top_ensemble['feature'], top_ensemble['frequency'])
        axes[1, 1].set_xlabel('Frequency (out of 3 methods)')
        axes[1, 1].set_title('Ensemble Feature Selection')
        axes[1, 1].invert_yaxis()
        
        plt.tight_layout()
        
        # Save plot
        plot_path = LOGS_DIR / "feature_selection_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"\nFeature selection visualization saved to {plot_path}")
        plt.close()
    
    def get_feature_importance_comparison(self):
        """
        Get comparison of feature importance across methods
        
        Returns:
            DataFrame: Feature importance comparison
        """
        if not self.feature_scores:
            logger.warning("No feature selection performed yet")
            return None
        
        # Merge all scores
        comparison = self.feature_scores['chi_square'][['feature', 'chi2_score']].copy()
        comparison = comparison.merge(
            self.feature_scores['anova_f'][['feature', 'f_score']],
            on='feature'
        )
        comparison = comparison.merge(
            self.feature_scores['mutual_info'][['feature', 'mi_score']],
            on='feature'
        )
        
        # Normalize scores to 0-1 range for comparison
        for col in ['chi2_score', 'f_score', 'mi_score']:
            comparison[f'{col}_norm'] = (
                (comparison[col] - comparison[col].min()) /
                (comparison[col].max() - comparison[col].min())
            )
        
        # Calculate average normalized score
        comparison['avg_score'] = comparison[
            ['chi2_score_norm', 'f_score_norm', 'mi_score_norm']
        ].mean(axis=1)
        
        return comparison.sort_values('avg_score', ascending=False)


# Example usage
if __name__ == "__main__":
    # Generate sample data
    from sklearn.datasets import make_classification
    
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        random_state=42
    )
    
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    
    # Perform feature selection
    selector = FeatureSelector(k_features=10)
    final_features = selector.ensemble_feature_selection(X, y, feature_names)
    
    print("\n" + "="*70)
    print("FINAL SELECTED FEATURES")
    print("="*70)
    for i, feature in enumerate(final_features, 1):
        print(f"{i}. {feature}")
    
    # Get comparison
    comparison = selector.get_feature_importance_comparison()
    print("\n" + "="*70)
    print("FEATURE IMPORTANCE COMPARISON")
    print("="*70)
    print(comparison.head(10))
