import argparse
import os
import zipfile
import time

EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence")

def export_evidence(target_ip, output_format="zip"):
    if output_format.lower() != "zip":
        print("[!] Currently only 'zip' format is supported.")
        return

    if not os.path.exists(EVIDENCE_DIR):
        print(f"[!] Evidence directory not found at {EVIDENCE_DIR}")
        return

    timestamp = int(time.time())
    zip_filename = f"argus_evidence_{target_ip.replace('/', '_')}_{timestamp}.zip"
    
    files_to_zip = []
    
    # Recursively find any evidence involving the target
    for root, _, files in os.walk(EVIDENCE_DIR):
        for file in files:
            if target_ip.replace("/", "_") in file:
                files_to_zip.append(os.path.join(root, file))
                
    if not files_to_zip:
        print(f"[-] No evidence found for target: {target_ip}")
        return

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_zip:
                # Store in zip relative to the evidence directory
                arcname = os.path.relpath(file_path, EVIDENCE_DIR)
                zipf.write(file_path, arcname)
                
        print(f"[+] Successfully exported {len(files_to_zip)} evidence files to: {os.path.abspath(zip_filename)}")
    except Exception as e:
        print(f"[!] Export failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Argus Command CLI interface")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    export_parser = subparsers.add_parser("export-evidence", help="Export collected evidence for a specific target")
    export_parser.add_argument("--target", required=True, help="Target IP or CIDR to filter evidence for")
    export_parser.add_argument("--format", default="zip", help="Output format (default: zip)")

    args = parser.parse_args()

    if args.command == "export-evidence":
        export_evidence(args.target, args.format)

if __name__ == "__main__":
    main()
