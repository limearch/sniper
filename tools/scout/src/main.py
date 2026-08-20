# File: tools/scout/src/main.py
# Description: Main entry point. (Updated to use .env keys)

import sys
import json
import argparse
from pathlib import Path

# --- SNIPER Environment Integration ---
try:
    _PROJECT_ROOT = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(_PROJECT_ROOT))
    from lib.sniper_env import env
    from lib.help_renderer import render_help
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.tree import Tree
    from rich.columns import Columns
    from rich import box
except ImportError:
    print("[CRITICAL] Sniper environment not found.", file=sys.stderr)
    sys.exit(1)

# Local Imports
try:
    from .network import NetworkHandler
    from .analyzer import UrlAnalyzer
    from .reporter import Reporter
except ImportError:
    from network import NetworkHandler
    from analyzer import UrlAnalyzer
    from reporter import Reporter

console = Console()

def load_api_keys():
    """
    Loads API keys with priority: 
    1. .env file (Best practice)
    2. sniper-config.json (Legacy/Backup)
    """
    # 1. Load from JSON Config (Legacy)
    keys = env.config.get('tools', {}).get('scout', {}).get('api_keys', {}).copy()
    
    # 2. Override/Add from .env (SniperEnv loads this into env.api_keys)
    # Mapping .env variable names to internal keys
    env_map = {
        "VIRUSTOTAL_API_KEY": "virustotal",
        "GOOGLE_SAFE_BROWSING_KEY": "google_safe_browsing",
        "URLHAUS_API_KEY": "urlhaus"
    }
    
    for env_var, internal_key in env_map.items():
        if env_var in env.api_keys:
            keys[internal_key] = env.api_keys[env_var]
            
    return keys

def show_help():
    help_file = env.ROOT_DIR / "share" / "readme" / "scout.json"
    if help_file.exists():
        with open(help_file) as f:
            render_help(json.load(f))
    sys.exit(0)

def process_single_url(url, network, analyzer, args):
    if args.offline:
        net_data = {
            "original_url": url,
            "final_url": url,
            "status_code": 0,
            "chain": [],
            "analysis": {},
            "error": "Offline Mode"
        }
    else:
        net_data = network.expand_url(url)

    final_url = net_data.get("final_url", url)

    clean_link, removed_trackers = analyzer.clean_url(final_url)
    score, level, flags, rep_data = analyzer.assess_risk(final_url, network_analysis=net_data.get('analysis'))

    result_obj = {
        "target": url,
        "final_url": final_url,
        "status": net_data.get("status_code", 0),
        "redirects": len(net_data.get("chain", [])),
        "chain": net_data.get("chain", []),
        "network_analysis": net_data.get("analysis", {}),
        "clean_link": clean_link,
        "trackers_removed": removed_trackers,
        "risk_score": score,
        "risk_level": level,
        "flags": flags,
        "reputation": rep_data,
        "error": net_data.get("error")
    }
    return result_obj

def print_rich_output(result):
    if result['risk_level'] == "SAFE":
        theme_color = "green"
        icon = "✅"
    elif result['risk_level'] == "SUSPICIOUS":
        theme_color = "yellow"
        icon = "⚠️"
    elif result['risk_level'] == "MALICIOUS":
        theme_color = "red"
        icon = "🚫"
    else:
        theme_color = "bold red"
        icon = "💀"

    summary_grid = Table.grid(expand=True, padding=(0, 1))
    summary_grid.add_column(justify="left", ratio=1)
    summary_grid.add_column(justify="right")
    
    summary_grid.add_row(
        f"[bold]Target:[/bold] [dim]{result['target']}[/]",
        f"Risk Score: [bold {theme_color}]{result['risk_score']}[/]"
    )
    
    status_code = result.get('status', 0)
    status_color = 'green' if status_code < 400 else 'red'
    
    if result['target'] != result['final_url']:
        summary_grid.add_row(
            f"[bold]Final Destination:[/bold] [cyan]{result['final_url']}[/]",
            f"Status: [{status_color}]{status_code}[/]"
        )
    else:
        summary_grid.add_row(
            f"[bold]Status Code:[/bold] [{status_color}]{status_code}[/]", ""
        )

    console.print(Panel(summary_grid, title=f"{icon} [bold {theme_color}]Scout Analysis Report: {result['risk_level']}[/]", border_style=theme_color))

    left_content = []
    right_content = []

    if result['chain']:
        tree = Tree(f"[bold cyan]Redirect Chain ({len(result['chain'])})[/]")
        for hop in result['chain']:
            hop_type = hop.get('type', 'http')
            type_icon = "🔄" if hop_type == 'meta_refresh' else "🔗"
            s_code = hop.get('status', 0)
            status_style = "green" if s_code < 300 else "yellow" if s_code < 400 else "red"
            
            node_text = f"[{status_style}]{s_code}[/] {type_icon} [dim]{hop['url']}[/]"
            if hop_type == 'meta_refresh':
                node_text += " [bold yellow](Meta Refresh)[/]"
            tree.add(node_text)
        left_content.append(Panel(tree, title="Network Trace", border_style="cyan", box=box.ROUNDED))
    elif result['error'] == "Offline Mode":
        left_content.append(Panel("[dim]Network analysis skipped (Offline)[/]", title="Network Trace", border_style="dim"))
    
    net_analysis = result.get('network_analysis', {})
    if any(net_analysis.values()):
        net_table = Table(box=None, show_header=False)
        net_table.add_column()
        if net_analysis.get('meta_refresh_detected'): net_table.add_row("[red]! Client-Side Redirect Detected[/]")
        if net_analysis.get('circular_redirect'): net_table.add_row("[red]! Circular Redirect Loop[/]")
        if net_analysis.get('downgrade_detected'): net_table.add_row("[red]! Protocol Downgrade (HTTPS->HTTP)[/]")
        if net_analysis.get('file_direct_download'): net_table.add_row("[red]! Direct File Download[/]")
        left_content.append(Panel(net_table, title="Network Behavior", border_style="red"))

    if result['flags']:
        flag_table = Table(box=None, show_header=False, padding=(0, 1))
        flag_table.add_column("Indicator", style="red")
        for flag in result['flags']:
            flag_table.add_row(f"• {flag}")
        right_content.append(Panel(flag_table, title="Risk Indicators", border_style="red", box=box.ROUNDED))
    else:
        right_content.append(Panel("[green]No significant risk indicators found.[/]", title="Risk Indicators", border_style="green"))

    if result['trackers_removed']:
        tracker_text = Text()
        tracker_text.append("Cleaned URL:\n", style="bold")
        tracker_text.append(f"{result['clean_link']}\n\n", style="cyan")
        tracker_text.append("Removed Trackers:\n", style="bold")
        tracker_text.append(", ".join(result['trackers_removed']), style="magenta")
        right_content.append(Panel(tracker_text, title="Privacy & Hygiene", border_style="magenta"))

    if result.get('reputation'):
        rep_text = Text()
        for source, info in result['reputation'].items():
            rep_text.append(f"{source}: ", style="bold")
            rep_text.append(f"{info}\n")
        right_content.append(Panel(rep_text, title="Threat Intelligence", border_style="blue"))

    console.print(Columns([Group(*left_content), Group(*right_content)], expand=True))
    
    if result['error'] and result['error'] != "Offline Mode":
        console.print(f"[bold red]Network Error: {result['error']}[/]")
    console.print("")

def extract_url_from_input(input_data):
    if isinstance(input_data, dict):
        for key in ['url', 'final_url', 'link', 'target']:
            if key in input_data:
                return input_data[key]
        return None
    return str(input_data).strip()

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("url", nargs='?')
    parser.add_argument("-o", "--output", help="Output report file (.json, .txt, .html)")
    parser.add_argument("--json", action="store_true", help="Raw JSON output to stdout")
    parser.add_argument("--offline", action="store_true", help="Disable all network activity")
    parser.add_argument("--reputation", action="store_true", help="Enable API-based threat checks (VT, etc)")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()

    if args.help:
        show_help()

    api_keys = load_api_keys()
    network = NetworkHandler()
    analyzer = UrlAnalyzer(
        offline_mode=args.offline,
        use_reputation=args.reputation,
        api_config=api_keys
    )
    reporter = Reporter()

    target_url = ""
    if args.stdin or not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line: 
                target_url = line
                break
    elif args.url:
        target_url = args.url
    
    if not target_url:
        console.print("[red]No URL provided.[/]")
        sys.exit(1)

    with console.status(f"[cyan]Analyzing {target_url}...[/]"):
        res = process_single_url(target_url, network, analyzer, args)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_rich_output(res)

    if args.output:
        if reporter.export(res, args.output):
            console.print(f"[green]Report saved to {args.output}[/]")

if __name__ == "__main__":
    main()
    
