"""
Analyze and visualize Locust performance test results
Generates comparison charts between monolithic and microservices architectures
"""
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime
import json

# Set style for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')


def load_stats(stats_file):
    """Load statistics from Locust CSV file."""
    try:
        df = pd.read_csv(stats_file)
        return df
    except Exception as e:
        print(f"Error loading {stats_file}: {e}")
        return None


def safe_pad_data(mono_data, micro_data):
    """Safely pad data arrays to match lengths."""
    mono_len = len(mono_data)
    micro_len = len(micro_data)
    
    if mono_len == micro_len:
        return list(mono_data), list(micro_data)
    elif mono_len > micro_len:
        micro_padded = list(micro_data) + [0] * (mono_len - micro_len)
        return list(mono_data), micro_padded
    else:
        mono_padded = list(mono_data) + [0] * (micro_len - mono_len)
        return mono_padded, list(micro_data)


def create_response_time_chart(mono_stats, micro_stats, output_dir):
    """Create response time comparison chart."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Filter out aggregated rows
    mono_filtered = mono_stats[~mono_stats['Name'].isin(['Aggregated', 'Total'])]
    micro_filtered = micro_stats[~micro_stats['Name'].isin(['Aggregated', 'Total'])]
    
    # Check if we have data to compare
    if len(mono_filtered) == 0 and len(micro_filtered) == 0:
        ax.text(0.5, 0.5, 'No data available for comparison\n(Test may not have completed successfully)', 
                ha='center', va='center', fontsize=16)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/response_time_comparison.png', dpi=300, bbox_inches='tight')
        print(f"⚠ Created placeholder: {output_dir}/response_time_comparison.png (no data)")
        plt.close()
        return
    
    # Use the longer list of endpoints for x-axis
    if len(mono_filtered) >= len(micro_filtered):
        endpoint_names = mono_filtered['Name'].tolist()
        mono_times = mono_filtered['Average Response Time'].tolist()
        micro_times = micro_filtered['Average Response Time'].tolist() if len(micro_filtered) > 0 else []
    else:
        endpoint_names = micro_filtered['Name'].tolist()
        mono_times = mono_filtered['Average Response Time'].tolist() if len(mono_filtered) > 0 else []
        micro_times = micro_filtered['Average Response Time'].tolist()
    
    # Pad data to match
    mono_times, micro_times = safe_pad_data(mono_times, micro_times)
    
    x = range(len(endpoint_names))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], mono_times, width, 
                   label='Monolithic', alpha=0.8, color='#2E86AB')
    bars2 = ax.bar([i + width/2 for i in x], micro_times, width,
                   label='Microservices', alpha=0.8, color='#A23B72')
    
    ax.set_xlabel('API Endpoint', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Response Time Comparison by Endpoint', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(endpoint_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/response_time_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created: {output_dir}/response_time_comparison.png")
    plt.close()


def create_requests_per_second_chart(mono_stats, micro_stats, output_dir):
    """Create requests per second comparison chart."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Filter out aggregated rows
    mono_filtered = mono_stats[~mono_stats['Name'].isin(['Aggregated', 'Total'])]
    micro_filtered = micro_stats[~micro_stats['Name'].isin(['Aggregated', 'Total'])]
    
    if len(mono_filtered) == 0 and len(micro_filtered) == 0:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=16)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/throughput_comparison.png', dpi=300, bbox_inches='tight')
        print(f"⚠ Created placeholder: {output_dir}/throughput_comparison.png (no data)")
        plt.close()
        return
    
    if len(mono_filtered) >= len(micro_filtered):
        endpoint_names = mono_filtered['Name'].tolist()
        mono_rps = mono_filtered['Requests/s'].tolist()
        micro_rps = micro_filtered['Requests/s'].tolist() if len(micro_filtered) > 0 else []
    else:
        endpoint_names = micro_filtered['Name'].tolist()
        mono_rps = mono_filtered['Requests/s'].tolist() if len(mono_filtered) > 0 else []
        micro_rps = micro_filtered['Requests/s'].tolist()
    
    mono_rps, micro_rps = safe_pad_data(mono_rps, micro_rps)
    
    x = range(len(endpoint_names))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], mono_rps, width,
                   label='Monolithic', alpha=0.8, color='#06A77D')
    bars2 = ax.bar([i + width/2 for i in x], micro_rps, width,
                   label='Microservices', alpha=0.8, color='#F77F00')
    
    ax.set_xlabel('API Endpoint', fontsize=12, fontweight='bold')
    ax.set_ylabel('Requests per Second', fontsize=12, fontweight='bold')
    ax.set_title('Throughput Comparison by Endpoint', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(endpoint_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/throughput_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created: {output_dir}/throughput_comparison.png")
    plt.close()


def create_failure_rate_chart(mono_stats, micro_stats, output_dir):
    """Create failure rate comparison chart."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    mono_filtered = mono_stats[~mono_stats['Name'].isin(['Aggregated', 'Total'])]
    micro_filtered = micro_stats[~mono_stats['Name'].isin(['Aggregated', 'Total'])]
    
    if len(mono_filtered) == 0 and len(micro_filtered) == 0:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=16)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/failure_rate_comparison.png', dpi=300, bbox_inches='tight')
        print(f"⚠ Created placeholder: {output_dir}/failure_rate_comparison.png (no data)")
        plt.close()
        return
    
    if len(mono_filtered) >= len(micro_filtered):
        endpoint_names = mono_filtered['Name'].tolist()
        mono_failure = (mono_filtered['# Failures'] / mono_filtered['# Requests'] * 100).fillna(0).tolist()
        micro_failure = (micro_filtered['# Failures'] / micro_filtered['# Requests'] * 100).fillna(0).tolist() if len(micro_filtered) > 0 else []
    else:
        endpoint_names = micro_filtered['Name'].tolist()
        mono_failure = (mono_filtered['# Failures'] / mono_filtered['# Requests'] * 100).fillna(0).tolist() if len(mono_filtered) > 0 else []
        micro_failure = (micro_filtered['# Failures'] / micro_filtered['# Requests'] * 100).fillna(0).tolist()
    
    mono_failure, micro_failure = safe_pad_data(mono_failure, micro_failure)
    
    x = range(len(endpoint_names))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], mono_failure, width,
                   label='Monolithic', alpha=0.8, color='#C1121F')
    bars2 = ax.bar([i + width/2 for i in x], micro_failure, width,
                   label='Microservices', alpha=0.8, color='#780000')
    
    ax.set_xlabel('API Endpoint', fontsize=12, fontweight='bold')
    ax.set_ylabel('Failure Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Failure Rate Comparison by Endpoint', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(endpoint_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/failure_rate_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created: {output_dir}/failure_rate_comparison.png")
    plt.close()


def create_percentile_comparison_chart(mono_stats, micro_stats, output_dir):
    """Create percentile response time comparison chart."""
    # Get aggregated row
    mono_agg = mono_stats[mono_stats['Name'] == 'Aggregated']
    micro_agg = micro_stats[micro_stats['Name'] == 'Aggregated']
    
    if len(mono_agg) == 0 and len(micro_agg) == 0:
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, 'No aggregated data available', ha='center', va='center', fontsize=16)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/percentile_comparison.png', dpi=300, bbox_inches='tight')
        print(f"⚠ Created placeholder: {output_dir}/percentile_comparison.png (no data)")
        plt.close()
        return
    
    mono_agg = mono_agg.iloc[0] if len(mono_agg) > 0 else None
    micro_agg = micro_agg.iloc[0] if len(micro_agg) > 0 else None
    
    percentiles = ['50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '99.9%', '100%']
    
    mono_values = [mono_agg[p] if mono_agg is not None and p in mono_agg else 0 for p in percentiles]
    micro_values = [micro_agg[p] if micro_agg is not None and p in micro_agg else 0 for p in percentiles]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = range(len(percentiles))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], mono_values, width,
                   label='Monolithic', alpha=0.8, color='#2E86AB')
    bars2 = ax.bar([i + width/2 for i in x], micro_values, width,
                   label='Microservices', alpha=0.8, color='#A23B72')
    
    ax.set_xlabel('Percentile', fontsize=12, fontweight='bold')
    ax.set_ylabel('Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Response Time Percentiles Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(percentiles)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontsize=8, rotation=0)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/percentile_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created: {output_dir}/percentile_comparison.png")
    plt.close()


def create_summary_table(mono_stats, micro_stats, output_dir):
    """Create summary comparison table."""
    # Get aggregated rows
    mono_agg = mono_stats[mono_stats['Name'] == 'Aggregated']
    micro_agg = micro_stats[micro_stats['Name'] == 'Aggregated']
    
    if len(mono_agg) == 0 or len(micro_agg) == 0:
        # Create a warning summary
        with open(f'{output_dir}/summary.txt', 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE TEST SUMMARY - INCOMPLETE DATA\n")
            f.write("=" * 80 + "\n\n")
            if len(mono_agg) == 0:
                f.write("⚠ Monolithic test did not complete successfully\n")
            if len(micro_agg) == 0:
                f.write("⚠ Microservices test did not complete successfully\n")
            f.write("\nPlease run the tests again with a longer duration (e.g., RUN_TIME=3m)\n")
            f.write("\n" + "=" * 80 + "\n")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, 'Insufficient data for summary\nPlease run tests with longer duration', 
                ha='center', va='center', fontsize=16)
        ax.axis('off')
        plt.savefig(f'{output_dir}/summary_table.png', dpi=300, bbox_inches='tight')
        print(f"⚠ Created: {output_dir}/summary.txt (incomplete data)")
        print(f"⚠ Created placeholder: {output_dir}/summary_table.png (incomplete data)")
        plt.close()
        return
    
    mono_agg = mono_agg.iloc[0]
    micro_agg = micro_agg.iloc[0]
    
    summary_data = {
        'Metric': [
            'Total Requests',
            'Total Failures',
            'Failure Rate (%)',
            'Requests/sec',
            'Avg Response Time (ms)',
            'Min Response Time (ms)',
            'Max Response Time (ms)',
            '50th Percentile (ms)',
            '95th Percentile (ms)',
            '99th Percentile (ms)'
        ],
        'Monolithic': [
            f"{mono_agg['# Requests']:.0f}",
            f"{mono_agg['# Failures']:.0f}",
            f"{(mono_agg['# Failures'] / mono_agg['# Requests'] * 100):.2f}",
            f"{mono_agg['Requests/s']:.2f}",
            f"{mono_agg['Average Response Time']:.2f}",
            f"{mono_agg['Min Response Time']:.2f}",
            f"{mono_agg['Max Response Time']:.2f}",
            f"{mono_agg['50%']:.2f}",
            f"{mono_agg['95%']:.2f}",
            f"{mono_agg['99%']:.2f}"
        ],
        'Microservices': [
            f"{micro_agg['# Requests']:.0f}",
            f"{micro_agg['# Failures']:.0f}",
            f"{(micro_agg['# Failures'] / micro_agg['# Requests'] * 100):.2f}",
            f"{micro_agg['Requests/s']:.2f}",
            f"{micro_agg['Average Response Time']:.2f}",
            f"{micro_agg['Min Response Time']:.2f}",
            f"{micro_agg['Max Response Time']:.2f}",
            f"{micro_agg['50%']:.2f}",
            f"{micro_agg['95%']:.2f}",
            f"{micro_agg['99%']:.2f}"
        ]
    }
    
    df = pd.DataFrame(summary_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=df.values, colLabels=df.columns,
                    cellLoc='center', loc='center',
                    colColours=['#E8E8E8']*3)
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(df) + 1):
        for j in range(3):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F2F2F2')
    
    plt.title('Performance Metrics Summary', fontsize=16, fontweight='bold', pad=20)
    plt.savefig(f'{output_dir}/summary_table.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created: {output_dir}/summary_table.png")
    plt.close()
    
    # Also save as text
    with open(f'{output_dir}/summary.txt', 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("PERFORMANCE TEST SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(df.to_string(index=False))
        f.write("\n\n" + "=" * 80 + "\n")
    
    print(f"✓ Created: {output_dir}/summary.txt")


def main():
    """Main analysis function."""
    if len(sys.argv) < 3:
        print("Usage: python analyze_results.py <mono_stats.csv> <micro_stats.csv> [output_dir]")
        sys.exit(1)
    
    mono_stats_file = sys.argv[1]
    micro_stats_file = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "results"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("PERFORMANCE TEST ANALYSIS")
    print("=" * 80)
    print(f"Loading data...")
    
    # Load statistics
    mono_stats = load_stats(mono_stats_file)
    micro_stats = load_stats(micro_stats_file)
    
    if mono_stats is None or micro_stats is None:
        print("Error: Could not load statistics files")
        sys.exit(1)
    
    print(f"✓ Loaded monolithic stats: {len(mono_stats)} rows")
    print(f"✓ Loaded microservices stats: {len(micro_stats)} rows")
    print(f"\nGenerating visualizations...")
    
    # Create all charts
    create_response_time_chart(mono_stats, micro_stats, output_dir)
    create_requests_per_second_chart(mono_stats, micro_stats, output_dir)
    create_failure_rate_chart(mono_stats, micro_stats, output_dir)
    create_percentile_comparison_chart(mono_stats, micro_stats, output_dir)
    create_summary_table(mono_stats, micro_stats, output_dir)
    
    print("\n" + "=" * 80)
    print(f"ANALYSIS COMPLETE!")
    print(f"Results saved to: {output_dir}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
