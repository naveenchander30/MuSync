# MuSync

**MuSync** is a cross-platform command-line tool for exporting and importing playlists and liked songs between Spotify and YouTube Music. Seamlessly transfer your music library between services with a simple CLI interface.

---

## Features

- **Export** playlists and liked songs from Spotify and YouTube Music
- **Import** playlists and liked songs to Spotify and YouTube Music
- **Fuzzy matching** for accurate track mapping across platforms
- **Simple CLI**: No browser extensions or manual copying required
- **Secure authentication** via a hosted service (no need to manage OAuth credentials)

---

## Authentication

Authentication is securely managed via a hosted service on [Render](https://musync-k60r.onrender.com).  
When prompted, simply follow the authentication instructions in your browser. No sensitive credentials are stored locally.

---

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/naveenchander30/musync.git
    cd musync
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

---

## Usage

Launch the CLI tool:

```sh
python musync_cli.py
```

You will be presented with a menu to:

- Export from Spotify
- Import to Spotify
- Export from YouTube Music
- Import to YouTube Music

Simply enter the number corresponding to your desired action and follow the on-screen instructions.

**Note:**  
- Exported playlists and liked songs are saved as `playlists.json` and `liked.json` in your working directory.
- These files are used for importing into the target platform.

---

## Example Workflow

1. **Export from Spotify:**
    - Choose "Export from Spotify" in the CLI.
    - Authenticate via the browser.
    - `playlists.json` and `liked.json` will be created.

2. **Import to YouTube Music:**
    - Choose "Import to YouTube Music" in the CLI.
    - Authenticate via the browser.
    - Your playlists and liked songs will be imported.

---

## Security & Privacy

- Authentication is handled via [https://musync-k60r.onrender.com](https://musync-k60r.onrender.com).
- No passwords or long-term tokens are stored locally.
- Only temporary tokens are used for the duration of the session.

---

## License

This project is licensed under the [MIT License](LICENSE.md).

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements or bug fixes.

---

## Disclaimer

MuSync is not affiliated with Spotify or YouTube Music. Use at your own
