import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import SyncPanel from "../components/SyncPanel";

const mockSpotifyToYt = vi.fn().mockResolvedValue({});
const mockYtToSpotify = vi.fn().mockResolvedValue({});

vi.mock("../api", () => ({
  endpoints: {
    sync: {
      spotifyToYt: () => mockSpotifyToYt(),
      ytToSpotify: () => mockYtToSpotify(),
    },
  },
}));

describe("SyncPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.alert = vi.fn();
  });

  it("renders the sync panel title", () => {
    render(<SyncPanel authStatus={{ spotify: true, ytmusic: true }} />);
    expect(screen.getByText("Sync Music")).toBeInTheDocument();
  });

  it("renders sync type options", () => {
    render(<SyncPanel authStatus={{ spotify: true, ytmusic: true }} />);
    expect(screen.getByText("Full Library")).toBeInTheDocument();
    expect(screen.getByText("Selected Playlists")).toBeInTheDocument();
    expect(screen.getByText("Incremental")).toBeInTheDocument();
  });

  it("renders source and target dropdowns", () => {
    render(<SyncPanel authStatus={{ spotify: true, ytmusic: true }} />);
    expect(screen.getByText("From")).toBeInTheDocument();
    expect(screen.getByText("To")).toBeInTheDocument();
  });

  it("renders toggle options", () => {
    render(<SyncPanel authStatus={{ spotify: true, ytmusic: true }} />);
    expect(screen.getByText("Include liked songs")).toBeInTheDocument();
    expect(screen.getByText("Match by metadata")).toBeInTheDocument();
    expect(screen.getByText("Auto-resolve conflicts")).toBeInTheDocument();
  });

  it("shows Start New Sync button", () => {
    render(<SyncPanel authStatus={{ spotify: true, ytmusic: true }} />);
    expect(screen.getByText("Start New Sync")).toBeInTheDocument();
  });

  it("calls spotifyToYt when Start New Sync is clicked with spotify source", async () => {
    render(<SyncPanel authStatus={{ spotify: true, ytmusic: true }} />);
    fireEvent.click(screen.getByText("Start New Sync"));
    await waitFor(() => {
      expect(mockSpotifyToYt).toHaveBeenCalled();
    });
  });
});
