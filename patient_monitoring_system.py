"""
Remote Patient Health Monitoring System Using IoT Sensors
For Continuous Clinical Observation and Emergency Alerts
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

class HealthSensor:
    """Simulates IoT health monitoring sensors"""
    
    def __init__(self, sensor_id, patient_id, sensor_type, normal_range):
        self.sensor_id = sensor_id
        self.patient_id = patient_id
        self.sensor_type = sensor_type  # 'heart_rate', 'temperature', 'oxygen'
        self.normal_range = normal_range  # (min, max) tuple
        self.current_reading = 0.0
        self.measurement_history = []
        self.sensor_status = 'normal'  # normal, warning, critical
        
    def read_vital_sign(self, base_value, stress_factor=0, activity_factor=0):
        """
        Read vital sign with realistic sensor characteristics
        base_value: baseline vital sign value
        stress_factor: stress level (0-1)
        activity_factor: activity level (0-1)
        Returns: measured_value (float)
        """
        # Simulate sensor noise
        noise = np.random.normal(0, 1)
        
        # Calculate affected reading based on stress and activity
        affected_reading = base_value + (stress_factor * 15) + (activity_factor * 20) + noise
        affected_reading = max(0, affected_reading)
        
        self.current_reading = affected_reading
        
        self.measurement_history.append({
            'timestamp': datetime.now(),
            'value': affected_reading,
            'sensor_id': self.sensor_id,
            'patient_id': self.patient_id,
            'sensor_type': self.sensor_type
        })
        
        return affected_reading


class AlertSystem:
    """Manages patient health alerts and emergency notifications"""
    
    def __init__(self, heart_rate_thresholds=None, temp_thresholds=None, oxygen_thresholds=None):
        self.heart_rate_thresholds = heart_rate_thresholds or {'low': 50, 'high': 100}
        self.temp_thresholds = temp_thresholds or {'low': 36.0, 'high': 38.5}
        self.oxygen_thresholds = oxygen_thresholds or {'low': 90, 'high': 100}
        self.alerts = []
        self.alert_history = []
        self.emergency_triggered = False
        
    def evaluate_vital_sign(self, patient_id, sensor_type, measured_value, current_time):
        """
        Evaluate vital sign and generate alerts
        Returns: alert_info (dict) or None
        """
        alert_info = None
        severity = 'normal'
        threshold = None
        
        # Determine severity based on sensor type
        if sensor_type == 'heart_rate':
            threshold = self.heart_rate_thresholds
            if measured_value < 40 or measured_value > 120:
                severity = 'critical'
                self.emergency_triggered = True
            elif measured_value < 50 or measured_value > 100:
                severity = 'high'
            elif measured_value < 55 or measured_value > 95:
                severity = 'medium'
                
        elif sensor_type == 'temperature':
            threshold = self.temp_thresholds
            if measured_value < 35.0 or measured_value > 39.5:
                severity = 'critical'
                self.emergency_triggered = True
            elif measured_value < 36.0 or measured_value > 38.5:
                severity = 'high'
            elif measured_value < 36.5 or measured_value > 38.0:
                severity = 'medium'
                
        elif sensor_type == 'oxygen':
            threshold = self.oxygen_thresholds
            if measured_value < 85:
                severity = 'critical'
                self.emergency_triggered = True
            elif measured_value < 90:
                severity = 'high'
            elif measured_value < 95:
                severity = 'medium'
        
        if severity != 'normal':
            alert_info = {
                'timestamp': current_time,
                'patient_id': patient_id,
                'sensor_type': sensor_type,
                'measured_value': measured_value,
                'severity': severity,
                'message': f"{severity.upper()} ALERT: Patient {patient_id} - {sensor_type.replace('_', ' ').title()} is {measured_value:.1f}"
            }
            
            self.alerts.append(alert_info)
            self.alert_history.append(alert_info)
        
        return alert_info


class PatientProfile:
    """Represents a patient with health monitoring"""
    
    def __init__(self, patient_id, patient_name, age, condition_type='chronic'):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.age = age
        self.condition_type = condition_type  # chronic, post_operative, elderly
        self.sensors = {}
        self.alert_system = AlertSystem()
        self.patient_status = 'stable'  # stable, warning, critical
        self.last_alert_time = None
        self.total_alerts = 0
        
    def add_sensor(self, sensor_id, sensor_type, normal_range):
        """Add a health sensor to the patient"""
        self.sensors[sensor_id] = HealthSensor(sensor_id, self.patient_id, sensor_type, normal_range)
        
    def evaluate_patient_health(self, current_time):
        """Evaluate overall patient health status"""
        active_alerts = len([a for a in self.alert_system.alerts if 
                           (current_time - a['timestamp']).total_seconds() < 300])
        
        if active_alerts > 0:
            critical_alerts = len([a for a in self.alert_system.alerts if 
                                 a['severity'] == 'critical' and 
                                 (current_time - a['timestamp']).total_seconds() < 300])
            
            if critical_alerts > 0:
                self.patient_status = 'critical'
            elif any(a['severity'] == 'high' for a in self.alert_system.alerts[-3:]):
                self.patient_status = 'warning'
            else:
                self.patient_status = 'stable'
        else:
            self.patient_status = 'stable'


class RemoteMonitoringSystem:
    """Main system managing remote patient health monitoring"""
    
    def __init__(self, system_name='Patient Health Monitoring System'):
        self.system_name = system_name
        self.patients = {}
        self.system_status = 'active'  # active, maintenance, offline
        self.daily_statistics = []
        self.all_alerts = []
        self.emergency_events = []
        
    def add_patient(self, patient_id, patient_name, age, condition_type='chronic'):
        """Add a patient to the monitoring system"""
        self.patients[patient_id] = PatientProfile(patient_id, patient_name, age, condition_type)
        
    def simulate_monitoring_day(self, date=None, num_intervals=96):
        """
        Simulate a full day of patient monitoring with 15-minute intervals (96 intervals in 24 hours)
        """
        if date is None:
            date = datetime.now().date()
        
        daily_data = []
        total_alerts = 0
        critical_events = 0
        
        for interval in range(num_intervals):
            quarter_hour = (interval * 15) / 60
            hour = int(quarter_hour)
            minutes = int((quarter_hour % 1) * 60)
            
            current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=quarter_hour)
            
            for patient_id, patient in self.patients.items():
                # Generate realistic vital signs based on time of day and condition
                heart_rate = self._generate_heart_rate(patient.condition_type, hour)
                temperature = self._generate_temperature(patient.condition_type, hour)
                oxygen_level = self._generate_oxygen_level(patient.condition_type, hour)
                
                # Process each sensor for the patient
                for sensor_id, sensor in patient.sensors.items():
                    if 'heart_rate' in sensor.sensor_type:
                        measured_hr = sensor.read_vital_sign(heart_rate)
                        alert = patient.alert_system.evaluate_vital_sign(
                            patient_id, 'heart_rate', measured_hr, current_time
                        )
                        if alert:
                            total_alerts += 1
                            if alert['severity'] == 'critical':
                                critical_events += 1
                            self.all_alerts.append(alert)
                            
                    elif 'temperature' in sensor.sensor_type:
                        measured_temp = sensor.read_vital_sign(temperature)
                        alert = patient.alert_system.evaluate_vital_sign(
                            patient_id, 'temperature', measured_temp, current_time
                        )
                        if alert:
                            total_alerts += 1
                            if alert['severity'] == 'critical':
                                critical_events += 1
                            self.all_alerts.append(alert)
                            
                    elif 'oxygen' in sensor.sensor_type:
                        measured_o2 = sensor.read_vital_sign(oxygen_level)
                        alert = patient.alert_system.evaluate_vital_sign(
                            patient_id, 'oxygen', measured_o2, current_time
                        )
                        if alert:
                            total_alerts += 1
                            if alert['severity'] == 'critical':
                                critical_events += 1
                            self.all_alerts.append(alert)
                
                # Evaluate patient health
                patient.evaluate_patient_health(current_time)
                
                daily_data.append({
                    'date': date,
                    'time': f"{hour:02d}:{minutes:02d}",
                    'hour': hour,
                    'patient_id': patient_id,
                    'patient_name': patient.patient_name,
                    'condition_type': patient.condition_type,
                    'patient_status': patient.patient_status,
                    'heart_rate': heart_rate,
                    'temperature': temperature,
                    'oxygen_level': oxygen_level,
                    'active_alerts': len(patient.alert_system.alerts)
                })
        
        self.daily_statistics.append({
            'date': date,
            'total_alerts': total_alerts,
            'critical_events': critical_events,
            'num_patients': len(self.patients),
            'system_status': self.system_status
        })
        
        return pd.DataFrame(daily_data)
    
    def _generate_heart_rate(self, condition_type, hour):
        """Generate realistic heart rate patterns"""
        if condition_type == 'post_operative':
            # Post-operative: elevated baseline with variability
            if 6 <= hour < 22:
                return np.random.normal(85, 12)
            else:
                return np.random.normal(75, 10)
        elif condition_type == 'elderly':
            # Elderly: lower baseline with more variability
            if 6 <= hour < 22:
                return np.random.normal(72, 8)
            else:
                return np.random.normal(65, 8)
        else:  # chronic
            # Chronic: moderate baseline
            if 6 <= hour < 22:
                return np.random.normal(75, 10)
            else:
                return np.random.normal(68, 8)
    
    def _generate_temperature(self, condition_type, hour):
        """Generate realistic body temperature patterns"""
        if condition_type == 'post_operative':
            # Post-operative: slightly elevated
            if 6 <= hour < 18:
                return np.random.normal(37.5, 0.3)
            else:
                return np.random.normal(37.2, 0.3)
        elif condition_type == 'elderly':
            # Elderly: lower baseline
            return np.random.normal(36.8, 0.3)
        else:  # chronic
            # Chronic: normal baseline
            if 6 <= hour < 22:
                return np.random.normal(37.0, 0.3)
            else:
                return np.random.normal(36.8, 0.3)
    
    def _generate_oxygen_level(self, condition_type, hour):
        """Generate realistic oxygen saturation patterns"""
        if condition_type == 'post_operative':
            # Post-operative: slightly lower
            return np.random.normal(96, 1.5)
        elif condition_type == 'elderly':
            # Elderly: lower baseline
            return np.random.normal(94, 2)
        else:  # chronic
            # Chronic: normal baseline
            return np.random.normal(97, 1)
    
    def get_system_report(self):
        """Generate comprehensive system report"""
        report = {
            'system_name': self.system_name,
            'total_patients': len(self.patients),
            'total_alerts': len(self.all_alerts),
            'critical_events': len([a for a in self.all_alerts if a['severity'] == 'critical']),
            'simulation_days': len(self.daily_statistics),
            'system_status': self.system_status,
            'avg_daily_alerts': np.mean([stat['total_alerts'] for stat in self.daily_statistics]) if self.daily_statistics else 0
        }
        return report


def generate_visualizations(system, daily_data):
    """Generate comprehensive visualizations for the report"""
    
    # 1. Vital Signs Analysis
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Remote Patient Health Monitoring System - Vital Signs Analysis', 
                 fontsize=16, fontweight='bold')
    
    # Heart rate by hour
    hr_by_hour = daily_data.groupby('hour')['heart_rate'].mean()
    axes[0, 0].plot(hr_by_hour.index, hr_by_hour.values, marker='o', linewidth=2, 
                    markersize=6, color='#FF6B6B', label='Heart Rate')
    axes[0, 0].axhline(y=100, color='red', linestyle='--', linewidth=2, label='High Threshold')
    axes[0, 0].axhline(y=50, color='orange', linestyle='--', linewidth=2, label='Low Threshold')
    axes[0, 0].fill_between(hr_by_hour.index, hr_by_hour.values, alpha=0.3, color='#FF6B6B')
    axes[0, 0].set_title('Heart Rate by Hour (bpm)', fontweight='bold')
    axes[0, 0].set_ylabel('Heart Rate (bpm)')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Temperature by hour
    temp_by_hour = daily_data.groupby('hour')['temperature'].mean()
    axes[0, 1].plot(temp_by_hour.index, temp_by_hour.values, marker='s', linewidth=2, 
                    markersize=6, color='#4ECDC4', label='Temperature')
    axes[0, 1].axhline(y=38.5, color='red', linestyle='--', linewidth=2, label='High Threshold')
    axes[0, 1].axhline(y=36.0, color='orange', linestyle='--', linewidth=2, label='Low Threshold')
    axes[0, 1].fill_between(temp_by_hour.index, temp_by_hour.values, alpha=0.3, color='#4ECDC4')
    axes[0, 1].set_title('Body Temperature by Hour (°C)', fontweight='bold')
    axes[0, 1].set_ylabel('Temperature (°C)')
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Oxygen level by hour
    o2_by_hour = daily_data.groupby('hour')['oxygen_level'].mean()
    axes[1, 0].plot(o2_by_hour.index, o2_by_hour.values, marker='^', linewidth=2, 
                    markersize=6, color='#95E1D3', label='Oxygen Level')
    axes[1, 0].axhline(y=90, color='red', linestyle='--', linewidth=2, label='Critical Threshold')
    axes[1, 0].axhline(y=95, color='orange', linestyle='--', linewidth=2, label='Warning Threshold')
    axes[1, 0].fill_between(o2_by_hour.index, o2_by_hour.values, alpha=0.3, color='#95E1D3')
    axes[1, 0].set_title('Oxygen Saturation by Hour (%)', fontweight='bold')
    axes[1, 0].set_ylabel('Oxygen Saturation (%)')
    axes[1, 0].set_xlabel('Hour of Day')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Patient status distribution
    patient_status_counts = daily_data['patient_status'].value_counts()
    colors_status = {'stable': 'green', 'warning': 'yellow', 'critical': 'red'}
    colors = [colors_status.get(status, 'gray') for status in patient_status_counts.index]
    
    axes[1, 1].bar(patient_status_counts.index, patient_status_counts.values, color=colors, edgecolor='black')
    axes[1, 1].set_title('Patient Status Distribution', fontweight='bold')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_xlabel('Patient Status')
    for i, v in enumerate(patient_status_counts.values):
        axes[1, 1].text(i, v + 10, str(v), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/patient_monitoring_project/fig_vital_signs.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_vital_signs.png")
    plt.close()
    
    # 2. Alert Analysis
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Alert Analysis and Emergency Response', fontsize=16, fontweight='bold')
    
    # Alert types distribution
    alert_types = [a['sensor_type'] for a in system.all_alerts]
    alert_counts = pd.Series(alert_types).value_counts()
    colors_map = {'heart_rate': '#FF6B6B', 'temperature': '#4ECDC4', 'oxygen': '#95E1D3'}
    colors = [colors_map.get(alert, 'gray') for alert in alert_counts.index]
    
    axes[0, 0].bar(alert_counts.index, alert_counts.values, color=colors, edgecolor='black')
    axes[0, 0].set_title('Alert Types Distribution', fontweight='bold')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_xlabel('Vital Sign Type')
    for i, v in enumerate(alert_counts.values):
        axes[0, 0].text(i, v + 2, str(v), ha='center', fontweight='bold')
    
    # Alerts by hour
    alerts_by_hour = daily_data.groupby('hour')['active_alerts'].mean()
    axes[0, 1].bar(alerts_by_hour.index, alerts_by_hour.values, color='#FF6B6B', edgecolor='black', alpha=0.7)
    axes[0, 1].set_title('Average Active Alerts by Hour', fontweight='bold')
    axes[0, 1].set_ylabel('Number of Alerts')
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Alert severity distribution
    alert_severities = [a['severity'] for a in system.all_alerts]
    severity_counts = pd.Series(alert_severities).value_counts()
    colors_severity = {'medium': 'yellow', 'high': 'orange', 'critical': 'red'}
    colors = [colors_severity.get(sev, 'gray') for sev in severity_counts.index]
    
    axes[1, 0].pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%',
                   colors=colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    axes[1, 0].set_title('Alert Severity Distribution', fontweight='bold')
    
    # Patient-wise alert count
    patient_alerts = daily_data.groupby('patient_name')['active_alerts'].sum()
    axes[1, 1].barh(patient_alerts.index, patient_alerts.values, color='#FF6B6B', edgecolor='black')
    axes[1, 1].set_title('Total Alerts by Patient', fontweight='bold')
    axes[1, 1].set_xlabel('Number of Alerts')
    for i, v in enumerate(patient_alerts.values):
        axes[1, 1].text(v + 2, i, str(int(v)), va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/patient_monitoring_project/fig_alert_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_alert_analysis.png")
    plt.close()
    
    # 3. System Architecture Diagram
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    ax.text(0.5, 0.95, 'Remote Patient Health Monitoring System Architecture', 
            ha='center', fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    components = [
        ('Heart Rate\nSensor', 0.15, 0.75),
        ('Temperature\nSensor', 0.5, 0.75),
        ('Oxygen\nSensor', 0.85, 0.75),
        ('IoT\nCommunication\nModule', 0.5, 0.55),
        ('Cloud\nServer', 0.15, 0.35),
        ('Alert\nManagement', 0.5, 0.35),
        ('Emergency\nNotifications', 0.85, 0.35),
    ]
    
    for label, x, y in components:
        bbox = dict(boxstyle='round,pad=0.6', facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold',
                transform=ax.transAxes, bbox=bbox)
    
    connections = [
        ((0.25, 0.75), (0.4, 0.75)),
        ((0.6, 0.75), (0.75, 0.75)),
        ((0.5, 0.65), (0.5, 0.60)),
        ((0.25, 0.65), (0.25, 0.60)),
        ((0.75, 0.65), (0.75, 0.60)),
    ]
    
    for start, end in connections:
        ax.annotate('', xy=end, xytext=start, transform=ax.transAxes,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    features_text = 'Key Features:\n• Real-time Vital Sign Monitoring\n• Multi-parameter Detection\n• Instant Emergency Alerts\n• Cloud-based Dashboard\n• 24/7 Clinical Observation'
    ax.text(0.5, 0.15, features_text, ha='center', va='top', fontsize=10,
            transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightyellow', 
            edgecolor='black', linewidth=1.5))
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/patient_monitoring_project/fig_system_architecture.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_system_architecture.png")
    plt.close()
    
    # 4. Daily Performance
    fig, ax = plt.subplots(figsize=(12, 6))
    
    daily_stats = pd.DataFrame(system.daily_statistics)
    
    x = np.arange(len(daily_stats))
    width = 0.35
    
    ax.bar(x - width/2, daily_stats['total_alerts'], width, label='Total Alerts', 
           color='orange', edgecolor='black')
    ax2 = ax.twinx()
    ax2.bar(x + width/2, daily_stats['critical_events'], width, label='Critical Events', 
            color='red', alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Day', fontweight='bold')
    ax.set_ylabel('Total Alerts', fontweight='bold', color='orange')
    ax2.set_ylabel('Critical Events', fontweight='bold', color='red')
    ax.set_title('Daily System Performance', fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Day {i+1}" for i in range(len(daily_stats))])
    ax.grid(True, alpha=0.3, axis='y')
    
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/patient_monitoring_project/fig_daily_performance.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_daily_performance.png")
    plt.close()
    
    # 5. Patient Condition Heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    
    patient_activity = daily_data.pivot_table(values='active_alerts', index='patient_name', 
                                             columns='hour', aggfunc='mean', fill_value=0)
    
    sns.heatmap(patient_activity, cmap='YlOrRd', annot=True, fmt='.1f', cbar_kws={'label': 'Avg Alerts'},
                ax=ax, linewidths=0.5, linecolor='gray')
    ax.set_title('Patient Monitoring Activity Heatmap - Alerts by Patient and Hour', fontweight='bold', fontsize=14)
    ax.set_xlabel('Hour of Day', fontweight='bold')
    ax.set_ylabel('Patient Name', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/patient_monitoring_project/fig_patient_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_patient_heatmap.png")
    plt.close()


def main():
    """Main execution function"""
    print("=" * 70)
    print("REMOTE PATIENT HEALTH MONITORING SYSTEM SIMULATION")
    print("=" * 70)
    
    # Initialize system
    system = RemoteMonitoringSystem("Remote Patient Health Monitoring System")
    
    # Add patients with different conditions
    patients_config = {
        'PAT-001': {'name': 'John Smith', 'age': 68, 'condition': 'elderly'},
        'PAT-002': {'name': 'Sarah Johnson', 'age': 45, 'condition': 'chronic'},
        'PAT-003': {'name': 'Michael Brown', 'age': 72, 'condition': 'post_operative'},
        'PAT-004': {'name': 'Emma Davis', 'age': 55, 'condition': 'chronic'},
        'PAT-005': {'name': 'Robert Wilson', 'age': 70, 'condition': 'elderly'},
    }
    
    for patient_id, config in patients_config.items():
        system.add_patient(patient_id, config['name'], config['age'], config['condition'])
        patient = system.patients[patient_id]
        
        # Add sensors to each patient
        patient.add_sensor(f"{patient_id}-HR-01", 'heart_rate', (50, 100))
        patient.add_sensor(f"{patient_id}-TEMP-01", 'temperature', (36.0, 38.5))
        patient.add_sensor(f"{patient_id}-O2-01", 'oxygen', (90, 100))
    
    print(f"\nSystem initialized with {len(patients_config)} patients:")
    for patient_id, config in patients_config.items():
        print(f"  - {patient_id}: {config['name']} ({config['condition']})")
    
    # Simulate 7 days
    print("\nSimulating 7 days of patient monitoring...")
    all_data = []
    
    for day in range(7):
        simulation_date = datetime.now().date() - timedelta(days=6-day)
        daily_data = system.simulate_monitoring_day(simulation_date)
        all_data.append(daily_data)
        
        daily_stats = system.daily_statistics[-1]
        print(f"Day {day+1}: Alerts={daily_stats['total_alerts']}, "
              f"Critical={daily_stats['critical_events']}, "
              f"Status={daily_stats['system_status']}")
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generate_visualizations(system, combined_data)
    
    # Generate report data
    report = system.get_system_report()
    
    print("\n" + "=" * 70)
    print("SYSTEM REPORT")
    print("=" * 70)
    print(f"System Name: {report['system_name']}")
    print(f"Total Patients Monitored: {report['total_patients']}")
    print(f"Total Alerts Generated: {report['total_alerts']}")
    print(f"Critical Events Detected: {report['critical_events']}")
    print(f"Average Daily Alerts: {report['avg_daily_alerts']:.1f}")
    print(f"System Status: {report['system_status']}")
    print(f"Simulation Period: {report['simulation_days']} days")
    print("=" * 70)
    
    # Save data to CSV
    combined_data.to_csv('/home/ubuntu/patient_monitoring_project/monitoring_data.csv', index=False)
    print("\nMonitoring data saved to: monitoring_data.csv")
    
    # Save report to JSON
    report_json = {
        'system_report': report,
        'patients': list(patients_config.keys()),
        'simulation_date': datetime.now().isoformat(),
        'daily_statistics': system.daily_statistics,
        'total_alerts': len(system.all_alerts)
    }
    
    with open('/home/ubuntu/patient_monitoring_project/system_report.json', 'w') as f:
        json.dump(report_json, f, indent=2, default=str)
    
    print("System report saved to: system_report.json")
    
    return system, combined_data


if __name__ == "__main__":
    system, data = main()
