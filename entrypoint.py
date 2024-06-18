import argparse
import subprocess
import os

def main():
    parser = argparse.ArgumentParser(description='Choose which script to run.')
    parser.add_argument('script', type=str, choices=['scraping', 'data_analysis'], help='The script to run: scraping or data_analysis')
    parser.add_argument('file_path', type=str, nargs='?', help='Path to the Excel file (required for scraping)')
    args = parser.parse_args()

    # List files in the /data directory for debugging
    print("Files in /data:")
    print(os.listdir('/data'))

    print(f"Script to run: {args.script}")
    if args.file_path:
        print(f"File path: {args.file_path}")

    if args.script == 'scraping':
        if not args.file_path:
            raise ValueError("file_path is required for scraping")
        subprocess.run(['python', 'scraping.py', args.file_path])
    elif args.script == 'data_analysis':
        subprocess.run(['python', 'data_analysis.py'])

if __name__ == "__main__":
    main()

