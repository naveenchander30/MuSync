import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Sidebar from "../components/Sidebar";

vi.mock("../api", () => ({
  endpoints: {
    auth: {
      spotifyLogin: () => "https://accounts.spotify.com/authorize?...",
      ytmusicLogin: () => "https://accounts.google.com/o/oauth2/auth?...",
    },
  },
}));

describe("Sidebar", () => {
  it("renders all navigation items", () => {
    render(
      <Sidebar
        currentPage="dashboard"
        onNavigate={() => {}}
        authStatus={{ spotify: false, ytmusic: false }}
      />
    );
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getAllByText("Sync").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Scheduler")).toBeInTheDocument();
  });

  it("highlights the current page with left border", () => {
    render(
      <Sidebar
        currentPage="sync"
        onNavigate={() => {}}
        authStatus={{ spotify: false, ytmusic: false }}
      />
    );
    const navButtons = screen.getAllByRole("button");
    const syncButton = navButtons.find(btn => btn.textContent.includes("Sync"));
    expect(syncButton.className).toContain("border-l-2");
  });

  it("calls onNavigate when a nav item is clicked", () => {
    const onNavigate = vi.fn();
    render(
      <Sidebar
        currentPage="dashboard"
        onNavigate={onNavigate}
        authStatus={{ spotify: false, ytmusic: false }}
      />
    );
    fireEvent.click(screen.getByText("Scheduler"));
    expect(onNavigate).toHaveBeenCalledWith("scheduler");
  });

  it("shows MuSync branding", () => {
    render(
      <Sidebar
        currentPage="dashboard"
        onNavigate={() => {}}
        authStatus={{ spotify: false, ytmusic: false }}
      />
    );
    const logo = document.querySelector(".text-base");
    expect(logo.textContent).toBe("MuSync");
  });

  it("renders Auth component with connection status", () => {
    render(
      <Sidebar
        currentPage="dashboard"
        onNavigate={() => {}}
        authStatus={{ spotify: true, ytmusic: false }}
      />
    );
    expect(screen.getByText("Spotify Connected")).toBeInTheDocument();
    expect(screen.getByText("Connect YT Music")).toBeInTheDocument();
  });

  it("renders Connections section header", () => {
    render(
      <Sidebar
        currentPage="dashboard"
        onNavigate={() => {}}
        authStatus={{ spotify: false, ytmusic: false }}
      />
    );
    expect(screen.getByText("Connections")).toBeInTheDocument();
  });
});
