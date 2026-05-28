import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import Dashboard from "../components/Dashboard";

const mockJobs = [
  {
    id: "job_1",
    status: "success",
    source_service: "spotify",
    target_service: "ytmusic",
    added_tracks: 15,
    failed_tracks: 2,
    total_tracks: 17,
    started_at: "2026-05-27T10:00:00Z",
    completed_at: "2026-05-27T10:05:00Z",
    error_message: null,
    progress_percentage: 100,
  },
  {
    id: "job_2",
    status: "failed",
    source_service: "ytmusic",
    target_service: "spotify",
    added_tracks: 0,
    failed_tracks: 5,
    total_tracks: 5,
    started_at: "2026-05-27T09:00:00Z",
    completed_at: "2026-05-27T09:02:00Z",
    error_message: "API rate limit exceeded",
    progress_percentage: 50,
  },
  {
    id: "job_3",
    status: "running",
    source_service: "spotify",
    target_service: "ytmusic",
    added_tracks: 8,
    failed_tracks: 1,
    total_tracks: 25,
    started_at: "2026-05-27T11:00:00Z",
    completed_at: null,
    error_message: null,
    progress_percentage: 45,
    current_playlist_name: "My Mix",
    current_track_name: "Test Song",
    current_track_artist: "Test Artist",
    current_track_image_url: "https://example.com/art.jpg",
  },
];

vi.mock("../api", () => ({
  endpoints: {
    jobs: {
      getByUser: () => Promise.resolve({ data: mockJobs }),
    },
    sync: {
      spotifyToYt: vi.fn().mockResolvedValue({}),
      ytToSpotify: vi.fn().mockResolvedValue({}),
    },
  },
}));

describe("Dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state initially", () => {
    render(<Dashboard />);
    expect(screen.getByText("Loading dashboard...")).toBeInTheDocument();
  });

  it("renders stats after loading", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("Total Syncs")).toBeInTheDocument();
    });
    const totals = screen.getAllByText("3");
    expect(totals.length).toBeGreaterThanOrEqual(1);
  });

  it("shows stats labels", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("Total Syncs")).toBeInTheDocument();
      expect(screen.getByText("Successful")).toBeInTheDocument();
      expect(screen.getAllByText("Running").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows active sync banner for running job", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("Sync in Progress")).toBeInTheDocument();
    });
  });

  it("shows progress percentage in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("45%")).toBeInTheDocument();
    });
  });

  it("shows added tracks count in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("+8")).toBeInTheDocument();
    });
  });

  it("shows current playlist name in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("My Mix")).toBeInTheDocument();
    });
  });

  it("shows current track info in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Test Song/)).toBeInTheDocument();
    });
  });

  it("shows album art image in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      const img = screen.getByAltText("Album art");
      expect(img).toHaveAttribute("src", "https://example.com/art.jpg");
    });
  });

  it("shows track artist in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Test Artist/)).toBeInTheDocument();
    });
  });

  it("renders filter tabs", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("All")).toBeInTheDocument();
      expect(screen.getByText("Success")).toBeInTheDocument();
      expect(screen.getAllByText("Running").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("renders sync history entries", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      const matches = screen.getAllByText(/Spotify.*YT Music/);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows error message for failed job", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("API rate limit exceeded")).toBeInTheDocument();
    });
  });

  it("shows track counts in job entries", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/15 added/)).toBeInTheDocument();
      expect(screen.getByText(/2 failed/)).toBeInTheDocument();
    });
  });

  it("shows quick action buttons", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getAllByText("Quick Sync").length).toBe(2);
      expect(screen.getByText("Auto Sync")).toBeInTheDocument();
    });
  });
});
