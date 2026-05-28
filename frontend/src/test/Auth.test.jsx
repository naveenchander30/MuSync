import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Auth from "../components/Auth";

vi.mock("../api", () => ({
  endpoints: {
    auth: {
      spotifyLogin: () => "https://accounts.spotify.com/authorize?...",
      ytmusicLogin: () => "https://accounts.google.com/o/oauth2/auth?...",
    },
  },
}));

describe("Auth", () => {
  it('shows "Connect Spotify" when not connected', () => {
    render(<Auth authStatus={{ spotify: false, ytmusic: false }} />);
    expect(screen.getByText("Connect Spotify")).toBeInTheDocument();
  });

  it('shows "Spotify Connected" when connected', () => {
    render(<Auth authStatus={{ spotify: true, ytmusic: false }} />);
    expect(screen.getByText("Spotify Connected")).toBeInTheDocument();
  });

  it('shows "Connect YT Music" when not connected', () => {
    render(<Auth authStatus={{ spotify: false, ytmusic: false }} />);
    expect(screen.getByText("Connect YT Music")).toBeInTheDocument();
  });

  it('shows "YT Music Connected" when connected', () => {
    render(<Auth authStatus={{ spotify: false, ytmusic: true }} />);
    expect(screen.getByText("YT Music Connected")).toBeInTheDocument();
  });

  it("redirects on Spotify connect click", () => {
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: "" };

    render(<Auth authStatus={{ spotify: false, ytmusic: false }} />);
    fireEvent.click(screen.getByText("Connect Spotify"));
    expect(window.location.href).toContain("spotify.com");

    window.location = originalLocation;
  });

  it("redirects on YT Music connect click", () => {
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: "" };

    render(<Auth authStatus={{ spotify: false, ytmusic: false }} />);
    fireEvent.click(screen.getByText("Connect YT Music"));
    expect(window.location.href).toContain("google.com");

    window.location = originalLocation;
  });
});
