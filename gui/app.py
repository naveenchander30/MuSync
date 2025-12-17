import tkinter as tk
from gui.state import SyncState
from sync.spotify_import import import_spotify
from config import AUTH_SERVER


class MuSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MuSync")
        self.geometry("900x600")
        self.state = SyncState()

        self.label = tk.Label(self, text="Idle", font=("Arial", 14))
        self.label.pack(pady=10)

        self.log = tk.Text(self)
        self.log.pack(expand=True, fill="both")

        tk.Button(
            self,
            text="Import Spotify → YTMusic",
            command=self.run
        ).pack(pady=10)

    def update_ui(self, state):
        self.label.config(text=f"Processing: {state.current_playlist}")
        self.log.insert(
            "end",
            f"Added: {len(state.added)} | Failed: {len(state.failed)}\n"
        )
        self.log.see("end")

    def run(self):
        self.state.reset()
        import_spotify(AUTH_SERVER, self.state, self.update_ui)

if __name__ == "__main__":
    MuSyncApp().mainloop()
