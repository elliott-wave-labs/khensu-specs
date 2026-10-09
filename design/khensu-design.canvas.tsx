import {
  BarChart,
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  LineChart,
  Link,
  PieChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  canvasPaletteDark,
  categoryPaletteDark,
  computeDAGLayout,
  useCanvasAction,
  useCanvasState,
  useHostTheme,
  type CSSProperties,
} from "cursor/canvas";

type UINode = Parameters<typeof Stack>[0]["children"];

const PLAN = "/Users/elliott/Documents/GitHub/khensu/khensu-specs/PLAN.md";
const CAPS = "/Users/elliott/Documents/GitHub/khensu/khensu-specs/APP-ID-CAPABILITIES.md";

// Brand surface for the phone mocks: monochrome on the dark palette.
// Starlight for accents, silver for your bubbles, ash for quiet fills.
const D = canvasPaletteDark;
const STAR = D.foreground;
const SILVER = D.foregroundSecondary;
const ASH = D.foregroundTertiary;

const TABS = ["Screens", "Architecture", "Economics", "Network", "Comparisons", "Roadmap", "Links"] as const;
type Tab = (typeof TABS)[number];

// ---------- small brand glyphs ----------

// khensu.nu mark: a ring with the crescent's inner edge drawn as an unfilled line of the same weight.
// The inner edge is an arc of a larger circle offset right, so its ends meet the ring in points.
function Crescent({ size = 18, color = STAR }: { size?: number; bg?: string; color?: string }) {
  const c = 50;
  const ring = 5;
  const a = 50 - ring / 2;
  const d = 62;
  const tipX = 0;
  const r = Math.sqrt(a * a + d * d - 2 * d * tipX);
  const ix = c + tipX;
  const iy = Math.sqrt(a * a - tipX * tipX);
  const innerEdge = `M ${ix} ${c - iy} A ${r} ${r} 0 0 0 ${ix} ${c + iy}`;
  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      <circle cx={c} cy={c} r={a} fill="none" stroke={color} strokeWidth={ring} />
      <path d={innerEdge} fill="none" stroke={color} strokeWidth={ring} strokeLinecap="round" />
    </svg>
  );
}

function AppIcon({ size = 64 }: { size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: size * 0.225,
        background: D.editor,
        border: `1px solid ${D.strokeSecondary}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Crescent size={size * 0.62} />
    </div>
  );
}

// ---------- connected-dots sphere (after moqom.cloud's IndrasNet) ----------

type P3 = { x: number; y: number; z: number };

function sphereNodes(count: number, rotY: number, tilt: number): P3[] {
  const pts: P3[] = [];
  const shell = Math.round(count * 0.75);
  for (let i = 0; i < shell; i++) {
    const y = 1 - (i / (shell - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const t = i * Math.PI * (3 - Math.sqrt(5));
    pts.push({ x: Math.cos(t) * r, y, z: Math.sin(t) * r });
  }
  for (let i = 0; pts.length < count; i++) {
    const h = (k: number) => Math.sin(i * 12.9898 + k * 78.233) * 43758.5453 % 1;
    const v = { x: h(1), y: h(2), z: h(3) };
    const len = Math.hypot(v.x, v.y, v.z) || 1;
    const s = (0.25 + Math.abs(h(4)) * 0.5) / len;
    pts.push({ x: v.x * s, y: v.y * s, z: v.z * s });
  }
  const cy = Math.cos(rotY), sy = Math.sin(rotY), ct = Math.cos(tilt), st = Math.sin(tilt);
  return pts.map(({ x, y, z }) => {
    const x1 = x * cy + z * sy;
    const z1 = -x * sy + z * cy;
    return { x: x1, y: y * ct - z1 * st, z: y * st + z1 * ct };
  });
}

function sphereEdges(pts: P3[], neighbours = 3): Array<[number, number]> {
  const seen = new Set<string>();
  const edges: Array<[number, number]> = [];
  pts.forEach((p, i) => {
    pts
      .map((q, j) => [j, (p.x - q.x) ** 2 + (p.y - q.y) ** 2 + (p.z - q.z) ** 2] as const)
      .filter(([j]) => j !== i)
      .sort((a, b) => a[1] - b[1])
      .slice(0, neighbours)
      .forEach(([j]) => {
        const key = i < j ? `${i}-${j}` : `${j}-${i}`;
        if (!seen.has(key)) {
          seen.add(key);
          edges.push([i, j]);
        }
      });
  });
  return edges;
}

function DotNet({
  width,
  height,
  radius,
  count = 72,
  rotY = 0.6,
  tilt = 0.3,
  opacity = 1,
  lit = [],
  children,
}: {
  width: number;
  height: number;
  radius: number;
  count?: number;
  rotY?: number;
  tilt?: number;
  opacity?: number;
  lit?: number[];
  children?: (at: (i: number) => { x: number; y: number; z: number }) => UINode;
}) {
  const pts = sphereNodes(count, rotY, tilt);
  const edges = sphereEdges(pts);
  const cx = width / 2;
  const cy = height / 2;
  const at = (i: number) => ({ x: cx + pts[i].x * radius, y: cy + pts[i].y * radius, z: pts[i].z });
  const depth = (z: number) => 0.25 + ((z + 1) / 2) * 0.75;
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ opacity, display: "block" }}>
      <defs>
        <radialGradient id="khensu-glow">
          <stop offset="0" stopColor={STAR} stopOpacity={0.55} />
          <stop offset="1" stopColor={STAR} stopOpacity={0} />
        </radialGradient>
      </defs>
      {edges.map(([a, b]) => {
        const pa = at(a);
        const pb = at(b);
        return <line key={`${a}-${b}`} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} stroke={STAR} strokeOpacity={0.14 * depth((pa.z + pb.z) / 2)} strokeWidth={0.7} />;
      })}
      {pts.map((_, i) => {
        const p = at(i);
        const on = lit.includes(i);
        return (
          <g key={i}>
            {on && <circle cx={p.x} cy={p.y} r={7} fill="url(#khensu-glow)" />}
            <circle cx={p.x} cy={p.y} r={on ? 1.8 : 0.6 + depth(p.z) * 0.9} fill={STAR} fillOpacity={on ? 1 : depth(p.z) * 0.7} />
          </g>
        );
      })}
      {children?.(at)}
    </svg>
  );
}

// Moon phase for disappearing timers: fraction 1 = full, 0 = new.
function MoonPhase({ fraction, size = 12, bg = D.fillSecondary }: { fraction: number; size?: number; bg?: string }) {
  const r = size / 2;
  const offset = (1 - fraction) * size;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={r} cy={r} r={r} fill={STAR} />
      <circle cx={r - offset} cy={r} r={r} fill={bg} />
      <circle cx={r} cy={r} r={r - 0.5} fill="none" stroke={STAR} strokeWidth={1} />
    </svg>
  );
}

function GoldCheck({ size = 12 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12">
      <circle cx={6} cy={6} r={6} fill={STAR} />
      <path d="M3.3 6.2 L5.2 8 L8.8 4.2" stroke={D.editor} strokeWidth={1.6} fill="none" strokeLinecap="round" />
    </svg>
  );
}

function Avatar({ letter, tint, size = 34 }: { letter: string; tint: string; size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: size / 2,
        background: D.fillSecondary,
        border: `1px solid ${tint}`,
        color: tint,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: size * 0.42,
        fontWeight: 600,
        flexShrink: 0,
      }}
    >
      {letter}
    </div>
  );
}

// ---------- phone frame ----------

const ph = {
  text: { color: D.foreground, fontSize: 12, lineHeight: "16px" } as CSSProperties,
  sub: { color: D.foregroundSecondary, fontSize: 11, lineHeight: "14px" } as CSSProperties,
  faint: { color: D.foregroundTertiary, fontSize: 10, lineHeight: "13px" } as CSSProperties,
  title: { color: D.foreground, fontSize: 22, lineHeight: "26px", fontWeight: 700 } as CSSProperties,
  glass: { background: D.fillSecondary, border: `1px solid ${D.strokeSecondary}` } as CSSProperties,
};

function Phone({ caption, children, tabBar = true, active = "Chats", wallpaper = false }: { caption: string; children: UINode; tabBar?: boolean; active?: string; wallpaper?: boolean }) {
  const theme = useHostTheme();
  return (
    <Stack gap={8} style={{ alignItems: "center" }}>
      <div
        style={{
          width: 248,
          height: 520,
          borderRadius: 38,
          border: `6px solid ${theme.stroke.primary}`,
          background: D.editor,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {wallpaper && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
            <DotNet width={236} height={360} radius={150} count={110} rotY={1.1} tilt={0.5} opacity={0.8} lit={[7, 31, 58, 90]} />
          </div>
        )}
        <div style={{ position: "relative", display: "flex", justifyContent: "space-between", padding: "10px 20px 4px", ...ph.text, fontWeight: 600 }}>
          <span>9:41</span>
          <div style={{ width: 70, height: 20, borderRadius: 10, background: D.chrome, marginTop: -2 }} />
          <span style={ph.sub}>100%</span>
        </div>
        <div style={{ position: "relative", flex: 1, display: "flex", flexDirection: "column", padding: tabBar ? "4px 12px 64px" : "4px 12px", gap: 8, overflow: "hidden" }}>{children}</div>
        {tabBar && <TabBar active={active} />}
      </div>
      <Text size="small" tone="secondary" style={{ textAlign: "center", maxWidth: 248 }}>
        {caption}
      </Text>
    </Stack>
  );
}

// ---------- native-style glyphs (SF Symbols stand-ins) ----------

type GlyphName =
  | "chat" | "phone" | "gear" | "search" | "compose" | "back" | "video" | "more" | "plus" | "mic"
  | "reply" | "copy" | "forward" | "pin" | "edit" | "trash" | "info" | "mute" | "archive" | "read" | "lock" | "heart";

const GLYPHS: Record<GlyphName, string> = {
  chat: "M4 5h16v10H9l-5 4z",
  phone: "M6 3l3 4-2 2a12 12 0 0 0 8 8l2-2 4 3-2 3C10 21 3 14 3 5z",
  gear: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2",
  search: "M10 4a6 6 0 1 0 0 12 6 6 0 0 0 0-12zM15 15l5 5",
  compose: "M4 20h4L19 9l-4-4L4 16zM14 6l4 4",
  back: "M15 4l-8 8 8 8",
  video: "M3 7h12v10H3zM15 10l6-3v10l-6-3",
  more: "M5 12h.01M12 12h.01M19 12h.01",
  plus: "M12 5v14M5 12h14",
  mic: "M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM6 11a6 6 0 0 0 12 0M12 17v4",
  reply: "M10 6L4 12l6 6M4 12h10a6 6 0 0 1 6 6",
  copy: "M8 8h12v12H8zM4 4h12v4M4 4v12h4",
  forward: "M14 6l6 6-6 6M20 12H10a6 6 0 0 0-6 6",
  pin: "M9 3h6l-1 6 4 4H6l4-4zM12 13v8",
  edit: "M4 20h4L19 9l-4-4L4 16z",
  trash: "M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13",
  info: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 11v6M12 7h.01",
  mute: "M4 9h4l5-4v14l-5-4H4zM17 9l4 6M21 9l-4 6",
  archive: "M3 4h18v4H3zM5 8v12h14V8M10 12h4",
  read: "M3 12l5 5L21 4",
  lock: "M6 11h12v9H6zM8 11V8a4 4 0 0 1 8 0v3",
  heart: "M12 20s-7-4.5-7-10a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5.5-7 10-7 10z",
};

function Glyph({ name, size = 14, color = D.foreground }: { name: GlyphName; size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={name === "more" ? 3.5 : 1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d={GLYPHS[name]} />
    </svg>
  );
}

function GlassCircle({ icon, size = 30, color = D.foreground }: { icon: GlyphName; size?: number; color?: string }) {
  return (
    <div style={{ width: size, height: size, borderRadius: size / 2, ...ph.glass, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      <Glyph name={icon} size={size * 0.48} color={color} />
    </div>
  );
}

function GlassCapsule({ children, style }: { children: UINode; style?: CSSProperties }) {
  return <div style={{ height: 30, borderRadius: 15, padding: "0 12px", ...ph.glass, display: "flex", alignItems: "center", gap: 10, ...style }}>{children}</div>;
}

// Large-title navigation bar with Liquid Glass toolbar buttons.
function NavBar({ title, leading, trailing }: { title?: string; leading?: UINode; trailing?: UINode }) {
  return (
    <Stack gap={4}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", minHeight: 30 }}>
        <div>{leading}</div>
        <div style={{ display: "flex", gap: 6 }}>{trailing}</div>
      </div>
      {title && <span style={ph.title}>{title}</span>}
    </Stack>
  );
}

// iOS 26 floating tab bar: a glass capsule of tabs plus a separate search button.
function TabBar({ active }: { active: string }) {
  const tabs: Array<[string, GlyphName]> = [
    ["Chats", "chat"],
    ["Calls", "phone"],
    ["Settings", "gear"],
  ];
  const wrap: CSSProperties = { position: "absolute", left: 12, right: 12, bottom: 12, display: "flex", gap: 8, alignItems: "center" };
  if (active === "Search") {
    return (
      <div style={wrap}>
        <GlassCircle icon="chat" size={44} color={D.foregroundSecondary} />
        <div style={{ flex: 1, height: 44, borderRadius: 22, ...ph.glass, display: "flex", alignItems: "center", gap: 8, padding: "0 14px" }}>
          <Glyph name="search" size={14} color={D.foregroundSecondary} />
          <span style={ph.sub}>Ask khensu</span>
          <div style={{ flex: 1 }} />
          <Glyph name="mic" size={14} color={D.foregroundSecondary} />
        </div>
      </div>
    );
  }
  return (
    <div style={wrap}>
      <div style={{ flex: 1, height: 52, borderRadius: 26, ...ph.glass, display: "flex", alignItems: "center", justifyContent: "space-around", padding: "0 4px" }}>
        {tabs.map(([name, icon]) => {
          const on = name === active;
          return (
            <div
              key={name}
              style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, padding: "5px 14px", borderRadius: 20, background: on ? D.fillPrimary : "transparent" }}
            >
              <Glyph name={icon} size={16} color={on ? STAR : D.foreground} />
              <span style={{ fontSize: 9, color: on ? STAR : D.foreground }}>{name}</span>
            </div>
          );
        })}
      </div>
      <GlassCircle icon="search" size={52} />
    </div>
  );
}

function FolderTabs() {
  const tabs = ["All", "Personal", "Groups", "Channels", "Unread"];
  return (
    <div style={{ display: "flex", gap: 6, overflow: "hidden" }}>
      {tabs.map((t, i) => (
        <span
          key={t}
          style={{
            fontSize: 10,
            padding: "3px 8px",
            borderRadius: 10,
            whiteSpace: "nowrap",
            color: i === 0 ? D.editor : D.foregroundSecondary,
            background: i === 0 ? STAR : D.fillTertiary,
          }}
        >
          {t}
        </span>
      ))}
    </div>
  );
}

function ChatRow({ name, msg, time, unread, verified, tint, timer }: { name: string; msg: string; time: string; unread?: number; verified?: boolean; tint: string; timer?: number }) {
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "5px 0", borderBottom: `1px solid ${D.strokeTertiary}` }}>
      <Avatar letter={name[0]} tint={tint} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ ...ph.text, fontWeight: 600 }}>{name}</span>
          {verified && <GoldCheck size={10} />}
          {timer !== undefined && <MoonPhase fraction={timer} size={10} bg={D.editor} />}
        </div>
        <div style={{ ...ph.sub, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{msg}</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 3 }}>
        <span style={ph.faint}>{time}</span>
        {unread ? (
          <span style={{ fontSize: 9, minWidth: 16, textAlign: "center", padding: "1px 5px", borderRadius: 8, background: STAR, color: D.editor, fontWeight: 700 }}>{unread}</span>
        ) : null}
      </div>
    </div>
  );
}

function ChatsScreen() {
  return (
    <Phone caption="Chat list: large title, glass toolbar buttons, floating tab bar with separate search, folder tabs" active="Chats">
      <NavBar
        title="Chats"
        leading={<GlassCapsule><span style={ph.text}>Edit</span></GlassCapsule>}
        trailing={<><GlassCircle icon="more" /><GlassCircle icon="compose" /></>}
      />
      <FolderTabs />
      <div style={{ borderRadius: 10, padding: "6px 8px", background: D.fillTertiary, border: `1px solid ${D.strokeSecondary}` }}>
        <span style={{ ...ph.faint, color: STAR }}>Early network</span>
        <span style={ph.faint}> · 12 operators, 4 countries. Anonymity grows as more join.</span>
      </div>
      <ChatRow name="Ana" msg="Lisbon moved to 12–19 May" time="9:38" unread={3} verified tint={SILVER} />
      <ChatRow name="Design crew" msg="Mara: new icon set is up" time="9:12" unread={12} tint={ASH} />
      <ChatRow name="Dad" msg="Voice note · 0:42" time="8:50" verified tint={SILVER} timer={0.6} />
      <ChatRow name="tatenan operators" msg="Epoch 41,203 header signed" time="Thu" tint={ASH} />
    </Phone>
  );
}

function SwipeAction({ label, icon, bg, fg = D.foreground }: { label: string; icon: GlyphName; bg: string; fg?: string }) {
  return (
    <div style={{ width: 52, background: bg, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 2 }}>
      <Glyph name={icon} size={14} color={fg} />
      <span style={{ fontSize: 9, color: fg }}>{label}</span>
    </div>
  );
}

function SwipeScreen() {
  return (
    <Phone caption="Swipe actions: leading Pin and Read, trailing Mute and Archive, full swipe archives" active="Chats">
      <NavBar
        title="Chats"
        leading={<GlassCapsule><span style={ph.text}>Edit</span></GlassCapsule>}
        trailing={<><GlassCircle icon="more" /><GlassCircle icon="compose" /></>}
      />
      <FolderTabs />
      <ChatRow name="Ana" msg="Lisbon moved to 12–19 May" time="9:38" unread={3} verified tint={SILVER} />
      <div style={{ display: "flex", margin: "0 -12px", height: 46 }}>
        <SwipeAction label="Pin" icon="pin" bg={STAR} fg={D.editor} />
        <SwipeAction label="Read" icon="read" bg={SILVER} fg={D.editor} />
        <div style={{ flex: 1, padding: "0 12px", background: D.editor }}>
          <ChatRow name="Design crew" msg="Mara: new icon set is up" time="9:12" unread={12} tint={ASH} />
        </div>
      </div>
      <div style={{ display: "flex", margin: "0 -12px", height: 46 }}>
        <div style={{ flex: 1, padding: "0 12px", background: D.editor }}>
          <ChatRow name="Dad" msg="Voice note · 0:42" time="8:50" verified tint={SILVER} timer={0.6} />
        </div>
        <SwipeAction label="Mute" icon="mute" bg={D.fillPrimary} />
        <SwipeAction label="Archive" icon="archive" bg={ASH} fg={D.editor} />
      </div>
      <ChatRow name="tatenan operators" msg="Epoch 41,203 header signed" time="Thu" tint={ASH} />
      <ChatRow name="Leo" msg="Sent you 25 · shielded" time="Wed" verified tint={ASH} />
    </Phone>
  );
}

function MenuItem({ label, icon, danger, trailing }: { label: string; icon: GlyphName; danger?: boolean; trailing?: UINode }) {
  const color = danger ? categoryPaletteDark.red : D.foreground;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "7px 12px", borderBottom: `1px solid ${D.strokeTertiary}` }}>
      <span style={{ ...ph.text, color, flex: 1 }}>{label}</span>
      {trailing}
      <Glyph name={icon} size={14} color={color} />
    </div>
  );
}

function NativeMenu({ children, width = 190, style }: { children: UINode; width?: number; style?: CSSProperties }) {
  return (
    <div style={{ width, borderRadius: 14, overflow: "hidden", background: D.chrome, border: `1px solid ${D.strokeSecondary}`, ...style }}>{children}</div>
  );
}

function LongPressScreen() {
  const reactions = ["♥", "+1", "!", "?", "✓"];
  return (
    <Phone caption="Long press: native context menu with reactions; the rest of the chat blurs behind" tabBar={false}>
      <div style={{ position: "absolute", inset: 0, background: D.chrome, opacity: 0.92 }} />
      <div style={{ position: "relative", display: "flex", flexDirection: "column", gap: 8, marginTop: 70 }}>
        <div style={{ alignSelf: "flex-end", display: "flex", gap: 4, padding: "5px 8px", borderRadius: 18, ...ph.glass }}>
          {reactions.map((r) => (
            <div key={r} style={{ width: 24, height: 24, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, color: r === "♥" ? STAR : D.foreground, background: r === "♥" ? D.fillPrimary : "transparent" }}>
              {r}
            </div>
          ))}
          <div style={{ width: 24, height: 24, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", background: D.fillTertiary }}>
            <Glyph name="plus" size={11} />
          </div>
        </div>
        <Bubble me meta="9:31">Yes, 12–19 May works</Bubble>
        <NativeMenu style={{ alignSelf: "flex-end" }}>
          <MenuItem label="Reply" icon="reply" />
          <MenuItem label="Copy" icon="copy" />
          <MenuItem label="Forward" icon="forward" />
          <MenuItem label="Pin" icon="pin" />
          <MenuItem label="Edit" icon="edit" />
          <MenuItem label="Info" icon="info" />
          <MenuItem label="Delete" icon="trash" danger />
        </NativeMenu>
      </div>
    </Phone>
  );
}

function ChatHeader() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <GlassCircle icon="back" />
      <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
        <GlassCapsule style={{ gap: 6, padding: "0 10px 0 4px" }}>
          <Avatar letter="A" tint={SILVER} size={22} />
          <span style={{ ...ph.text, fontWeight: 600 }}>Ana</span>
          <GoldCheck size={10} />
        </GlassCapsule>
      </div>
      <GlassCapsule style={{ padding: "0 10px" }}>
        <Glyph name="phone" size={13} />
        <Glyph name="video" size={13} />
      </GlassCapsule>
    </div>
  );
}

function MenuScreen() {
  return (
    <Phone caption="Pull-down menu from the chat title: timers, search, mute, safety number, wallet" tabBar={false}>
      <ChatHeader />
      <div style={{ display: "flex", justifyContent: "center", marginTop: 4 }}>
        <NativeMenu width={210}>
          <MenuItem label="Search in chat" icon="search" />
          <MenuItem label="Mute" icon="mute" />
          <MenuItem label="Disappearing messages" icon="info" trailing={<MoonPhase fraction={0.5} size={11} bg={D.chrome} />} />
          <MenuItem label="Send money" icon="forward" />
          <MenuItem label="Encryption and safety number" icon="lock" />
          <MenuItem label="Wallpaper" icon="edit" />
          <MenuItem label="Block" icon="trash" danger />
        </NativeMenu>
      </div>
      <div style={{ flex: 1 }} />
      <div style={{ opacity: 0.35, display: "flex", flexDirection: "column", gap: 8 }}>
        <Bubble>Can we push Lisbon a week?</Bubble>
        <Bubble me>Yes, 12–19 May works</Bubble>
      </div>
    </Phone>
  );
}

function Bubble({ me, children, meta }: { me?: boolean; children: UINode; meta?: UINode }) {
  return (
    <div style={{ display: "flex", justifyContent: me ? "flex-end" : "flex-start" }}>
      <div
        style={{
          maxWidth: "78%",
          padding: "6px 9px",
          borderRadius: 14,
          background: me ? SILVER : D.fillSecondary,
          color: me ? D.editor : D.foreground,
          fontSize: 12,
          lineHeight: "16px",
        }}
      >
        {children}
        {meta && <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 4, marginTop: 2, fontSize: 9, opacity: 0.8 }}>{meta}</div>}
      </div>
    </div>
  );
}

function ChatScreen() {
  return (
    <Phone caption="Chat: glass back button, title capsule opens the chat menu, floating glass composer" tabBar={false}>
      <ChatHeader />
      <Bubble>Can we push Lisbon a week?</Bubble>
      <Bubble me meta="9:31">Yes, 12–19 May works</Bubble>
      <Bubble meta={<><MoonPhase fraction={0.3} size={9} bg={D.fillSecondary} /> 2h left</>}>Gate code is 4471, delete after</Bubble>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <div style={{ borderRadius: 14, padding: "8px 10px", border: `1px solid ${STAR}`, background: D.fillTertiary, width: "70%" }}>
          <div style={{ ...ph.faint, color: STAR }}>Shielded payment</div>
          <div style={{ ...ph.text, fontSize: 18, lineHeight: "22px", fontWeight: 700 }}>25</div>
          <div style={ph.faint}>Hidden amount · no lasting record</div>
        </div>
      </div>
      <Bubble meta="9:38">Booked the flat</Bubble>
      <div style={{ ...ph.faint, paddingLeft: 4 }}>Ana is typing…</div>
      <div style={{ flex: 1 }} />
      <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 12 }}>
        <GlassCircle icon="plus" size={34} />
        <div style={{ flex: 1, height: 34, borderRadius: 17, padding: "0 12px", ...ph.glass, display: "flex", alignItems: "center" }}>
          <span style={{ ...ph.sub, flex: 1 }}>Message</span>
          <Glyph name="mic" size={14} color={D.foregroundSecondary} />
        </div>
      </div>
    </Phone>
  );
}

function SearchScreen() {
  const results = [
    { k: "Graph", t: "Ana: Lisbon moved to 12–19 May", d: "Today" },
    { k: "Keyword", t: "Flat booked near Cais do Sodré", d: "Today" },
    { k: "Time", t: "Flights on hold until Friday", d: "Mon" },
    { k: "Meaning", t: "Leo: seafood places, skip the trams", d: "Sep 28" },
  ];
  return (
    <Phone caption="Ask khensu: Hindsight-style recall and reflect, entirely on the device, with citations" active="Search">
      <NavBar title="Ask khensu" trailing={<GlassCircle icon="more" />} />
      <div style={{ ...ph.glass, borderRadius: 10, padding: "6px 10px", ...ph.text }}>When is the Lisbon trip?</div>
      <div style={{ borderRadius: 12, padding: 10, background: D.fillTertiary, border: `1px solid ${D.strokeSecondary}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
          <Crescent size={12} bg={D.fillTertiary} />
          <span style={{ ...ph.faint, color: STAR }}>Answer · on-device model</span>
        </div>
        <div style={ph.text}>
          12–19 May. Ana moved it a week on Thursday [1], and you booked a flat near Cais do Sodré [2].
        </div>
        <div style={{ display: "flex", gap: 4, marginTop: 6 }}>
          {["[1] Ana", "[2] You"].map((c) => (
            <span key={c} style={{ fontSize: 9, padding: "1px 6px", borderRadius: 8, background: D.fillSecondary, color: D.foregroundSecondary }}>
              {c}
            </span>
          ))}
        </div>
      </div>
      <div style={ph.faint}>Recall · keyword, meaning, graph and time, fused by rank</div>
      {results.map((r) => (
        <div key={r.t} style={{ display: "flex", gap: 6, alignItems: "center", padding: "4px 0", borderBottom: `1px solid ${D.strokeTertiary}` }}>
          <span style={{ fontSize: 9, width: 46, textAlign: "center", padding: "1px 0", borderRadius: 6, background: D.fillSecondary, color: STAR }}>{r.k}</span>
          <span style={{ ...ph.sub, flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{r.t}</span>
          <span style={ph.faint}>{r.d}</span>
        </div>
      ))}
    </Phone>
  );
}

function WalletScreen() {
  const notes = [10, 10, 5, 2, 2, 1];
  return (
    <Phone caption="Wallet: shielded notes in fixed sizes, era refresh, Face ID for every spend" active="Settings">
      <NavBar title="Wallet" leading={<GlassCircle icon="back" />} trailing={<GlassCircle icon="more" />} />
      <div style={{ borderRadius: 14, padding: 12, background: D.fillTertiary, border: `1px solid ${D.strokeSecondary}` }}>
        <div style={ph.faint}>Shielded balance</div>
        <div style={{ ...ph.text, fontSize: 22, lineHeight: "26px", fontWeight: 700, color: STAR }}>30</div>
        <div style={ph.faint}>Era Oct 2026 · auto-refresh in 12 days</div>
        <div style={{ display: "flex", gap: 4, marginTop: 8, flexWrap: "wrap" }}>
          {notes.map((n, i) => (
            <span key={i} style={{ fontSize: 10, padding: "2px 7px", borderRadius: 8, border: `1px solid ${STAR}`, color: STAR }}>
              {n}
            </span>
          ))}
        </div>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {["Send", "Receive", "Deposit"].map((b, i) => (
          <div key={b} style={{ flex: 1, textAlign: "center", padding: "6px 0", borderRadius: 10, fontSize: 11, fontWeight: 600, background: i === 0 ? STAR : D.fillSecondary, color: i === 0 ? D.editor : D.foreground }}>
            {b}
          </div>
        ))}
      </div>
      <div style={ph.faint}>History · stored only on this device</div>
      {[
        ["To Ana", "-25", "Today"],
        ["From Leo", "+25", "Wed"],
        ["Deposit from public account", "+30", "Oct 1"],
      ].map(([a, b, c]) => (
        <div key={a} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: `1px solid ${D.strokeTertiary}` }}>
          <span style={ph.sub}>{a}</span>
          <span style={{ ...ph.text, color: b.startsWith("+") ? SILVER : D.foreground }}>{b}</span>
          <span style={ph.faint}>{c}</span>
        </div>
      ))}
      <div style={{ ...ph.faint, marginTop: 4 }}>STARK proof · ML-KEM-1024 notes · sent through the mixnet</div>
    </Phone>
  );
}

function CallScreen() {
  const W = 224;
  const H = 240;
  const count = 72;
  const pts = sphereNodes(count, 0.6, 0.3);
  const front = pts.map((p, i) => [i, p] as const).filter(([, p]) => p.z > 0.15);
  const pick = (ax: number, ay: number) =>
    front.reduce((best, cur) => ((cur[1].x - ax) ** 2 + (cur[1].y - ay) ** 2 < (best[1].x - ax) ** 2 + (best[1].y - ay) ** 2 ? cur : best))[0];
  const people = [
    { l: "Ana", i: pick(-0.75, -0.45), speaking: true },
    { l: "Mara", i: pick(0.7, -0.5), speaking: false },
    { l: "Leo", i: pick(0.75, 0.45), speaking: false },
    { l: "Dad", i: pick(-0.65, 0.55), speaking: false },
  ];
  const lit = people.map((p) => p.i);
  return (
    <Phone caption="Group call: each voice is a node in space around you; AirPods head pose keeps them fixed as you turn" tabBar={false}>
      <div style={{ textAlign: "center", marginTop: 8 }}>
        <div style={{ ...ph.text, fontWeight: 600 }}>Design crew</div>
        <div style={ph.faint}>4 people · 12:04 · two relays, different operators</div>
      </div>
      <div style={{ margin: "4px -12px 0", display: "flex", justifyContent: "center" }}>
        <DotNet width={W} height={H} radius={92} count={count} lit={lit}>
          {(at) => (
            <>
              {people.map((p) => {
                const q = at(p.i);
                const mx = W / 2 + (q.x - W / 2) * 0.55;
                const my = H / 2 + (q.y - H / 2) * 0.55;
                return (
                  <g key={p.l}>
                    <line x1={W / 2} y1={H / 2} x2={q.x} y2={q.y} stroke={STAR} strokeOpacity={p.speaking ? 0.7 : 0.25} strokeWidth={p.speaking ? 1.1 : 0.7} strokeDasharray={p.speaking ? undefined : "2 3"} />
                    {p.speaking && <circle cx={mx} cy={my} r={2.2} fill={STAR} />}
                    {p.speaking && <circle cx={q.x} cy={q.y} r={11} fill="none" stroke={STAR} strokeOpacity={0.35} strokeWidth={0.8} />}
                    <text x={q.x} y={q.y + (q.y > H / 2 ? 18 : -10)} textAnchor="middle" fontSize={9} fill={p.speaking ? STAR : SILVER}>
                      {p.l}
                    </text>
                  </g>
                );
              })}
              <circle cx={W / 2} cy={H / 2} r={14} fill="url(#khensu-glow)" />
              <circle cx={W / 2} cy={H / 2} r={3.2} fill={STAR} />
              <text x={W / 2} y={H / 2 + 17} textAnchor="middle" fontSize={9} fill={STAR}>
                You
              </text>
            </>
          )}
        </DotNet>
      </div>
      <div style={{ ...ph.faint, textAlign: "center" }}>Personalized Spatial Audio · head tracking on</div>
      <div style={{ flex: 1 }} />
      <div style={{ display: "flex", justifyContent: "space-around", marginBottom: 16 }}>
        {(
          [
            ["Mute", "mic"],
            ["Speaker", "mute"],
            ["Video", "video"],
            ["End", "phone"],
          ] as Array<[string, GlyphName]>
        ).map(([b, icon]) => (
          <div key={b} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
            {b === "End" ? (
              <div style={{ width: 40, height: 40, borderRadius: 20, background: categoryPaletteDark.red, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Glyph name="phone" size={18} color={D.editor} />
              </div>
            ) : (
              <GlassCircle icon={icon} size={40} />
            )}
            <span style={ph.faint}>{b}</span>
          </div>
        ))}
      </div>
    </Phone>
  );
}

function LockScreen() {
  return (
    <Phone caption="Lock screen in Anonymous mode, on the connected-dots wallpaper: no sender, no preview" tabBar={false} wallpaper>
      <div style={{ textAlign: "center", marginTop: 30 }}>
        <div style={ph.sub}>Friday 9 October</div>
        <div style={{ color: D.foreground, fontSize: 22, lineHeight: "26px", fontWeight: 300, letterSpacing: 1 }}>9:41</div>
      </div>
      <div style={{ flex: 1 }} />
      {[0, 1].map((i) => (
        <div key={i} style={{ display: "flex", gap: 8, alignItems: "center", borderRadius: 16, padding: 10, ...ph.glass, opacity: i === 1 ? 0.7 : 1 }}>
          <div style={{ width: 28, height: 28, borderRadius: 7, background: D.chrome, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Crescent size={16} bg={D.chrome} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ ...ph.text, fontWeight: 600 }}>khensu.nu</span>
              <span style={ph.faint}>{i === 0 ? "now" : "8m ago"}</span>
            </div>
            <div style={ph.sub}>New message</div>
          </div>
        </div>
      ))}
      <div style={{ ...ph.faint, textAlign: "center", marginBottom: 24, marginTop: 8 }}>Wake delayed 0–20 s and merged at the gateway</div>
    </Phone>
  );
}

function SettingRow({ label, value, gold }: { label: string; value: string; gold?: boolean }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", padding: "7px 10px", borderBottom: `1px solid ${D.strokeTertiary}` }}>
      <span style={ph.text}>{label}</span>
      <span style={{ ...ph.sub, color: gold ? STAR : D.foregroundSecondary }}>{value} ›</span>
    </div>
  );
}

function PrivacyScreen() {
  return (
    <Phone caption="Privacy settings: notification modes, reciprocal typing and receipts, on-device memory" active="Settings">
      <NavBar title="Privacy" leading={<GlassCircle icon="back" />} />
      <div style={{ borderRadius: 12, overflow: "hidden", background: D.fillTertiary }}>
        <SettingRow label="Notifications" value="Anonymous" gold />
        <SettingRow label="Typing indicators" value="On" />
        <SettingRow label="Read receipts" value="On" />
        <SettingRow label="Online status" value="Off" />
      </div>
      <div style={{ borderRadius: 12, overflow: "hidden", background: D.fillTertiary }}>
        <SettingRow label="App lock" value="Face ID" gold />
        <SettingRow label="Passcode-only mode" value="Off" />
        <SettingRow label="Memory and search" value="On device" />
        <SettingRow label="Offline nearby mode" value="Off" />
      </div>
      <div style={{ ...ph.faint, padding: "0 4px" }}>
        Turning typing indicators off also hides other people&apos;s. Memory never leaves this device and is never backed up.
      </div>
    </Phone>
  );
}

function ProfileScreen() {
  const cells = Array.from({ length: 81 }, (_, i) => ((i * 37 + (i % 7) * 11) % 5 < 2 ? 1 : 0));
  return (
    <Phone caption="Identity: permanent handle, khensu1 address, four-word check phrase, QR and tap to add" active="Settings">
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, marginTop: 6 }}>
        <Avatar letter="E" tint={STAR} size={56} />
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ ...ph.text, fontSize: 16, fontWeight: 700 }}>@elliott</span>
          <GoldCheck size={12} />
        </div>
        <div style={ph.faint}>Permanent handle · elliott.khensu.nu</div>
      </div>
      <div style={{ alignSelf: "center", display: "grid", gridTemplateColumns: "repeat(9, 9px)", gap: 1, padding: 8, borderRadius: 10, background: D.foreground }}>
        {cells.map((c, i) => (
          <div key={i} style={{ width: 9, height: 9, background: c ? D.editor : D.foreground }} />
        ))}
      </div>
      <div style={{ borderRadius: 12, padding: 10, background: D.fillTertiary }}>
        <div style={ph.faint}>Address</div>
        <div style={{ ...ph.text, fontFamily: "ui-monospace, monospace", fontSize: 10 }}>khensu1q8f3x…7w2kpz</div>
        <div style={{ ...ph.faint, marginTop: 6 }}>Check phrase</div>
        <div style={{ ...ph.text, color: STAR }}>lotus · river · falcon · dawn</div>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {["Share link", "Tap to add", "Devices (3)"].map((b) => (
          <div key={b} style={{ flex: 1, textAlign: "center", padding: "6px 0", borderRadius: 10, fontSize: 10, background: D.fillSecondary, color: D.foreground }}>
            {b}
          </div>
        ))}
      </div>
    </Phone>
  );
}

function ScreensTab() {
  return (
    <Stack gap={20}>
      <Stack gap={4}>
        <H2>iPhone screens</H2>
        <Text tone="secondary">
          Stock iOS 26 Liquid Glass chrome: large-title navigation bars with glass toolbar buttons, the floating tab bar with its separate search button, native pull-down and context menus, long press and system swipe actions. The identity is monochrome and spacey: true-black surfaces, silver bubbles, starlight accents, the crescent mark, moon-phase timers, and connected-dot node networks (after moqom.cloud) for calls, the network and wallpapers. Red appears only for destructive actions and ending calls.
        </Text>
      </Stack>
      <Grid columns={4} gap={20} align="start">
        <ChatsScreen />
        <SwipeScreen />
        <ChatScreen />
        <LongPressScreen />
        <MenuScreen />
        <SearchScreen />
        <LockScreen />
        <WalletScreen />
        <CallScreen />
        <PrivacyScreen />
        <ProfileScreen />
      </Grid>
      <IconVariants />
      <BrandStrip />
    </Stack>
  );
}

function IconVariants() {
  const variants: Array<[string, string, string]> = [
    ["Dark", D.chrome, STAR],
    ["Graphite", D.fillPrimary, STAR],
    ["Light", D.foreground, D.editor],
    ["Tinted", D.chrome, SILVER],
  ];
  return (
    <Card>
      <CardHeader>App icon</CardHeader>
      <CardBody>
        <Row gap={28} align="end" wrap>
          <Stack gap={6} style={{ alignItems: "center" }}>
            <AppIcon size={112} />
            <Text size="small" tone="secondary">
              Home screen, 1024 master
            </Text>
          </Stack>
          {variants.map(([name, bg, fg]) => (
            <Stack key={name} gap={6} style={{ alignItems: "center" }}>
              <div style={{ width: 64, height: 64, borderRadius: 14.4, background: bg, border: `1px solid ${D.strokeSecondary}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Crescent size={40} color={fg} />
              </div>
              <Text size="small" tone="secondary">
                {name}
              </Text>
            </Stack>
          ))}
          <Stack gap={6} style={{ alignItems: "center" }}>
            <Row gap={10} align="center">
              <Crescent size={32} />
              <Crescent size={20} />
              <Crescent size={12} />
            </Row>
            <Text size="small" tone="secondary">
              Small sizes
            </Text>
          </Stack>
        </Row>
      </CardBody>
    </Card>
  );
}

function BrandStrip() {
  const theme = useHostTheme();
  const swatches: Array<[string, string, string]> = [
    ["Void", D.editor, "Backgrounds, true black on OLED"],
    ["Glass", D.fillSecondary, "Tab bar, toolbars, menus, sheets"],
    ["Silver", SILVER, "Your bubbles, secondary text"],
    ["Starlight", STAR, "Actions, verified, unread, timers, nodes"],
  ];
  return (
    <Card>
      <CardHeader>Brand tokens</CardHeader>
      <CardBody>
        <Row gap={24} wrap align="center">
          <Row gap={8} align="center">
            <Crescent size={28} />
            <Text weight="semibold">khensu.nu</Text>
          </Row>
          {swatches.map(([n, c, d]) => (
            <Row key={n} gap={8} align="center">
              <div style={{ width: 24, height: 24, borderRadius: 6, background: c, border: `1px solid ${theme.stroke.secondary}` }} />
              <Stack gap={0}>
                <Text size="small" weight="medium">
                  {n}
                </Text>
                <Text size="small" tone="tertiary">
                  {d}
                </Text>
              </Stack>
            </Row>
          ))}
          <Row gap={6} align="center">
            {[1, 0.75, 0.5, 0.25, 0.05].map((f) => (
              <MoonPhase key={f} fraction={f} size={16} bg={theme.bg.editor} />
            ))}
            <Text size="small" tone="tertiary">
              Timer phases
            </Text>
          </Row>
        </Row>
      </CardBody>
    </Card>
  );
}

// ---------- architecture ----------

type Group = "client" | "mixnet" | "chain" | "service" | "apple";
const ARCH_NODES: Array<{ id: string; label: string; group: Group }> = [
  { id: "app", label: "khensu.nu app", group: "client" },
  { id: "memory", label: "KhensuMemory", group: "client" },
  { id: "enclave", label: "Secure Enclave keys", group: "client" },
  { id: "mix1", label: "Mix layer 1", group: "mixnet" },
  { id: "mix2", label: "Mix layer 2", group: "mixnet" },
  { id: "mix3", label: "Mix layer 3", group: "mixnet" },
  { id: "mailbox", label: "Mailbox nodes", group: "mixnet" },
  { id: "seq", label: "Group sequencers", group: "mixnet" },
  { id: "relay", label: "Call relays (2 hops)", group: "mixnet" },
  { id: "committee", label: "Committee (21, BFT)", group: "chain" },
  { id: "pool", label: "Shielded pool", group: "chain" },
  { id: "kt", label: "Key transparency log", group: "service" },
  { id: "issuer", label: "Credential issuer", group: "service" },
  { id: "push", label: "Push gateway", group: "service" },
  { id: "apns", label: "APNs", group: "apple" },
];
const ARCH_EDGES: Array<{ from: string; to: string }> = [
  { from: "app", to: "memory" },
  { from: "app", to: "enclave" },
  { from: "app", to: "mix1" },
  { from: "mix1", to: "mix2" },
  { from: "mix2", to: "mix3" },
  { from: "mix3", to: "mailbox" },
  { from: "mix3", to: "seq" },
  { from: "mix3", to: "committee" },
  { from: "committee", to: "pool" },
  { from: "app", to: "relay" },
  { from: "app", to: "kt" },
  { from: "app", to: "issuer" },
  { from: "mailbox", to: "push" },
  { from: "push", to: "apns" },
];

function ArchitectureDiagram() {
  const theme = useHostTheme();
  const groupColor: Record<Group, string> = {
    client: theme.category.yellow,
    mixnet: theme.category.blue,
    chain: theme.category.purple,
    service: theme.category.green,
    apple: theme.category.gray,
  };
  const layout = computeDAGLayout({ nodes: ARCH_NODES, edges: ARCH_EDGES, direction: "horizontal", nodeWidth: 150, nodeHeight: 36, rankGap: 56, nodeGap: 14 });
  const byId = new Map(ARCH_NODES.map((n) => [n.id, n]));
  return (
    <Stack gap={10}>
      <div style={{ overflowX: "auto" }}>
        <svg width={layout.width} height={layout.height}>
          <defs>
            <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M0 0 L8 4 L0 8 z" fill={theme.text.tertiary} />
            </marker>
          </defs>
          {layout.edges.map((e, i) => {
            const mx = (e.sourceX + e.targetX) / 2;
            return (
              <path
                key={i}
                d={`M${e.sourceX} ${e.sourceY} C${mx} ${e.sourceY} ${mx} ${e.targetY} ${e.targetX} ${e.targetY}`}
                stroke={theme.stroke.primary}
                strokeWidth={1.2}
                fill="none"
                markerEnd="url(#arrow)"
                strokeDasharray={e.isBackEdge ? "4 3" : undefined}
              />
            );
          })}
          {layout.nodes.map((n) => {
            const meta = byId.get(n.id)!;
            return (
              <g key={n.id}>
                <rect x={n.x} y={n.y} width={150} height={36} rx={6} fill={theme.fill.tertiary} stroke={theme.stroke.secondary} />
                <rect x={n.x} y={n.y + 8} width={3} height={20} rx={1.5} fill={groupColor[meta.group]} />
                <text x={n.x + 12} y={n.y + 22} fontSize={12} fill={theme.text.primary}>
                  {meta.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <Row gap={16} wrap>
        {(Object.keys(groupColor) as Group[]).map((g) => (
          <Row key={g} gap={6} align="center">
            <div style={{ width: 10, height: 10, borderRadius: 3, background: groupColor[g] }} />
            <Text size="small" tone="secondary">
              {{ client: "On the device", mixnet: "Operator nodes", chain: "Consensus and token chain", service: "Thin services (ours)", apple: "Apple" }[g]}
            </Text>
          </Row>
        ))}
      </Row>
    </Stack>
  );
}

function ArchitectureTab() {
  return (
    <Stack gap={20}>
      <Stack gap={4}>
        <H2>System architecture</H2>
        <Text tone="secondary">Every message, receipt, typing event and shielded spend crosses three mix layers. Calls are the one exception and use two relays run by different operators.</Text>
      </Stack>
      <ArchitectureDiagram />
      <H3>What each hop can see</H3>
      <Table
        headers={["Component", "Sees", "Never sees"]}
        rows={[
          ["Mix layer 1 (entry)", "Your IP, packet timing", "Recipient, content, which conversation"],
          ["Mix layers 2 and 3", "Previous and next hop only", "Sender IP, recipient, content"],
          ["Mailbox nodes", "A rotating mailbox ID, sealed packets", "Who you are, who sent them"],
          ["Group sequencers", "Encrypted commits for one group epoch", "Members' identities, content"],
          ["Committee", "Nullifiers, proofs, work receipts", "Who paid whom, amounts"],
          ["Push gateway", "A device token and a wake time", "Sender, conversation, your address"],
          ["Call relays", "One end's IP each", "Both ends together, media content"],
        ]}
      />
      <Grid columns={3} gap={16}>
        <Stat value="ML-KEM-1024" label="Key exchange (pure post-quantum)" />
        <Stat value="ML-DSA-87" label="Signatures everywhere, incl. consensus" />
        <Stat value="1,000" label="Max devices per group (TreeKEM)" />
      </Grid>
    </Stack>
  );
}

// ---------- economics ----------

const MINT = [80, 80, 40, 40, 20, 20, 10, 10, 5, 5];
const BURN_SLOW = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20];
const BURN_TARGET = [5, 12, 22, 35, 50, 65, 80, 95, 110, 125];
function supplyPath(burn: number[]) {
  const out = [1000];
  for (let i = 0; i < MINT.length; i++) out.push(out[i] + MINT[i] - burn[i]);
  return out;
}

function EconomicsTab() {
  const years = Array.from({ length: 11 }, (_, i) => `Year ${i}`);
  return (
    <Stack gap={24}>
      <Stack gap={4}>
        <H2>Burn and mint</H2>
        <Text tone="secondary">
          A fixed share of net subscription proceeds is company revenue; the rest buys the token and burns it for capacity. The protocol, not the company, mints operator rewards from measured work. Company margin stays fixed regardless of token price.
        </Text>
      </Stack>
      <Grid columns="minmax(0, 1fr) minmax(0, 1.4fr)" gap={24} align="start">
        <Stack gap={8}>
          <H3>Where $4.99 a month goes</H3>
          <PieChart
            donut
            size={190}
            data={[
              { label: "Apple (15%)", value: 0.75, tone: "neutral" },
              { label: "Company revenue", value: 2.12, tone: "info" },
              { label: "Bought and burned for operators", value: 2.12, tone: "warning" },
            ]}
          />
          <Text size="small" tone="tertiary">
            USD per Plus subscriber per month. Assumes Apple's 15% rate (Small Business Program or after year one) and a 50/50 split. Source: plan, Money section.
          </Text>
        </Stack>
        <Stack gap={8}>
          <H3>Token supply under three burn scenarios (illustrative)</H3>
          <LineChart
            categories={years}
            series={[
              { name: "No burn", data: supplyPath(MINT.map(() => 0)), tone: "neutral" },
              { name: "Slow adoption", data: supplyPath(BURN_SLOW), tone: "info" },
              { name: "Target adoption", data: supplyPath(BURN_TARGET), tone: "success" },
            ]}
            valueSuffix="M"
            beginAtZero={false}
            referenceLines={[{ value: 1000, label: "Genesis 1B" }]}
          />
          <Text size="small" tone="tertiary">
            Circulating supply in millions of tokens. Emission 8% of genesis per year, halving every 2 years. Burn paths are assumptions for discussion with counsel, not forecasts.
          </Text>
        </Stack>
      </Grid>
      <Row gap={32}>
        <Stat value="≈70" label="Free users carried per Plus subscriber" />
        <Stat value="$0.03" label="Est. operator cost per free user / month" />
        <Stat value="2 GB" label="Mixnet traffic per text-heavy user / month" />
      </Row>
      <H3>Pricing tiers (starting proposal)</H3>
      <Table
        headers={["Tier", "Price", "Includes"]}
        rows={[
          ["Free", "$0", "1:1 and groups, calls, 100 MB attachments, 30-day mailbox history, 3 devices"],
          ["Plus", "$4.99 / month", "2 GB attachments, encrypted backups, 10 devices, icons and themes"],
          ["Family", "$9.99 / month", "Plus for 6 people"],
          ["Business", "Per seat", "Admin roles, on-device compliance exports, self-hosted network option"],
        ]}
      />
      <H3>Genesis allocation (proposal for counsel)</H3>
      <Grid columns="minmax(0, 1fr) minmax(0, 1.4fr)" gap={24} align="center">
        <PieChart
          size={170}
          data={[
            { label: "Network treasury (time-locked)", value: 60 },
            { label: "Company (4-year vest)", value: 20 },
            { label: "Ecosystem and grants", value: 15 },
            { label: "Burn auction liquidity", value: 5 },
          ]}
        />
        <Callout tone="warning" title="Utility-token rules">
          No price or return promises, no revenue share or company-funded yield, subscribers never receive tokens, phones never earn, no referral rewards. Counsel signs off before anything is minted.
        </Callout>
      </Grid>
    </Stack>
  );
}

// ---------- network ----------

function NetworkTab() {
  return (
    <Stack gap={24}>
      <Stack gap={4}>
        <H2>Network, battery and data</H2>
        <Text tone="secondary">iOS suspends background apps, so phones send cover traffic only while the app is open. Two fixed packet sizes keep attachments inside the mixnet.</Text>
      </Stack>
      <Grid columns={2} gap={24} align="start">
        <Stack gap={8}>
          <H3>Cover traffic while the app is open</H3>
          <BarChart
            categories={["Wi-Fi", "Cellular", "Low Power Mode"]}
            series={[{ name: "Small-packet cover (MB per hour)", data: [18, 3.6, 0] }]}
            valueSuffix=" MB"
            referenceLines={[{ value: 50 / 4, label: "Daily 50 MB cellular cap ÷ 4 h", tone: "warning" }]}
          />
          <Text size="small" tone="tertiary">
            MB per hour of foreground use. Wi-Fi: 1 packet / 2 s; cellular: 1 / 10 s; Low Power: real traffic only. Rates to be tuned on devices.
          </Text>
        </Stack>
        <Stack gap={8}>
          <H3>Packet size on the wire</H3>
          <BarChart
            categories={["Small packet", "Bulk packet"]}
            series={[
              { name: "ML-KEM-1024 headers, 5 hops (KB)", data: [8, 8], tone: "neutral" },
              { name: "Payload (KB)", data: [2, 64], tone: "info" },
            ]}
            stacked
            valueSuffix=" KB"
          />
          <Text size="small" tone="tertiary">Kilobytes per packet. Small: messages, receipts, typing. Bulk: attachment chunks, Wi-Fi by default.</Text>
        </Stack>
      </Grid>
      <H3>"Private network" threshold before the Early network banner goes away</H3>
      <Table
        headers={["Requirement", "Minimum", "Why"]}
        rows={[
          ["Mix nodes", "30", "Enough nodes per layer that paths don't repeat"],
          ["Independent operators", "10", "No single party sees most paths"],
          ["Countries", "5", "No single jurisdiction can compel most nodes"],
          ["Network providers (ASNs)", "5", "No single ISP sees most traffic"],
          ["Largest operator's mixing share", "≤ 20%", "Limits end-to-end correlation"],
        ]}
        columnAlign={["left", "right", "left"]}
      />
      <Grid columns={3} gap={16}>
        <Stat value="< 3%" label="Battery per day, typical use" />
        <Stat value="< 50 MB" label="Cellular data per day" />
        <Stat value="Pi 5" label="Minimum node hardware" />
      </Grid>
    </Stack>
  );
}

// ---------- comparisons ----------

function ComparisonsTab() {
  return (
    <Stack gap={24}>
      <H2>khensu.nu vs Signal vs Telegram</H2>
      <Table
        headers={["", "Signal", "Telegram", "khensu.nu"]}
        rows={[
          ["Identity", "Phone number (usernames optional)", "Phone number", "Key pair; optional permanent handle; no phone or email"],
          ["Default encryption", "End-to-end, PQXDH + SPQR", "Server-side; E2EE only in 1:1 secret chats", "End-to-end for everything, pure ML-KEM-1024"],
          ["Identity signatures", "Classical", "Classical", "ML-DSA-87"],
          ["Who-talks-to-whom", "Server sees recipient, IP, timing", "Server sees everything", "Three-layer mixnet with cover traffic"],
          ["Group size (E2EE)", "1,000", "Not E2EE", "1,000 devices, TreeKEM"],
          ["Call IP privacy", "Relay sees both IPs", "Peer-to-peer or server", "Two relays, different operators"],
          ["Search and AI", "Local search", "Server search, cloud AI", "Hindsight-style memory, on-device model only"],
          ["Push", "Content-free wake", "Previews via Apple/Google", "Anonymous \"New message\", blind gateway"],
          ["Payments", "MobileCoin (opt-in)", "Stars, TON", "Shielded STARK notes over the mixnet, expiring records"],
          ["Infrastructure", "Signal's servers", "Telegram's servers", "Independent operator nodes, down to a Pi 5"],
        ]}
      />
      <H2>khensu.nu chain vs post-quantum coins</H2>
      <Table
        headers={["", "QRL", "Algorand", "Abelian", "Zcash / Monero", "khensu.nu chain"]}
        rows={[
          ["Signatures", "XMSS (stateful)", "Falcon opt-in, Ed25519 default", "Lattice (custom)", "Classical", "ML-DSA-87, stateless, incl. consensus"],
          ["Payment privacy", "None", "None", "Lattice-based", "Classical (archived notes decryptable later)", "STARK + ML-KEM-1024"],
          ["Network privacy", "None", "None", "None", "Partial (Dandelion++)", "Post-quantum mixnet"],
          ["History", "Permanent", "Permanent", "Permanent", "Permanent", "Shielded eras deleted"],
          ["Demand", "Speculative", "Smart contracts", "Payments", "Payments", "Burned for media and messaging capacity"],
          ["Node hardware", "Server", "Server", "Server", "Server", "Raspberry Pi 5"],
        ]}
      />
      <Callout tone="neutral" title="Where we start behind">
        No track record (QRL since 2018), no liquidity until the burn auction and listings, and bigger transactions (4.6 KB signatures, tens of KB of proof). Formal models, audits and a long public testnet close the gap.
      </Callout>
    </Stack>
  );
}

// ---------- roadmap ----------

const PHASES = [
  { name: "Threat model, spec, legal, export, design", start: 0, end: 3 },
  { name: "MLS hardening and TreeKEM", start: 3, end: 9 },
  { name: "Node core and consensus testnet", start: 3, end: 12 },
  { name: "App alpha (iOS, macOS)", start: 5, end: 12 },
  { name: "Mixnet and Outfox paper", start: 9, end: 16 },
  { name: "Shielded payments (STARK pool)", start: 12, end: 18 },
  { name: "Key transparency and identity", start: 10, end: 15 },
  { name: "Audits", start: 14, end: 20 },
  { name: "Public testnet", start: 18, end: 22 },
  { name: "Mainnet and App Store launch", start: 22, end: 24 },
];

function Gantt() {
  const theme = useHostTheme();
  return (
    <Stack gap={6}>
      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 8, alignItems: "center" }}>
        <span />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(24, 1fr)" }}>
          {Array.from({ length: 24 }, (_, i) => (
            <span key={i} style={{ fontSize: 10, color: theme.text.tertiary, textAlign: "center" }}>
              {i % 3 === 0 ? `M${i}` : ""}
            </span>
          ))}
        </div>
      </div>
      {PHASES.map((p) => (
        <div key={p.name} style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 8, alignItems: "center" }}>
          <Text size="small">{p.name}</Text>
          <div style={{ position: "relative", height: 14, background: theme.fill.quaternary, borderRadius: 4 }}>
            <div
              style={{
                position: "absolute",
                left: `${(p.start / 24) * 100}%`,
                width: `${((p.end - p.start) / 24) * 100}%`,
                top: 0,
                bottom: 0,
                borderRadius: 4,
                background: p.name.startsWith("Mainnet") ? theme.category.yellow : theme.accent.primary,
              }}
            />
          </div>
        </div>
      ))}
      <Text size="small" tone="tertiary">Months from start (estimate). Source: plan, Launch readiness section 10.</Text>
    </Stack>
  );
}

function RoadmapTab() {
  return (
    <Stack gap={24}>
      <H2>24-month roadmap</H2>
      <Gantt />
      <Grid columns="minmax(0, 1fr) minmax(0, 1.2fr)" gap={24} align="start">
        <Stack gap={8}>
          <H3>Budget estimate (USD millions, 24 months)</H3>
          <PieChart
            donut
            size={180}
            data={[
              { label: "Engineering team", value: 2.2 },
              { label: "Audits", value: 0.6 },
              { label: "Legal and export", value: 0.25 },
              { label: "Design", value: 0.1 },
              { label: "Genesis nodes and infra", value: 0.1 },
            ]}
          />
          <Text size="small" tone="tertiary">Midpoint of the plan's $2.5M–$4M range. Audits cover MLS, chain, shielded pool and app.</Text>
        </Stack>
        <Stack gap={8}>
          <H3>Team</H3>
          <Table
            headers={["Role", "Count"]}
            rows={[
              ["iOS engineers", "2"],
              ["Protocol engineers (Go, Rust)", "2"],
              ["Cryptographer", "1"],
              ["Zero-knowledge and chain engineer", "1"],
              ["SRE", "1"],
              ["Designer", "1"],
              ["Counsel (crypto, export, privacy)", "Part-time"],
            ]}
            columnAlign={["left", "right"]}
          />
        </Stack>
      </Grid>
      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader trailing={<Pill size="sm">v1</Pill>}>One release, no tiers</CardHeader>
          <CardBody>
            <Text size="small">
              Everything ships together: messaging, groups, calls, mixnet, key transparency, identity and handles, push, typing, on-device memory and knowledge pages, token and burn auction, shielded payments, Wi-Fi Aware offline mode, CarPlay calls, Push to Talk. If the schedule slips, the date moves, not features.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Pill size="sm">outside approval</Pill>}>Switches on when approved</CardHeader>
          <CardBody>
            <Text size="small">Payments region by region after legal review; CarPlay, default messaging and calling app, and external purchase links once Apple grants the entitlements.</Text>
          </CardBody>
        </Card>
      </Grid>
    </Stack>
  );
}

// ---------- links ----------

const PLAN_SECTIONS: Array<[string, number]> = [
  ["Goals and non-negotiables", 112],
  ["Why it's better than Signal", 121],
  ["Telegram's features, end-to-end encrypted", 141],
  ["What exists and the gaps", 173],
  ["Architecture", 203],
  ["Consensus", 252],
  ["Governance and founder safeguards", 270],
  ["Identity, addresses and handles", 288],
  ["App design", 330],
  ["Local search and memory", 344],
  ["Push notifications", 378],
  ["Apple platform features", 403],
  ["Mix packet format: Outfox", 421],
  ["Cryptographic design", 435],
  ["Money", 466],
  ["Shielded payments", 485],
  ["Compared with post-quantum coins", 497],
  ["Launch readiness", 512],
  ["Repository layout", 585],
  ["Documentation and patents", 600],
  ["Milestones", 627],
  ["Decisions", 639],
];

const EXTERNAL: Array<[string, string, string]> = [
  ["Hindsight (agent memory, MIT)", "https://hindsight.vectorize.io/", "Design basis for on-device memory"],
  ["SEC/CFTC crypto asset interpretation (Mar 2026)", "https://www.sec.gov/newsroom/press-releases/2026-30-sec-clarifies-application-federal-securities-laws-crypto-assets", "Digital commodity vs digital security"],
  ["CLARITY Act stalls in the Senate (Orrick)", "https://www.orrick.com/Insights/2026/10/The-CLARITY-Act-Stalls-in-the-Senate-Whats-Next-for-Digital-Asset-Regulation", "Regulation Crypto Assets proposal"],
  ["App Review Guidelines", "https://developer.apple.com/app-store/review/guidelines/", "4.8 login, 5.1.1(v) deletion, 3.1.5 crypto"],
  ["Enabling enhanced security for your app", "https://developer.apple.com/documentation/xcode/enabling-enhanced-security-for-your-app", "Memory Integrity Enforcement"],
  ["Memory Integrity Enforcement (Apple Security Research)", "https://security.apple.com/blog/memory-integrity-enforcement/", "Why messaging apps should enable it"],
  ["CarPlay Developer Guide", "https://developer.apple.com/download/files/CarPlay-Developer-Guide.pdf", "SiriKit required for CarPlay messaging"],
  ["Spatial audio profile entitlement", "https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.spatial-audio.profile-access", "Personalized spatial audio in calls"],
  ["RFC 9420: Messaging Layer Security", "https://www.rfc-editor.org/rfc/rfc9420", "Group key agreement"],
  ["Quantum-resistant coins (Tangem)", "https://tangem.com/en/blog/post/quantum-resistant-crypto/", "Competitive landscape (note: IOTA claim is outdated)"],
];

function LinksTab() {
  const dispatch = useCanvasAction();
  const open = (line: number) =>
    dispatch({ type: "openFile", path: PLAN, selection: { startLineNumber: line, startColumn: 1, endLineNumber: line, endColumn: 1 } });
  return (
    <Grid columns="minmax(0, 1fr) minmax(0, 1.3fr)" gap={32} align="start">
      <Stack gap={8}>
        <H2>Plan sections</H2>
        <Text size="small" tone="secondary">
          Opens the plan at that heading.
        </Text>
        <Stack gap={2}>
          {PLAN_SECTIONS.map(([name, line]) => (
            <Row key={name} gap={8} align="center" style={{ padding: "3px 0" }}>
              <Button variant="ghost" onClick={() => open(line)}>
                {name}
              </Button>
              <Text size="small" tone="quaternary">
                line {line}
              </Text>
            </Row>
          ))}
          <Divider />
          <Row gap={8} align="center">
            <Button variant="secondary" onClick={() => dispatch({ type: "openFile", path: CAPS })}>
              App ID capabilities
            </Button>
          </Row>
        </Stack>
      </Stack>
      <Stack gap={8}>
        <H2>External references</H2>
        {EXTERNAL.map(([name, href, note]) => (
          <Stack key={href} gap={0} style={{ padding: "4px 0" }}>
            <Link href={href}>{name}</Link>
            <Text size="small" tone="tertiary">
              {note}
            </Text>
          </Stack>
        ))}
      </Stack>
    </Grid>
  );
}

// ---------- page ----------

export default function KhensuDesign() {
  const theme = useHostTheme();
  const [tab, setTab] = useCanvasState<Tab>("tab", "Screens");
  return (
    <Stack gap={20} style={{ padding: 24, maxWidth: 1180 }}>
      <Row gap={12} align="center">
        <Crescent size={30} bg={theme.bg.editor} />
        <Stack gap={2}>
          <H1>khensu.nu design canvas</H1>
          <Text tone="secondary">Decentralized, post-quantum Signal replacement on MOQOM · bundle nu.khensu.ptah · nodes at tatenan.khensu.nu</Text>
        </Stack>
      </Row>
      <Row gap={6} wrap>
        {TABS.map((t) => (
          <Pill key={t} active={t === tab} onClick={() => setTab(t)}>
            {t}
          </Pill>
        ))}
      </Row>
      <Divider />
      {tab === "Screens" && <ScreensTab />}
      {tab === "Architecture" && <ArchitectureTab />}
      {tab === "Economics" && <EconomicsTab />}
      {tab === "Network" && <NetworkTab />}
      {tab === "Comparisons" && <ComparisonsTab />}
      {tab === "Roadmap" && <RoadmapTab />}
      {tab === "Links" && <LinksTab />}
    </Stack>
  );
}
