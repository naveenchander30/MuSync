import { stitch } from '@google/stitch-sdk';
import { writeFileSync } from 'fs';

const PROJECT_ID = '1690119060883562944';
const DESIGN_SYSTEM = 'assets/5701983260865948581';

async function generatePage(name, prompt) {
  console.log(`\n=== Generating ${name} ===`);
  const project = stitch.project(PROJECT_ID);
  const screen = await project.generate(prompt, 'DESKTOP', 'GEMINI_3_1_PRO');
  const htmlUrl = await screen.getHtml();
  const imgUrl = await screen.getImage();
  console.log(`Screen ID: ${screen.screenId}`);
  console.log(`HTML URL: ${htmlUrl}`);
  console.log(`Image URL: ${imgUrl}`);

  // Download and save HTML
  const resp = await fetch(htmlUrl);
  const html = await resp.text();
  const filePath = `docs/stitch-designs/${name.toLowerCase().replace(/\s+/g, '-')}.html`;
  writeFileSync(filePath, html);
  console.log(`Saved to ${filePath} (${html.length} bytes)`);
  return { screenId: screen.screenId, htmlUrl, imgUrl };
}

// Generate remaining pages
const pages = [
  {
    name: 'SyncPanel',
    prompt: `MuSync SyncPanel page - FULL PAGE desktop design. True black background #000, white text, 0px corners. Left sidebar with navigation: MuSync logo, Dashboard, Sync (active with 2px white left border), Scheduler, Settings, Help. Main content area. HEADER: 'Sync Music' title with 'Start New Sync' button (white bg, black text, 0px radius). SYNC CONFIG: From dropdown 'Spotify' to 'YouTube Music' with thin 1px #222 bottom border. Sync type pills: 'Full Library', 'Selected Playlists', 'Incremental' with 1px border, active has white bg black text. PLAYLIST SELECTOR: searchable list, each row has 1px #222 bottom border, checkbox as white border square. SYNC OPTIONS toggles: 'Include liked songs', 'Match by metadata', 'Auto-resolve conflicts' toggles (rectangle slider, 1px border). PROGRESS: linear progress bar with white fill, 1px #222 outline, monospace status text 'Syncing 24/142 tracks'. No shadows, minimalist.`
  },
  {
    name: 'Scheduler',
    prompt: `MuSync Scheduler page - FULL PAGE desktop design. True black background #000, white text, 0px corners. Left sidebar nav: MuSync logo, Dashboard, Sync, Scheduler (active with 2px white left border), Settings, Help. Main content. HEADER: 'Scheduled Syncs' title with 'Create Schedule' button (white bg black text, 0px radius). SCHEDULE CARDS: each has 1px #222 border, 2px white left border accent for active card. Card content: schedule name, frequency badge 'Daily' in monospace with 1px border, last run time, next run time. Status dot: green for Active, gray for Paused. Toggle switch on right. Three-dot menu. CREATE MODAL: dark overlay, centered modal with 1px #222 border. Form: Schedule Name input, Frequency dropdown, Time selector, Day pills M T W T F S S, Source/Destination selects. Save (white bg) and Cancel buttons. All inputs have 1px #222 bottom border only. Minimalist.`
  },
  {
    name: 'Sidebar',
    prompt: `MuSync Sidebar navigation component - standalone design. True black background #000, white text, 0px corners. Full height vertical navigation bar, 240px wide, with 1px #222 right border divider. TOP: MuSync logo with 'Mu' in regular weight and 'Sync' in bold weight, vertically. User avatar area below logo: white circle outline with initials 'JD', username 'john.doe' in small text below. NAV ITEMS: Dashboard with grid icon (active state: 2px solid white left border, white text), Sync with sync icon, Scheduler with clock icon, Settings with gear icon, Help with question icon. Each item: icon on left, label on right, 1px #222 bottom border separator. Bottom section: collapse arrow, theme toggle. Inactive items have #666 text color. Minimalist no shadows.`
  }
];

for (const page of pages) {
  try {
    await generatePage(page.name, page.prompt);
  } catch (err) {
    console.error(`Failed to generate ${page.name}:`, err.message);
  }
}
