import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import SchedulerManager from "../components/SchedulerManager";

const mockCreate = vi.fn().mockResolvedValue({});
const mockUpdate = vi.fn().mockResolvedValue({});
const mockDelete = vi.fn().mockResolvedValue({});

const mockJobs = [
  {
    id: "job_1",
    name: "Daily Sync",
    source_service: "spotify",
    target_service: "ytmusic",
    interval_minutes: 60,
    enabled: true,
    next_run: "2026-05-28T00:00:00Z",
    last_run: null,
  },
  {
    id: "job_2",
    name: "Weekly Backup",
    source_service: "ytmusic",
    target_service: "spotify",
    interval_minutes: 1440,
    enabled: false,
    next_run: null,
    last_run: "2026-05-26T00:00:00Z",
  },
];

vi.mock("../api", () => ({
  endpoints: {
    scheduler: {
      getByUser: () => Promise.resolve({ data: mockJobs }),
      create: (data) => {
        mockCreate(data);
        return Promise.resolve({});
      },
      update: (id, data) => {
        mockUpdate(id, data);
        return Promise.resolve({});
      },
      delete: (id) => {
        mockDelete(id);
        return Promise.resolve({});
      },
    },
  },
}));

describe("SchedulerManager", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.alert = vi.fn();
    window.confirm = vi.fn().mockReturnValue(true);
  });

  it("shows loading state initially", () => {
    render(<SchedulerManager />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders the scheduler page title after loading", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      expect(screen.getByText("Scheduled Syncs")).toBeInTheDocument();
    });
  });

  it("renders scheduled jobs after loading", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      expect(screen.getByText("Daily Sync")).toBeInTheDocument();
      expect(screen.getByText("Weekly Backup")).toBeInTheDocument();
    });
  });

  it("shows directional info for each job", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      expect(screen.getAllByText(/spotify/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows Create Schedule button", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      expect(screen.getByText("Create Schedule")).toBeInTheDocument();
    });
  });

  it("opens create form when Create Schedule clicked", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      fireEvent.click(screen.getByText("Create Schedule"));
    });
    expect(screen.getByText("Save")).toBeInTheDocument();
    expect(screen.getByText("Cancel")).toBeInTheDocument();
  });

  it("closes form when Cancel button clicked", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      fireEvent.click(screen.getByText("Create Schedule"));
    });
    const cancelButtons = screen.getAllByText("Cancel");
    fireEvent.click(cancelButtons[0]);
    await waitFor(() => {
      expect(screen.queryByText("Save")).not.toBeInTheDocument();
    });
  });

  it("calls delete when delete button clicked", async () => {
    render(<SchedulerManager />);
    await waitFor(() => {
      const deleteButtons = screen.getAllByText("Delete");
      fireEvent.click(deleteButtons[0]);
    });
    expect(mockDelete).toHaveBeenCalledWith("job_1");
  });
});
