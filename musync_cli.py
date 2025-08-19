# musync_cli.py

import subprocess

def main():
    print("MuSync CLI")
    print("1. Export from Spotify")
    print("2. Import to Spotify")
    print("3. Export from YouTube Music")
    print("4. Import to YouTube Music")
    choice = input("Select an option (1-4): ").strip()

    script_map = {
        "1": "spotify_export.py",
        "2": "spotify_import.py",
        "3": "ytmusic_export.py",
        "4": "ytmusic_import.py"
    }

    script = script_map.get(choice)
    if not script:
        print("Invalid choice.")
        return

    try:
        subprocess.run(["python", script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")

if __name__ == "__main__":
    main()