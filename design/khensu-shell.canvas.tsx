import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Code,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
  useHostTheme,
} from "cursor/canvas";

// Geometry and results mirror hardware/shell/shell.py and out/summary.json (khensu-specs).

type PhoneId = "pro-plateau" | "island";
type StyleId = "card" | "fill" | "wrap" | "wrap-xl" | "case";

type Phone = {
  id: PhoneId;
  label: string;
  w: number;
  h: number;
  depth: number;
  r: number;
  bump: { x0: number; y0: number; w: number; h: number; r: number; z: number };
  magsafeY: number;
};

const PHONES: Record<PhoneId, Phone> = {
  "pro-plateau": {
    id: "pro-plateau",
    label: "Pro phone, camera plateau",
    w: 71.9, h: 150.0, depth: 8.75, r: 10,
    bump: { x0: 0, y0: 0, w: 71.9, h: 44, r: 10, z: 3.5 },
    magsafeY: -5,
  },
  island: {
    id: "island",
    label: "Standard phone, camera island",
    w: 71.5, h: 147.6, depth: 7.8, r: 10,
    bump: { x0: 4.5, y0: 4.5, w: 38, h: 38, r: 8, z: 2.6 },
    magsafeY: 0,
  },
};

const B = {
  wall: 1.0, skin: 0.7, base: 0.6, suction: 0.3, gap: 0.6, inset: 0.4,
  magnetOD: 56, magnetID: 46, magnetT: 0.5, coilD: 44, coilT: 0.8,
  pcbL: 34, pcbW: 14, pcbT: 1.6, antL: 40, antW: 8, usbW: 9.2,
};

type Result = {
  footprint: [number, number];
  t: number;
  wh: number;
  cm3: number;
  tiG: number;
  proud: number;
  usb: boolean;
  ring: number;
};

const RESULTS: Record<PhoneId, Record<Exclude<StyleId, "case">, Result>> = {
  "pro-plateau": {
    card: { footprint: [56, 86], t: 5.2, wh: 4.1, cm3: 9.19, tiG: 50, proud: 1.7, usb: false, ring: 53 },
    fill: { footprint: [65.9, 101.4], t: 3.5, wh: 2.2, cm3: 4.92, tiG: 47, proud: 0, usb: true, ring: 56 },
    wrap: { footprint: [71.1, 105.0], t: 3.5, wh: 2.8, cm3: 6.26, tiG: 54, proud: 0, usb: true, ring: 56 },
    "wrap-xl": { footprint: [71.1, 105.0], t: 6.5, wh: 11.4, cm3: 25.34, tiG: 102, proud: 3.0, usb: true, ring: 56 },
  },
  island: {
    card: { footprint: [56, 86], t: 5.2, wh: 4.1, cm3: 9.17, tiG: 50, proud: 2.6, usb: false, ring: 53 },
    fill: { footprint: [65.5, 100.5], t: 3.4, wh: 2.0, cm3: 4.5, tiG: 46, proud: 0.8, usb: true, ring: 56 },
    wrap: { footprint: [70.7, 146.8], t: 3.4, wh: 3.5, cm3: 7.74, tiG: 65, proud: 0.8, usb: true, ring: 56 },
    "wrap-xl": { footprint: [70.7, 146.8], t: 6.4, wh: 13.4, cm3: 29.76, tiG: 123, proud: 3.8, usb: true, ring: 56 },
  },
};

const STYLE_INFO: Record<StyleId, { name: string; line: string }> = {
  card: { name: "Card", line: "Pocket-size, 56 × 86 × 5.2 mm, snaps on MagSafe below the camera" },
  fill: { name: "Fill", line: "Fills the flat area below the camera bump, flush with it" },
  wrap: { name: "Wrap", line: "Covers the whole back around the bump; the back becomes flat" },
  "wrap-xl": { name: "Wrap XL", line: "Wrap 3 mm thicker, for relaying all day" },
  case: { name: "Silicone case", line: "Shock case that holds the phone with a Wrap module inside" },
};

const STYLE_ORDER: StyleId[] = ["card", "fill", "wrap", "wrap-xl", "case"];

type Rect = { cx: number; cy: number; w: number; h: number; r: number };

function bumpRect(p: Phone): Rect {
  return {
    cx: -p.w / 2 + p.bump.x0 + p.bump.w / 2,
    cy: p.h / 2 - p.bump.y0 - p.bump.h / 2,
    w: p.bump.w, h: p.bump.h, r: p.bump.r,
  };
}

function bumpBottom(p: Phone): number {
  return p.h / 2 - p.bump.y0 - p.bump.h;
}

function cardCenterY(p: Phone): number {
  return Math.min(p.magsafeY, bumpBottom(p) - B.gap - 43 - 1);
}

/** Outline rectangles: the first is the shell; any after are holes. */
function outline(p: Phone, s: StyleId): Rect[] {
  const bb = bumpBottom(p) - B.gap;
  const b = bumpRect(p);
  const cut: Rect = { cx: b.cx, cy: b.cy, w: b.w + 2 * B.gap, h: b.h + 2 * B.gap, r: b.r + B.gap };
  if (s === "card") return [{ cx: 0, cy: cardCenterY(p), w: 56, h: 86, r: 8 }];
  if (s === "fill") {
    const bot = -p.h / 2 + 4;
    return [{ cx: 0, cy: (bb + bot) / 2, w: p.w - 6, h: bb - bot, r: p.r - 3 }];
  }
  if (s === "case") return [{ cx: 0, cy: 0, w: p.w + 3.2, h: p.h + 3.2, r: p.r + 1.6 }, { ...cut, w: b.w + 1.6, h: b.h + 1.6, r: b.r + 0.8 }];
  if (p.bump.w >= p.w - 2 * p.r) {
    const bot = -p.h / 2 + B.inset;
    return [{ cx: 0, cy: (bb + bot) / 2, w: p.w - 2 * B.inset, h: bb - bot, r: 1 }];
  }
  return [{ cx: 0, cy: 0, w: p.w - 2 * B.inset, h: p.h - 2 * B.inset, r: p.r - B.inset }, cut];
}

function rrPath(r: Rect, sx: (x: number) => number, sy: (y: number) => number, k: number): string {
  const rad = Math.min(r.r, r.w / 2, r.h / 2) * k;
  const x0 = sx(r.cx - r.w / 2), x1 = sx(r.cx + r.w / 2);
  const y0 = sy(r.cy + r.h / 2), y1 = sy(r.cy - r.h / 2);
  return [
    `M${x0 + rad},${y0}`, `H${x1 - rad}`, `A${rad},${rad} 0 0 1 ${x1},${y0 + rad}`,
    `V${y1 - rad}`, `A${rad},${rad} 0 0 1 ${x1 - rad},${y1}`,
    `H${x0 + rad}`, `A${rad},${rad} 0 0 1 ${x0},${y1 - rad}`,
    `V${y0 + rad}`, `A${rad},${rad} 0 0 1 ${x0 + rad},${y0}`, "Z",
  ].join(" ");
}

function internals(p: Phone, s: Exclude<StyleId, "case">) {
  const o = outline(p, s)[0];
  const ymin = o.cy - o.h / 2 + B.wall;
  const xmin = o.cx - o.w / 2 + B.wall;
  const innerW = o.w - 2 * B.wall;
  const ring = RESULTS[p.id][s].ring;
  const pcbL = Math.min(B.pcbL, innerW - 2);
  return {
    ringOD: ring,
    ringID: ring - (B.magnetOD - B.magnetID),
    magsafe: { x: 0, y: p.magsafeY },
    antenna: { cx: 0, cy: ymin + B.antW / 2 + 0.5, w: Math.min(B.antL, innerW - 2), h: B.antW, r: 1 },
    pcb: { cx: xmin + pcbL / 2 + 1, cy: ymin + B.antW + 1.5 + B.pcbW / 2, w: pcbL, h: B.pcbW, r: 1 },
    usb: RESULTS[p.id][s].usb ? { cx: 0, cy: o.cy - o.h / 2 + 1.5, w: B.usbW, h: 3, r: 1.2 } : null,
    inner: { cx: o.cx, cy: o.cy, w: innerW, h: o.h - 2 * B.wall, r: Math.max(0.5, o.r - B.wall) },
  };
}

function BackView({ phone, style, scale, showInternals }: { phone: Phone; style: StyleId; scale: number; showInternals: boolean }) {
  const t = useHostTheme();
  const pad = 14;
  const W = (phone.w + 3.2) * scale + pad * 2;
  const H = (phone.h + 3.2) * scale + pad * 2;
  const sx = (x: number) => W / 2 + x * scale;
  const sy = (y: number) => H / 2 - y * scale;
  const body: Rect = { cx: 0, cy: 0, w: phone.w, h: phone.h, r: phone.r };
  const shapes = outline(phone, style);
  const shellPath = shapes.map((r) => rrPath(r, sx, sy, scale)).join(" ");
  const inner = style !== "case" ? internals(phone, style) : null;
  const hatchId = `hatch-${phone.id}-${style}-${scale}`;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: "block" }}>
      <defs>
        <pattern id={hatchId} width={6} height={6} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1={0} y1={0} x2={0} y2={6} stroke={t.category.green} strokeWidth={1.4} opacity={0.55} />
        </pattern>
      </defs>
      {style === "case" ? (
        <>
          <path d={shellPath} fill={t.fill.secondary} fillRule="evenodd" stroke={t.text.secondary} strokeWidth={1} />
          <path d={rrPath(body, sx, sy, scale)} fill="none" stroke={t.stroke.secondary} strokeDasharray="3 3" />
        </>
      ) : (
        <>
          <path d={rrPath(body, sx, sy, scale)} fill={t.bg.chrome} stroke={t.stroke.primary} strokeWidth={1} />
          <path d={rrPath(bumpRect(phone), sx, sy, scale)} fill={t.fill.tertiary} stroke={t.stroke.primary} />
          <path d={shellPath} fill={t.fill.secondary} fillRule="evenodd" stroke={t.accent.primary} strokeWidth={1.6} />
        </>
      )}
      {style === "case" && (
        <path d={rrPath(bumpRect(phone), sx, sy, scale)} fill={t.fill.tertiary} stroke={t.stroke.primary} />
      )}
      {inner && showInternals && (
        <g>
          <path d={rrPath(inner.inner, sx, sy, scale)} fill={`url(#${hatchId})`} stroke="none" />
          <circle cx={sx(inner.magsafe.x)} cy={sy(inner.magsafe.y)} r={(inner.ringOD / 2 + 1) * scale} fill={t.bg.editor} />
          <circle cx={sx(inner.magsafe.x)} cy={sy(inner.magsafe.y)} r={((inner.ringOD + inner.ringID) / 4) * scale}
            fill="none" stroke={t.text.secondary} strokeWidth={((inner.ringOD - inner.ringID) / 2) * scale} opacity={0.5} />
          <circle cx={sx(inner.magsafe.x)} cy={sy(inner.magsafe.y)} r={(B.coilD / 2) * scale}
            fill="none" stroke={t.category.yellow} strokeWidth={1.4} strokeDasharray="4 3" />
          <path d={rrPath(inner.pcb, sx, sy, scale)} fill={t.category.blue} opacity={0.75} />
          <path d={rrPath(inner.antenna, sx, sy, scale)} fill="none" stroke={t.category.pink} strokeWidth={1.4} strokeDasharray="2 2" />
          {inner.usb && <path d={rrPath(inner.usb, sx, sy, scale)} fill={t.text.primary} />}
        </g>
      )}
    </svg>
  );
}

function SectionView({ phone, style }: { phone: Phone; style: Exclude<StyleId, "case"> }) {
  const t = useHostTheme();
  const o = outline(phone, style)[0];
  const r = RESULTS[phone.id][style];
  const inner = internals(phone, style);
  const T = r.t;
  const kx = 3.4;
  const kz = 14;
  const padX = 20;
  const padTop = 18;
  const y0 = o.cy - o.h / 2;
  const y1 = o.cy + o.h / 2;
  const W = (y1 - y0) * kx + padX * 2;
  const H = (Math.max(T, phone.bump.z) + 1.8) * kz + padTop + 40;
  const X = (y: number) => padX + (y - y0) * kx;
  const Z = (z: number) => padTop + (Math.max(T, phone.bump.z) - z) * kz;
  const box = (ya: number, yb: number, za: number, zb: number, fill: string, op = 1, stroke?: string) => (
    <rect x={X(ya)} y={Z(zb)} width={Math.max(0, (yb - ya) * kx)} height={Math.max(0, (zb - za) * kz)}
      fill={fill} opacity={op} stroke={stroke} strokeWidth={stroke ? 1 : 0} />
  );
  const zb = B.suction + B.base;
  const top = T - B.skin;
  const coilZ = top - B.coilT;
  const hasCoil = coilZ >= zb + B.magnetT + 0.1;
  const zoneA = inner.magsafe.y - (inner.ringOD / 2 + 1);
  const zoneB = inner.magsafe.y + (inner.ringOD / 2 + 1);
  const stacked = coilZ - (zb + B.magnetT) - 0.2;
  const yi0 = y0 + B.wall;
  const yi1 = y1 - B.wall;
  const pcbA = inner.pcb.cy - B.pcbW / 2;
  const pcbB = inner.pcb.cy + B.pcbW / 2;
  const antB = inner.antenna.cy + B.antW / 2;
  const batFrom = Math.max(pcbB + 1, antB + 1);
  const ringA = (inner.ringOD + inner.ringID) / 4;
  const ringW = (inner.ringOD - inner.ringID) / 2;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: "block" }}>
      <line x1={X(y0) - 12} x2={X(y1) + 12} y1={Z(0)} y2={Z(0)} stroke={t.stroke.primary} />
      <text x={X(y0) - 12} y={Z(0) + 14} fontSize={10} fill={t.text.tertiary}>phone back glass</text>
      <line x1={X(y0) - 12} x2={X(y1) + 12} y1={Z(phone.bump.z)} y2={Z(phone.bump.z)} stroke={t.text.tertiary} strokeDasharray="4 4" />
      <text x={X(y1) + 12} y={Z(phone.bump.z) - 4} fontSize={10} fill={t.text.tertiary} textAnchor="end">camera bump height {phone.bump.z} mm</text>
      {box(y0, y1, 0, B.suction, t.category.gray, 0.6)}
      {box(yi0, yi1, B.suction, zb, t.fill.primary, 0.6)}
      {box(y0, yi0, B.suction, T, t.text.secondary, 0.85)}
      {box(yi1, y1, B.suction, T, t.text.secondary, 0.85)}
      {box(y0, y1, top, T, t.text.secondary, 0.85)}
      {box(inner.antenna.cy - B.antW / 2, antB, zb, top, t.category.pink, 0.25)}
      {inner.pcb.cx - B.pcbL / 2 <= 0 && box(pcbA, pcbB, zb, zb + B.pcbT, t.category.blue, 0.8)}
      {box(Math.max(batFrom, yi0 + 0.5), Math.min(zoneA, yi1 - 0.5), zb + 0.05, top - 0.05, t.category.green, 0.45)}
      {box(Math.max(zoneB, batFrom), yi1 - 0.5, zb + 0.05, top - 0.05, t.category.green, 0.45)}
      {box(inner.magsafe.y - ringA - ringW / 2, inner.magsafe.y - ringA + ringW / 2, zb, zb + B.magnetT, t.text.primary, 0.8)}
      {box(inner.magsafe.y + ringA - ringW / 2, inner.magsafe.y + ringA + ringW / 2, zb, zb + B.magnetT, t.text.primary, 0.8)}
      {stacked >= 0.8 && box(Math.max(zoneA, yi0 + 0.5), Math.min(zoneB, yi1 - 0.5), zb + B.magnetT + 0.1, zb + B.magnetT + 0.1 + stacked, t.category.green, 0.45)}
      {hasCoil && box(inner.magsafe.y - B.coilD / 2, inner.magsafe.y + B.coilD / 2, coilZ, top, t.category.yellow, 0.75)}
      <text x={X(y0)} y={H - 8} fontSize={10} fill={t.text.tertiary}>bottom edge</text>
      <text x={X(y1)} y={H - 8} fontSize={10} fill={t.text.tertiary} textAnchor="end">toward camera</text>
      <text x={(X(y0) + X(y1)) / 2} y={H - 8} fontSize={10} fill={t.text.tertiary} textAnchor="middle">
        {`${(y1 - y0).toFixed(0)} mm long, ${T} mm thick (height drawn ${(kz / kx).toFixed(1)}× for legibility)`}
      </text>
    </svg>
  );
}

function Legend() {
  const t = useHostTheme();
  const items: [string, string, boolean][] = [
    ["Shell outline", t.accent.primary, false],
    ["Battery cells", t.category.green, false],
    ["MagSafe magnet ring", t.text.secondary, false],
    ["Qi2 coil (charges the shell)", t.category.yellow, true],
    ["Board and radios", t.category.blue, false],
    ["HaLow antenna window (no metal)", t.category.pink, true],
    ["USB-C to phone", t.text.primary, false],
  ];
  return (
    <Stack gap={6}>
      {items.map(([label, color, dashed]) => (
        <Row key={label} gap={8} align="center">
          <svg width={22} height={10}>
            {dashed ? (
              <line x1={1} y1={5} x2={21} y2={5} stroke={color} strokeWidth={2} strokeDasharray="4 3" />
            ) : (
              <rect x={1} y={1} width={20} height={8} rx={2} fill={color} opacity={0.8} />
            )}
          </svg>
          <Text size="small" tone="secondary">{label}</Text>
        </Row>
      ))}
    </Stack>
  );
}

export default function KhensuShell() {
  const t = useHostTheme();
  const [phoneId, setPhoneId] = useCanvasState<PhoneId>("phone", "pro-plateau");
  const [style, setStyle] = useCanvasState<StyleId>("style", "wrap");
  const [showInternals, setShowInternals] = useCanvasState<boolean>("internals", true);
  const phone = PHONES[phoneId];
  const res = style === "case" ? null : RESULTS[phoneId][style];

  return (
    <Stack gap={24} style={{ padding: 24, maxWidth: 1120 }}>
      <Stack gap={6}>
        <H1>khensu shell: attachment styles</H1>
        <Text tone="secondary">
          A mesh node on the back of the phone: HaLow radio for the neighbourhood mesh, Wi-Fi and Bluetooth to the phone, its own battery, and fallback power from the phone over USB-C. Every drawing is to scale and generated from the same parametric CAD (<Code>khensu-specs/hardware/shell/shell.py</Code>), which exports STEP and STL for CNC and tooling.
        </Text>
      </Stack>

      <Row gap={8} wrap>
        {(Object.keys(PHONES) as PhoneId[]).map((id) => (
          <Pill key={id} active={phoneId === id} onClick={() => setPhoneId(id)}>{PHONES[id].label}</Pill>
        ))}
        <div style={{ width: 16 }} />
        {STYLE_ORDER.map((id) => (
          <Pill key={id} active={style === id} onClick={() => setStyle(id)}>{STYLE_INFO[id].name}</Pill>
        ))}
        <div style={{ width: 16 }} />
        <Pill active={showInternals} onClick={() => setShowInternals(!showInternals)}>Show internals</Pill>
      </Row>

      <Grid columns="auto 1fr" gap={28} align="start">
        <div style={{ border: `1px solid ${t.stroke.secondary}`, borderRadius: 8, padding: 8, background: t.bg.editor }}>
          <BackView phone={phone} style={style} scale={2.6} showInternals={showInternals} />
        </div>
        <Stack gap={18}>
          <Stack gap={4}>
            <H2>{STYLE_INFO[style].name}</H2>
            <Text tone="secondary">{STYLE_INFO[style].line}.</Text>
          </Stack>
          {res ? (
            <>
              <Row gap={28} wrap>
                <Stat value={`${res.wh} Wh`} label={`battery (${res.cm3} cm³ of cells)`} />
                <Stat value={`${res.t} mm`} label={res.proud > 0 ? `thick, ${res.proud} mm proud of the bump` : "thick, flush with the bump"} />
                <Stat value={`${res.tiG} g`} label="titanium" />
              </Row>
              <Text size="small" tone="tertiary">
                Footprint {res.footprint[0]} × {res.footprint[1]} mm. Magnet ring {res.ring} mm. {res.usb ? "USB-C plug powers it from the phone when its own cells run out." : "No plug: runs on its own cells and covers the phone's MagSafe coil, so the phone charges with the card off."}
              </Text>
              <Stack gap={6}>
                <H3>Section through the MagSafe centre</H3>
                <div style={{ overflowX: "auto" }}>
                  <SectionView phone={phone} style={style as Exclude<StyleId, "case">} />
                </div>
              </Stack>
            </>
          ) : (
            <Stack gap={10}>
              <Row gap={28} wrap>
                <Stat value="1.6 mm" label="walls, raised corners" />
                <Stat value="~17 g" label="LSR silicone, Shore 50–60A" />
              </Row>
              <Text size="small" tone="tertiary">
                Holds the phone with a Wrap module inside; the camera opening is cut through. Before tooling: 0.5–1° draft on all walls, and button, speaker, microphone and USB-C openings from Apple's drawings. The dive version is a rigid polycarbonate housing with O-ring seals.
              </Text>
            </Stack>
          )}
          <Divider />
          <Legend />
        </Stack>
      </Grid>

      <Stack gap={10}>
        <H2>All styles on the {PHONES[phoneId].label.toLowerCase()}</H2>
        <Row gap={14} wrap align="start">
          {STYLE_ORDER.map((id) => (
            <div key={id} onClick={() => setStyle(id)} style={{
              cursor: "pointer", padding: 8, borderRadius: 8,
              border: `1px solid ${style === id ? t.accent.primary : t.stroke.tertiary}`,
            }}>
              <BackView phone={phone} style={id} scale={1.15} showInternals={false} />
              <Text size="small" weight={style === id ? "semibold" : "normal"} style={{ textAlign: "center", marginTop: 4 }}>
                {STYLE_INFO[id].name}
              </Text>
              <Text size="small" tone="tertiary" style={{ textAlign: "center" }}>
                {id === "case" ? "holds a Wrap" : `${RESULTS[phoneId][id].wh} Wh · ${RESULTS[phoneId][id].t} mm`}
              </Text>
            </div>
          ))}
        </Row>
      </Stack>

      <Stack gap={10}>
        <H2>Battery and weight, both reference phones</H2>
        <Table
          headers={["Style", "Phone", "Footprint (mm)", "Thickness (mm)", "Battery (Wh)", "Relays alone (≈1 W)", "Mass, titanium (g)"]}
          columnAlign={["left", "left", "right", "right", "right", "right", "right"]}
          rows={(Object.keys(PHONES) as PhoneId[]).flatMap((pid) =>
            (["card", "fill", "wrap", "wrap-xl"] as const).map((sid) => {
              const r = RESULTS[pid][sid];
              return [
                STYLE_INFO[sid].name,
                pid === "pro-plateau" ? "Pro" : "Standard",
                `${r.footprint[0]} × ${r.footprint[1]}`,
                r.proud > 0 ? `${r.t} (+${r.proud})` : `${r.t} (flush)`,
                r.wh.toFixed(1),
                `${r.wh.toFixed(0)} h`,
                `${r.tiG}`,
              ];
            }),
          )}
        />
        <Text size="small" tone="tertiary">
          Source: shell.py CAD output. Cells at 0.45 Wh/cm³ (thin pouch). "+" is height above the camera bump. Relay time assumes about 1 W average for board and radios (an estimate until the board exists); after that the shell runs from the phone over USB-C. Phone dimensions are placeholders until Apple's accessory drawings replace them.
        </Text>
      </Stack>

      <Grid columns={3} gap={16}>
        <Card>
          <CardHeader>Runs cool</CardHeader>
          <CardBody>
            <Text size="small" tone="secondary">
              About 1 W spread across the back is a few degrees of rise. Charging is the real heat source, so the shell never charges itself and the phone at full rate together. A 25 µm graphite sheet spreads heat into the metal skin; above 41 °C skin temperature it cuts charging first, then pauses optional work. The board stays on and the 2 s tick never changes, at any battery level.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Unstoppable links</CardHeader>
          <CardBody>
            <Text size="small" tone="secondary">
              Three independent paths: the internet through the phone or Wi-Fi as WebTransport on UDP 443 (looks like ordinary HTTPS/3, no SNI); the HaLow mesh to nearby shells and home nodes (about 1 km); Bluetooth LE to wake the phone without Apple's push. Losing any one leaves the others.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Made in metal</CardHeader>
          <CardBody>
            <Text size="small" tone="secondary">
              CNC titanium Grade 5 only, 1.0 mm walls and 0.7 mm skin. Metal blocks radio and wireless charging, so the coil area and a 40 mm strip along the bottom edge are PC windows, like the bands on a phone frame. Glass-filled PC base, die-cut micro-suction film.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="warning" title="Three findings from the CAD">
        Slim shells can't go below about 3.4 mm (film, base, board, skin), so on phones with a low bump they sit up to 0.8 mm proud. A slim shell holds 2–4 Wh, not the 8–10 Wh first estimated; with the board always on, that's a few hours on its own cells before it draws about 1 W from the phone over USB-C (roughly 6–7% of a Pro iPhone's battery per hour); the card has no plug and stops. Only the XL runs all day on its own. The Pocket-size card fits a 53 mm magnet ring, not the full 56 mm one, and blocks the phone's MagSafe charging while attached.
      </Callout>
    </Stack>
  );
}
