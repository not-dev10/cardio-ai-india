"""
Clinical Monitoring System
Real-time monitoring of model performance and patient safety
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Clinical performance metrics"""
    sensitivity: float  # True positive rate
    specificity: float  # True negative rate
    ppv: float  # Positive predictive value
    npv: float  # Negative predictive value
    auc: float  # Area under curve
    mcc: float  # Matthews correlation coefficient
    calibration_error: float  # Calibration error
    timestamp: str


class ClinicalMonitor:
    """Monitor model performance and patient safety"""
    
    # Target metrics for medical-grade system
    TARGETS = {
        "sensitivity": 0.90,
        "specificity": 0.95,
        "ppv": 0.90,
        "npv": 0.95,
        "auc": 0.95,
        "mcc": 0.85,
        "calibration_error": 0.05,
    }
    
    # Alert thresholds (when to flag issues)
    ALERT_THRESHOLDS = {
        "sensitivity": 0.85,  # Alert if drops below 85%
        "specificity": 0.90,  # Alert if drops below 90%
        "ppv": 0.85,
        "npv": 0.90,
        "auc": 0.90,
        "calibration_error": 0.10,
    }
    
    def __init__(self):
        """Initialize monitor"""
        self.predictions_log = []
        self.performance_history = []
        self.alerts = []
    
    def log_prediction(
        self,
        patient_id: str,
        predicted_prob: float,
        actual_outcome: int,
        confidence: float,
        timestamp: str = None
    ):
        """
        Log a prediction for monitoring
        
        Args:
            patient_id: Unique patient identifier
            predicted_prob: Predicted probability (0-1)
            actual_outcome: Actual outcome (0=healthy, 1=disease)
            confidence: Model confidence score
            timestamp: Prediction timestamp
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.predictions_log.append({
            "patient_id": patient_id,
            "predicted_prob": predicted_prob,
            "actual_outcome": actual_outcome,
            "confidence": confidence,
            "timestamp": timestamp,
            "prediction": 1 if predicted_prob >= 0.5 else 0,
        })
    
    def calculate_metrics(
        self,
        predictions: List[float],
        actuals: List[int],
        threshold: float = 0.5
    ) -> PerformanceMetrics:
        """
        Calculate clinical performance metrics
        
        Args:
            predictions: List of predicted probabilities
            actuals: List of actual outcomes
            threshold: Decision threshold
            
        Returns:
            PerformanceMetrics object
        """
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Binary predictions
        binary_preds = (predictions >= threshold).astype(int)
        
        # Calculate metrics
        tp = np.sum((binary_preds == 1) & (actuals == 1))
        tn = np.sum((binary_preds == 0) & (actuals == 0))
        fp = np.sum((binary_preds == 1) & (actuals == 0))
        fn = np.sum((binary_preds == 0) & (actuals == 1))
        
        # Sensitivity (True Positive Rate)
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # Specificity (True Negative Rate)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # Positive Predictive Value
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        # Negative Predictive Value
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        
        # Matthews Correlation Coefficient
        denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = ((tp * tn) - (fp * fn)) / denominator if denominator > 0 else 0
        
        # AUC (simplified - using ROC approximation)
        auc = self._calculate_auc(predictions, actuals)
        
        # Calibration error
        calibration_error = self._calculate_calibration_error(predictions, actuals)
        
        metrics = PerformanceMetrics(
            sensitivity=sensitivity,
            specificity=specificity,
            ppv=ppv,
            npv=npv,
            auc=auc,
            mcc=mcc,
            calibration_error=calibration_error,
            timestamp=datetime.now().isoformat()
        )
        
        self.performance_history.append(metrics)
        return metrics
    
    def check_performance_drift(self) -> List[str]:
        """
        Check for performance drift
        
        Returns:
            List of alerts if drift detected
        """
        alerts = []
        
        if len(self.predictions_log) < 100:
            return alerts  # Need minimum data
        
        # Get recent predictions
        recent_df = pd.DataFrame(self.predictions_log[-100:])
        
        # Calculate recent metrics
        recent_metrics = self.calculate_metrics(
            recent_df["predicted_prob"].tolist(),
            recent_df["actual_outcome"].tolist()
        )
        
        # Check against thresholds
        if recent_metrics.sensitivity < self.ALERT_THRESHOLDS["sensitivity"]:
            alerts.append(
                f"⚠️ ALERT: Sensitivity dropped to {recent_metrics.sensitivity:.2%} "
                f"(target: {self.TARGETS['sensitivity']:.2%})"
            )
        
        if recent_metrics.specificity < self.ALERT_THRESHOLDS["specificity"]:
            alerts.append(
                f"⚠️ ALERT: Specificity dropped to {recent_metrics.specificity:.2%} "
                f"(target: {self.TARGETS['specificity']:.2%})"
            )
        
        if recent_metrics.calibration_error > self.ALERT_THRESHOLDS["calibration_error"]:
            alerts.append(
                f"⚠️ ALERT: Calibration error increased to {recent_metrics.calibration_error:.4f} "
                f"(target: {self.TARGETS['calibration_error']:.4f})"
            )
        
        self.alerts.extend(alerts)
        return alerts
    
    def check_fairness(self, demographic_groups: Dict[str, List[int]]) -> Dict:
        """
        Check for fairness across demographic groups
        
        Args:
            demographic_groups: Dict of group_name -> list of indices
            
        Returns:
            Fairness metrics by group
        """
        fairness_report = {}
        
        predictions_array = np.array([p["predicted_prob"] for p in self.predictions_log])
        actuals_array = np.array([p["actual_outcome"] for p in self.predictions_log])
        
        for group_name, indices in demographic_groups.items():
            if len(indices) == 0:
                continue
            
            group_preds = predictions_array[indices]
            group_actuals = actuals_array[indices]
            
            metrics = self.calculate_metrics(
                group_preds.tolist(),
                group_actuals.tolist()
            )
            
            fairness_report[group_name] = {
                "sensitivity": metrics.sensitivity,
                "specificity": metrics.specificity,
                "ppv": metrics.ppv,
                "npv": metrics.npv,
                "sample_size": len(indices),
            }
        
        # Check for disparities
        disparities = self._check_disparities(fairness_report)
        fairness_report["disparities"] = disparities
        
        return fairness_report
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        if len(self.predictions_log) == 0:
            return "No predictions logged yet"
        
        df = pd.DataFrame(self.predictions_log)
        metrics = self.calculate_metrics(
            df["predicted_prob"].tolist(),
            df["actual_outcome"].tolist()
        )
        
        report = f"""
{'='*70}
CLINICAL PERFORMANCE REPORT
{'='*70}

Report Generated: {datetime.now().isoformat()}
Total Predictions: {len(self.predictions_log)}

PERFORMANCE METRICS:
{'-'*70}
Sensitivity (Recall):        {metrics.sensitivity:.2%}  (Target: {self.TARGETS['sensitivity']:.2%})
Specificity:                 {metrics.specificity:.2%}  (Target: {self.TARGETS['specificity']:.2%})
Positive Predictive Value:   {metrics.ppv:.2%}  (Target: {self.TARGETS['ppv']:.2%})
Negative Predictive Value:   {metrics.npv:.2%}  (Target: {self.TARGETS['npv']:.2%})
AUC (Area Under Curve):      {metrics.auc:.4f}  (Target: {self.TARGETS['auc']:.4f})
MCC (Matthews Corr. Coeff):  {metrics.mcc:.4f}  (Target: {self.TARGETS['mcc']:.4f})
Calibration Error:           {metrics.calibration_error:.4f}  (Target: {self.TARGETS['calibration_error']:.4f})

COMPLIANCE STATUS:
{'-'*70}
"""
        
        # Check compliance
        compliant = True
        for metric_name, target_value in self.TARGETS.items():
            actual_value = getattr(metrics, metric_name)
            if metric_name == "calibration_error":
                is_compliant = actual_value <= target_value
            else:
                is_compliant = actual_value >= target_value
            
            status = "✓ PASS" if is_compliant else "✗ FAIL"
            report += f"{metric_name:30s}: {status}\n"
            
            if not is_compliant:
                compliant = False
        
        report += f"\n{'='*70}\n"
        report += f"Overall Status: {'✓ COMPLIANT' if compliant else '✗ NON-COMPLIANT'}\n"
        report += f"{'='*70}\n"
        
        if self.alerts:
            report += f"\nACTIVE ALERTS ({len(self.alerts)}):\n"
            report += f"{'-'*70}\n"
            for alert in self.alerts[-10:]:  # Last 10 alerts
                report += f"• {alert}\n"
        
        return report
    
    def _calculate_auc(self, predictions: np.ndarray, actuals: np.ndarray) -> float:
        """Calculate AUC using trapezoidal rule"""
        # Sort by predictions
        sorted_indices = np.argsort(predictions)[::-1]
        sorted_actuals = actuals[sorted_indices]
        
        # Calculate TPR and FPR at different thresholds
        n_pos = np.sum(actuals == 1)
        n_neg = np.sum(actuals == 0)
        
        if n_pos == 0 or n_neg == 0:
            return 0.5
        
        tp = np.cumsum(sorted_actuals == 1)
        fp = np.cumsum(sorted_actuals == 0)
        
        tpr = tp / n_pos
        fpr = fp / n_neg
        
        # Trapezoidal rule
        auc = np.trapz(tpr, fpr)
        return auc
    
    def _calculate_calibration_error(
        self,
        predictions: np.ndarray,
        actuals: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """Calculate calibration error"""
        bins = np.linspace(0, 1, n_bins + 1)
        calibration_errors = []
        
        for i in range(n_bins):
            mask = (predictions >= bins[i]) & (predictions < bins[i + 1])
            if np.sum(mask) > 0:
                bin_predictions = predictions[mask]
                bin_actuals = actuals[mask]
                
                mean_pred = np.mean(bin_predictions)
                mean_actual = np.mean(bin_actuals)
                
                calibration_errors.append(abs(mean_pred - mean_actual))
        
        return np.mean(calibration_errors) if calibration_errors else 0
    
    def _check_disparities(self, fairness_report: Dict) -> List[str]:
        """Check for disparities across groups"""
        disparities = []
        
        if len(fairness_report) < 2:
            return disparities
        
        # Get sensitivity values for each group
        sensitivities = {
            group: metrics["sensitivity"]
            for group, metrics in fairness_report.items()
            if group != "disparities"
        }
        
        if len(sensitivities) > 1:
            max_sens = max(sensitivities.values())
            min_sens = min(sensitivities.values())
            
            # Flag if difference > 5%
            if (max_sens - min_sens) > 0.05:
                disparities.append(
                    f"Sensitivity disparity detected: {max_sens:.2%} vs {min_sens:.2%}"
                )
        
        return disparities


def example_monitoring():
    """Example usage of clinical monitor"""
    monitor = ClinicalMonitor()
    
    # Simulate predictions
    np.random.seed(42)
    n_samples = 200
    
    # Generate realistic predictions
    actuals = np.random.binomial(1, 0.3, n_samples)  # 30% disease prevalence
    predictions = np.random.beta(2, 5, n_samples)  # Beta distribution
    
    # Make predictions correlated with actuals
    predictions[actuals == 1] += 0.3
    predictions = np.clip(predictions, 0, 1)
    
    # Log predictions
    for i in range(n_samples):
        monitor.log_prediction(
            patient_id=f"P{i:04d}",
            predicted_prob=predictions[i],
            actual_outcome=int(actuals[i]),
            confidence=0.8 + np.random.normal(0, 0.1)
        )
    
    # Generate report
    print(monitor.generate_performance_report())
    
    # Check for drift
    drift_alerts = monitor.check_performance_drift()
    if drift_alerts:
        print("\nDrift Alerts:")
        for alert in drift_alerts:
            print(f"  {alert}")


if __name__ == "__main__":
    example_monitoring()
