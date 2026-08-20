# File: tools/scout/src/reporter.py
# Description: Handles generating reports in various formats (TXT, JSON, CSV, HTML).

import json
import csv
from datetime import datetime
from lib.sniper_env import env

class Reporter:
    def __init__(self):
        pass

    def save_json(self, data, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            env.log.error(f"Failed to save JSON report: {e}")
            return False

    def save_txt(self, data, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== SNIPER: Scout Security Report ===\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Target: {data['target']}\n")
                f.write(f"Risk Level: {data['risk_level']} ({data['risk_score']})\n\n")
                
                f.write("--- Analysis Flags ---\n")
                for flag in data['flags']:
                    f.write(f"[!] {flag}\n")
                
                if data.get('reputation'):
                    f.write("\n--- Threat Intelligence ---\n")
                    for source, info in data['reputation'].items():
                        f.write(f"{source}: {info}\n")
                
                f.write("\n--- Network Chain ---\n")
                if 'network' in data and 'chain' in data['network']:
                    for hop in data['network']['chain']:
                        f.write(f" -> {hop['status']} : {hop['url']} ({hop.get('type', 'http')})\n")
                        
            return True
        except Exception as e:
            env.log.error(f"Failed to save TXT report: {e}")
            return False

    def save_html(self, data, filename):
        try:
            # A simple HTML template
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Scout Report: {data['target']}</title>
                <style>
                    body {{ font-family: sans-serif; background: #1e1e1e; color: #eee; padding: 20px; }}
                    .card {{ background: #2d2d2d; padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
                    .critical {{ color: #ff4444; }} .high {{ color: #ff8800; }} .medium {{ color: #ffcc00; }}
                    .box {{ border: 1px solid #444; padding: 10px; }}
                </style>
            </head>
            <body>
                <h1>Scout Analysis Report</h1>
                <div class="card">
                    <h2>Summary</h2>
                    <p><strong>Target:</strong> {data['target']}</p>
                    <p><strong>Final URL:</strong> {data['final_url']}</p>
                    <p><strong>Risk Level:</strong> <span class="{data['risk_level'].lower()}">{data['risk_level']} ({data['risk_score']})</span></p>
                </div>
                
                <div class="card">
                    <h3>Risk Flags</h3>
                    <ul>
                        {''.join(f'<li>{flag}</li>' for flag in data['flags'])}
                    </ul>
                </div>

                <div class="card">
                    <h3>Redirect Chain</h3>
                    <div class="box">
                        {'<br>⬇<br>'.join(f"[{hop['status']}] {hop['url']}" for hop in data.get('network', {}).get('chain', []))}
                    </div>
                </div>
            </body>
            </html>
            """
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            env.log.error(f"Failed to save HTML report: {e}")
            return False

    def export(self, data, filename):
        """Auto-detects format based on extension."""
        if filename.endswith('.json'): return self.save_json(data, filename)
        elif filename.endswith('.txt'): return self.save_txt(data, filename)
        elif filename.endswith('.html'): return self.save_html(data, filename)
        else:
            env.log.error("Unsupported format. Use .json, .txt, or .html")
            return False
