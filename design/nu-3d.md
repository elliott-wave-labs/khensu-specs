# nu-3d: the .nu 3D format

How khensu.nu carries 3D models, scenes and Gaussian splats in fewer bits than USDZ and GLB, with smoother surfaces and higher texture resolution, and with nothing in the file that can run code or reach the network. A 3D `.nu` file is a nu-media object (`design/nu-media-protocol.md`): the same `"nuMe"` magic, stream header, tracks, frames and extensions as images and video, with new track kinds and codecs for scenes. khensu apps read `.nu` directly; for everything else the app writes USDZ (RealityKit, Reality Composer Pro, AR Quick Look) or GLB (Android Scene Viewer, `<model-viewer>`, the web) on the device, or a **wrapped** USDZ or GLB that opens anywhere and carries the `.nu` payload inside for khensu apps.

Status: design, 11 October 2026. **Nothing here is built or measured.** Every size and time for `.nu` is a **design target**; every figure for USDZ, GLB, Draco, meshoptimizer and KTX2 is an **estimate** from typical published results unless a measurement is cited. Section 10 is the benchmark that replaces them. Registry values proposed here are listed in `nu-media-protocol.md` 16.10. Open questions are in section 12 and `OPEN-QUESTIONS.md` section H (91–96). Provenance and signatures for 3D are in `design/nu-provenance.md`.

## 1. What the owner asked for, and what it means

| Ask | What `.nu` does |
| --- | --- |
| Smaller | Quantised, predicted and entropy-coded geometry (Draco and meshoptimizer class, with an optional learned integer context model); textures in the learned `nu_image_v1` codec instead of PNG or JPEG; one container with no zip, XML or JSON overhead |
| Faster | Progressive: a coarse mesh and colour preview in the first 1,990-byte tick chunk, refined by every later chunk; GPU-ready layouts (meshlets, ASTC-ready textures) so decode goes straight into Metal buffers |
| More secure | No scripts, no behaviours, no external references; USD composition arcs and glTF external URIs are resolved and flattened at import; strict limits checked before allocation; parsed in memory-safe code in a sandbox; signed (`nu-provenance.md`) and sealed (MLS or nu-transfer) |
| Smoother | Subdivision surfaces (Catmull–Clark and Loop, OpenSubdiv semantics as in USD) and displacement maps, so curved surfaces come from a small control cage instead of millions of triangles |
| Higher resolution | Textures up to 16,384 × 16,384 per tile and tiled beyond that, 12-bit and HDR emissive; geometry quantisation up to 16 bits per axis or lossless float; optional neural detail on the receiver, display-only |
| Builds on USDZ | The scene model is USD's (prims, transforms, instancing, UsdPreviewSurface and MaterialX materials, UsdSkel, blend shapes, variants), so USDZ round-trips; RealityKit and Reality Composer Pro get a clean USDZ on export |
| GLB for Android and the web | The material and animation model also maps one to one to glTF 2.0 metallic-roughness, skins and morph targets; GLB export uses the standard compression extensions |

## 2. Design rules

These extend R1–R8 in `nu-media-protocol.md` section 3.

| Rule | Statement |
| --- | --- |
| D1 One container | A 3D object is a nu-media object with `profile = scene` (5). There is no second file format, no zip and no sidecar files. Images, video, audio and 3D share the parser, limits, provenance and transport |
| D2 No code | The format has no field for scripts, behaviours, triggers, shader source, custom components or plug-in data. Reality Composer Pro behaviours and timelines, USD Python, glTF `KHR_interactivity` and any shader code are dropped at import, and the import report says so |
| D3 Self-contained | No external references of any kind: no file paths, URLs, asset resolvers, composition arcs or `data:` indirection. Everything the scene needs is a track in the same object. A decoder never opens a file or a connection because of what a scene contains |
| D4 Authoritative geometry | Mesh positions, connectivity, skinning and blend shapes decode bit-exactly on every conforming decoder (integer only, as R5). Subdivision and displacement are evaluated by a specified algorithm, so the limit surface is defined by the file, not by the renderer |
| D5 Neural detail outside the geometry | Receiver-side neural detail (fine surface detail, texture super-resolution) is display-only, like the video enhancement layer (R4). It is never written into the decoded geometry, never used for physics, collision, measurement or 3D printing, never exported, and the viewer can show "decoded only" (R6 applies: no generated texture) |
| D6 No sender decimation | The sender carries the source's full geometry and texture resolution (R1). Coarser levels of detail are extra representations inside the same object, never replacements. Exports to USDZ or GLB may reduce resolution only in the export copy, when the target platform requires it |
| D7 Metadata stripping | Section 8 of `nu-media-protocol.md` applies. In addition: USD `customLayerData`, `documentation` and authoring-tool fields, glTF `asset.generator` and `extras`, FBX creator and file-path fields, original file names, and capture data from Object Capture or RoomPlan beyond the geometry and textures are dropped. A licence and attribution string (for CC BY models) is kept only if the user keeps it, inside the encryption |
| D8 Units and axes | Metres, right-handed, Y up, as glTF and RealityKit. USD stages with other `metersPerUnit` or Z up are converted at import; the conversion is recorded in `scene_bounds` |

## 3. File layout

### 3.1 Tracks

A scene object is a `StreamHeader` with `profile = scene` and these tracks (values proposed in `nu-media-protocol.md` 16.10):

| Track kind | Codec | Contents | Units per object |
| --- | --- | --- | --- |
| `scene` (9) | `nu_scene_v1` (7) | Node hierarchy, transforms, instancing, cameras, lights, material definitions, variant sets, bindings from nodes to meshes and materials | Exactly 1 track |
| `mesh` (10) | `nu_mesh_v1` (8) | Meshes: connectivity, positions, normals, tangents, UV sets, colours, skin weights, blend shapes, subdivision tags; progressive layers | Up to 4,096 meshes |
| `texture` (11) | `nu_image_v1` (4), `ktx2` (11) or `hevc_main10` (1) | Textures: base colour, normal, occlusion-roughness-metallic, emissive, displacement, opacity and others; video textures use HEVC | Up to 1,024 textures |
| `animation` (12) | `nu_anim_v1` (9) | Skeleton definitions and keyframe curves for joints, node transforms, blend-shape weights and material parameters | Up to 256 clips |
| `splat` (13) | `nu_splat_v1` (10) | Gaussian-splat sets (3DGS) | Up to 64 sets |
| `audio` (3) | any nu-audio codec | Spatial audio sources placed in the scene (`design/nu-audio.md`) | One track per source, within the track limit |

The 16-track limit and the 8-bit `track_id` of `nu-media-protocol.md` 4.2 stay as they are. A track carries many **units** (one mesh, one texture, one clip, one splat set), and each `scene_layer` frame (frame type 8, proposed) starts with a small header naming its unit and level:

```
enum { geometry(1), base_colour(2), normal(3), orm(4), emissive(5), displacement(6),
       vector_displacement(7), opacity(8), clip(9), splats(10), (255) } UnitRole;

struct {
  uint32   unit_id;                   // unique within the track
  UnitRole role;
  uint8    level;                     // 0 = coarsest; refinement levels follow in order
  uint8    last_level;                // 1 if no further level of this unit follows
} SceneLayerHeader;                   // first bytes of every scene_layer frame payload
```

So a receiver can fetch, decode and replace each unit and level independently, and provenance covers each one separately (`nu-provenance.md`). Texture units coded with `nu_image_v1` or `ktx2` follow the `SceneLayerHeader` with the codec's own layer data; a texture track uses one codec, so a scene that mixes `nu_image_v1` and `ktx2` textures has two texture tracks. In `profile = scene`, a texture track's `native_width` and `native_height` are the largest unit's, and each texture unit's own size and tile grid follow its `SceneLayerHeader` at level 0.

### 3.2 Scene description (`nu_scene_v1`)

The scene track carries one `scene_layer` frame with a compact binary scene graph:

```
struct {
  uint32 node_count;
  Node   nodes[node_count];          // parents before children; node 0 is the root
  Material materials<V>;
  Camera cameras<V>;
  Light  lights<V>;
  VariantSet variant_sets<V>;
  opaque attribution<V>;             // UTF-8, empty unless the user keeps it (D7)
} SceneDescription;

struct {
  uint32 parent;                      // 0xFFFFFFFF for the root
  opaque name<V>;                     // UTF-8, at most 128 bytes; may be empty
  Transform local;                    // translation, rotation quaternion, scale; or a 4x4 matrix
  uint32 mesh_unit;                   // unit_id in the mesh track, or 0xFFFFFFFF
  uint16 material_bindings<V>;        // index into materials, per mesh subset
  uint16 skeleton;                    // skeleton index in the animation track, or 0xFFFF
  uint8  flags;                       // bit0 instanced (mesh shared), bit1 visible, bit2 casts_shadow
} Node;
```

Materials name their textures by `unit_id` in a texture track.

- **Flattened.** There are no references, payloads, sublayers, inherits or specialisations: the importer composes the USD stage and writes the result (D3). Instancing is kept as shared `mesh_unit` values, so a forest of identical trees costs one tree.
- **Variants** (Reality Composer Pro and AR Quick Look configurators) are kept as a closed set: each `VariantSet` names alternatives, each alternative lists node visibility and material overrides. No variant can add a reference.
- **Names** are optional and short; they are needed for variant UIs and animation targets, and they are inside the encryption.

### 3.3 Geometry (`nu_mesh_v1`)

| Stage | Method |
| --- | --- |
| Quantisation | Positions 11 to 16 bits per axis in the mesh's bounding box (default 14, Draco's common default); normals and tangents octahedral, 8 to 12 bits; UVs 10 to 14 bits in their own range; colours 8 to 12 bits; skin weights 8 bits summing exactly to 255 |
| Connectivity | Edgebreaker-class traversal for manifold regions, with a fallback index codec (meshoptimizer-class) for non-manifold and point or line primitives |
| Prediction | Parallelogram prediction for positions and UVs, octahedral difference for normals, delta coding for blend-shape offsets (sparse: only moved vertices) |
| Entropy coding | Range coder with 16-bit integer CDFs, the same coder as `nu_image_v1` (`nu-media-protocol.md` 6.1). Optional learned context model in integer arithmetic (INT8 weights, INT32 accumulators, as 5.3), identified by `model_id`, so every device decodes the same symbols |
| Progressive levels | A coarse base mesh plus refinement layers (vertex splits in the style of progressive meshes), ordered by screen-space error; each layer is one `scene_layer` frame |
| GPU layout | After decode, the mesh is laid out as meshlets (up to 64 vertices and 124 triangles, Metal mesh-shader friendly) in the order the layers arrived; this is a decoder step, not a format field |
| Lossless | `quantisation_bits = 0` keeps IEEE 754 float32 positions bit-exact with lossless prediction, for CAD, measurement and 3D printing; the frame carries `sample_hash` (ext 6) of the decoded vertex buffer |

Quantisation is part of the authoritative geometry: the decoded, dequantised positions are what every receiver shows and exports (D4). The import report shows the maximum position error in millimetres for the chosen bit depth, so the user can raise it.

### 3.4 Smoother: subdivision and displacement

- **Subdivision surfaces.** A mesh may be flagged as a Catmull–Clark (quads) or Loop (triangles) control cage with creases, corners and boundary interpolation rules, with the same semantics as USD's `subdivisionScheme`, `creaseIndices` and `cornerIndices` and OpenSubdiv's evaluation. The receiver tessellates adaptively to screen size. A smooth character or product can be carried as a cage of a few thousand faces instead of a million triangles.
- **Displacement.** A `texture` track with role `displacement` (scalar, along the limit normal) or `vector_displacement` (tangent space) adds sculpted detail on top of the limit surface, coded in `nu_image_v1` at 12 bits.
- **Defined result.** Tessellation level and displacement are evaluated by a specified algorithm (uniform or feature-adaptive refinement to a level the receiver chooses), so two receivers at the same level produce the same surface up to floating-point rounding. Export bakes the subdivided, displaced surface into ordinary triangles at a level the user picks, because AR Quick Look, Scene Viewer and most web viewers don't evaluate subdivision (RealityKit's runtime support for subdivision is to be checked).

### 3.5 Higher resolution: textures and neural detail

- **Textures.** `nu_image_v1` at 12-bit, 4:4:4, with alpha (`nu-media-protocol.md` 6), tiled with the 4.4 grid above 4,096 px, up to 16,384 × 16,384 per tile and tiled further for virtual texturing. Normal maps are coded as two channels with Z rebuilt on decode; occlusion, roughness and metallic are packed as one three-channel texture (as glTF ORM). Emissive textures may be HDR (PQ).
- **`ktx2` fast path.** For assets where load time matters more than size (large scenes on a Mac, repeated loads), a texture may be carried as KTX 2.0 with Basis Universal UASTC or ETC1S supercompression, which transcodes to ASTC in microseconds per block instead of running a network. The sender chooses per texture.
- **ASTC on the receiver.** `nu_image_v1` textures are decoded on the Neural Engine and compressed to ASTC on the GPU for rendering (TBD-spike: the cost of real-time ASTC encoding per megapixel on A20 Pro, against keeping uncompressed RGBA16F in memory).
- **Video textures** (screens, signage) are `hevc_main10` tracks bound as a material input.
- **Neural detail (display-only).** The receiver MAY run texture super-resolution and a fine-detail normal-map network when the camera is close to a surface. It follows D5: never in the geometry, the export or a screenshot without a label, and off when the sender clears it in `enhancement_hint`.

### 3.6 Materials

One physically based material model that maps without loss to both platforms' standard models:

| `.nu` parameter | UsdPreviewSurface | glTF 2.0 |
| --- | --- | --- |
| Base colour, opacity | `diffuseColor`, `opacity` | `baseColorFactor` and texture, alpha |
| Metallic, roughness | `metallic`, `roughness` | `metallicRoughnessTexture` |
| Normal | `normal` | `normalTexture` |
| Occlusion | `occlusion` | `occlusionTexture` |
| Emissive, strength | `emissiveColor` | `emissiveFactor`, `KHR_materials_emissive_strength` |
| Clearcoat | `clearcoat`, `clearcoatRoughness` | `KHR_materials_clearcoat` |
| Index of refraction | `ior` | `KHR_materials_ior` |
| Transmission, sheen, specular, anisotropy | MaterialX (Reality Composer Pro ShaderGraph, OpenPBR or Standard Surface) | `KHR_materials_transmission`, `_sheen`, `_specular`, `_anisotropy` |
| Alpha mode, cutoff, double-sided | `opacityThreshold`, `doubleSided` | `alphaMode`, `alphaCutoff`, `doubleSided` |

- **MaterialX graphs** from Reality Composer Pro are kept as data: a restricted node set (pure maths, texture reads from tracks in the same object, standard BSDF nodes), at most 256 nodes per material, no file or URL inputs, no custom code nodes. Graphs that use anything else are baked to textures at import.
- **Export fallback.** AR Quick Look reads UsdPreviewSurface only, so USDZ exports always include a UsdPreviewSurface fallback alongside any MaterialX graph.

### 3.7 Animation

- **Skeletal.** Up to 256 joints per skeleton and 8 influences per vertex (exported as 4 when the target requires it, with renormalised weights). Maps to UsdSkel and glTF skins.
- **Blend shapes.** Sparse quantised offsets per target; up to 256 targets per mesh (ARKit's 52 face blend shapes fit). Maps to UsdSkel `BlendShape` and glTF morph targets.
- **Curves.** Keyframes with linear, step or cubic interpolation, quantised (rotations as smallest-three quaternions, 12 to 16 bits), fitted within an error bound at import and coded per track in `nu_anim_v1`. Times use the 1 MHz clock of `nu-media-protocol.md` 4.6.
- **Physics and behaviours** are not carried (D2). Collision shapes may be added later as plain data.

### 3.8 Gaussian splats (`nu_splat_v1`)

- **Contents.** Per splat: position, scale, rotation, opacity, colour and spherical-harmonic coefficients up to degree 3, as in 3D Gaussian Splatting (Kerbl et al., SIGGRAPH 2023).
- **Coding.** SPZ-class quantisation (positions as 24-bit fixed point, log scales 8 bits, rotations as smallest-three 8-bit, SH coefficients 4 to 8 bits), splats sorted along a Morton curve with delta coding, then the integer range coder. Progressive by importance (opacity × projected area), so the first layer shows the scene's shape and colour.
- **Rendering.** Sorted splat rasterisation in Metal; RealityKit has no splat primitive that we know of (to check for iOS and visionOS 26), so the khensu viewer renders splats itself and composites with RealityKit content.
- **Export.** GLB with the Khronos Gaussian-splat extension if ratified (a `KHR_gaussian_splatting` extension was in development in 2025; to check its status), otherwise PLY or SPZ files; USDZ export bakes the splats to a textured mesh (lossy, labelled), because USDZ has no splat type that RealityKit renders (to check OpenUSD's particle-field work).
- **Capture.** Splats trained on the device from a phone capture are later work; v1 carries splats imported from PLY or SPZ.

### 3.9 Spatial audio in scenes

A scene may place `audio` tracks at nodes (point sources with distance attenuation and a cone) or as an ambisonic bed, coded with nu-audio (`design/nu-audio.md`). USDZ export writes `SpatialAudio` prims with M4A (AAC) files; GLB export uses `KHR_audio_emitter` if ratified (to check), otherwise drops audio with a note.

## 4. Progressive delivery

### 4.1 First tick, then refine

On the tick lane (`nu-media-protocol.md` 10.1) a scene is cut into 1,990-byte chunks like any nu-media object, ordered so that every chunk boundary is a usable state:

| Order | Contents | Design target size |
| --- | --- | --- |
| Chunk 0 | Stream header, scene description, a coarse mesh of 200–500 triangles per visible object, one colour per material | at most 1,990 bytes |
| Next | Texture previews (layer 0 of each `nu_image_v1` texture), then mesh refinement layers by screen-space error | a few chunks |
| Then | Full textures, remaining refinement, animation curves, splat layers | the rest |

`TickMediaOffer.layer_ends` marks where each level completes, so the receiver redraws after each one. The preview in chunk 0 is a recognisable silhouette in the right colours, shown on the first tick.

### 4.2 Two worked examples

Every figure is an estimate or design target; section 10 replaces them.

| Asset | Contents | `.nu` design target | Lane and time |
| --- | --- | --- | --- |
| Small object (a sticker, a product, a toy) | 10,000 triangles, 3 textures at 1,024 × 1,024 | about 210 KB: mesh about 18 KB, textures about 190 KB | Tick lane: about 108 chunks, about 36 ticks (about 72 s) complete, silhouette on the first tick |
| Room-scale scan | 1,000,000 triangles, 8 textures at 4,096 × 4,096 | about 10 MB: mesh about 2 MB, textures about 8 MB | Bulk lane (nu-transfer), viewer-driven fetch (4.3) |

### 4.3 Viewer-driven fetch on the bulk lane

Large scenes are a nu-transfer whose payload is the scene object. Like viewport fetch for 360° video (`nu-media-protocol.md` 10.3.4), the receiver fetches the header, scene description and coarse levels first, then the refinement layers and texture tiles for what is near and in view, then the rest. Fetch order is the receiver's choice and nodes see only uniform chunk requests.

## 5. Security

### 5.1 Why 3D files are risky

3D formats are a large, complex parsing surface, and Apple's security notes have repeatedly listed fixes for "processing a maliciously crafted USD file" in Model I/O and related components (specific CVEs to be cited before this is quoted). USD can also compose other files by path or resolver, glTF can point to external URIs, FBX parsers are large native code, and Reality Composer Pro content can carry behaviours. A messenger that opens 3D files from strangers needs the strictest rules of any media type.

### 5.2 Rules

- **Import is the dangerous step.** Importers (OpenUSD, glTF, OBJ, FBX, PLY) run in a separate sandboxed process with no network, no file access beyond the one input, and a memory and time cap. Only the importer touches foreign formats; it emits `.nu`, which the main app parses with the `khensu-core` parser (Rust, memory-safe, fuzzed).
- **Resolve and flatten.** USD references, payloads, sublayers, inherits, specialisations and variant selections are composed inside the package only; any asset path that is absolute, contains `..`, uses a URL scheme or names a file outside the package fails the import. glTF buffers and images must be in the GLB or in `data:` URIs or relative paths inside the same folder; `http(s):` URIs fail the import and are never fetched.
- **Strip.** D2 and D7: behaviours, scripts, custom components, plug-in data and metadata are dropped and listed in the import report.
- **Limits before allocation** (version 1, TBD-spike to tune):

  | Limit | Value |
  | --- | --- |
  | Tracks per scene object | 16 (as every nu-media object) |
  | Units per track | as in 3.1 (4,096 meshes, 1,024 textures, 256 clips, 64 splat sets) |
  | Nodes | 65,536 |
  | Triangles per mesh, after subdivision at the receiver's chosen level | 16,777,216 |
  | Triangles in the scene, decoded | 67,108,864 |
  | Vertices per mesh | 16,777,216 |
  | Texture size | 16,384 × 16,384 per tile; tiled textures up to 65,536 × 65,536 |
  | Subdivision level evaluated | at most 6 |
  | Joints per skeleton, influences per vertex | 256, 8 |
  | Blend-shape targets per mesh | 256 |
  | MaterialX nodes per material | 256 |
  | Splats per object | 16,777,216 |
  | Animation length | 24 hours of curve time |

  A decoder MUST reject an object that exceeds any limit before allocating buffers for it, with `limits_exceeded` (`nu-media-protocol.md` 12.1).
- **Signed and sealed.** Scenes travel sealed like any nu-media object (MLS on the tick lane, nu-transfer on the bulk lane) and carry provenance (`nu-provenance.md`): every mesh, texture, animation and splat layer is a leaf, so a changed byte anywhere is detected before display.
- **Wrapped files are polyglots.** A wrapped USDZ or GLB (7.3) shows one thing in other apps and another in khensu. The `.nu` payload records the hash of the fallback it was written with (`fallback_binding`, ext 14 proposed); if the fallback has been changed, khensu warns that other apps will show something different.

## 6. Import

| Source | Path | Notes |
| --- | --- | --- |
| USDZ, USDA, USDC | OpenUSD in the import sandbox | Composition flattened (5.2); UsdPreviewSurface and MaterialX mapped (3.6); UsdSkel and blend shapes kept; physics and RealityKit components dropped |
| Reality Composer Pro project | Its USDA scenes, or a USDZ exported from Reality Composer Pro | Behaviours, timelines and custom components dropped with a report; ShaderGraph materials mapped or baked (3.6) |
| `.reality` files | Not supported | The format is not documented for third parties; the app asks for a USDZ export |
| GLB, glTF | Our own glTF reader | Draco, meshoptimizer and KTX2 decoded; `KHR_materials_*` mapped; external URIs per 5.2 |
| OBJ with MTL | Our own reader | Only files in the same shared folder; no URLs |
| FBX | `ufbx` (MIT) in the sandbox | The Autodesk FBX SDK's licence needs review before use; FBX import is provisional (question 93) |
| PLY, SPZ | Our own reader | Gaussian splats (3.8) and point clouds |
| STL | Our own reader | Geometry only, lossless mode by default (3D printing) |
| Object Capture, RoomPlan | On-device USDZ output | Already on the device; capture metadata stripped (D7) |

The import report lists what was flattened, baked, dropped and converted, with the geometry error of the chosen quantisation.

## 7. Export and wrapping

All exports run on the user's device; nothing is converted on a server.

### 7.1 USDZ for RealityKit, Reality Composer Pro and AR Quick Look

- **Package.** An uncompressed, unencrypted zip with every file's data starting at a multiple of 64 bytes, a single USDC (crate) root layer first, and textures as PNG (normal, ORM, anything needing exact values) or JPEG (base colour, when the user chooses smaller over exact). These are the USDZ specification's rules; `usdchecker --arkit` must pass on every export (acceptance test in section 10).
- **Content.** Meshes with subdivision and displacement baked (3.4) at a user-chosen level; UsdPreviewSurface on every material, MaterialX kept for RealityKit where present; UsdSkel animation; `SpatialAudio` prims with M4A.
- **Size.** USDZ can't carry compressed geometry or learned textures, so exports are much larger than `.nu` (section 9). Textures larger than the target supports are reduced in the export copy only (D6).

### 7.2 GLB for Android, `<model-viewer>` and the web

- **Container.** glTF 2.0 binary (GLB): JSON chunk, BIN chunk.
- **Compression**, chosen by the user:

  | Option | Geometry | Textures | For |
  | --- | --- | --- | --- |
  | Small | `KHR_draco_mesh_compression` | `KHR_texture_basisu` (KTX2, ETC1S) | Smallest download; Scene Viewer and `<model-viewer>` (Scene Viewer support for each extension to check) |
  | Balanced | `EXT_meshopt_compression` with `KHR_mesh_quantization` | `KHR_texture_basisu` (KTX2, UASTC) | Fast decode, higher texture quality |
  | Compatible | None | PNG and JPEG | Any glTF viewer |

- **Materials** map to metallic-roughness plus the `KHR_materials_*` extensions in 3.6; splats per 3.8.

### 7.3 Wrapped mode: open anywhere, better in khensu

A wrapped file is a valid USDZ or GLB that ordinary apps open normally, with the `.nu` payload inside for khensu apps. The user chooses the fallback's quality: **full** (largest, best for people without khensu) or **light** (a reduced level of detail, smallest wrapped file). A wrapped file is always larger than either the plain export or the `.nu` alone, since it carries both.

**GLB.** The `.nu` payload goes in a third GLB chunk with a new chunk type, after the JSON and BIN chunks. The glTF 2.0 specification requires clients to ignore chunks of unknown type that follow the first two, so viewers render the fallback geometry in JSON and BIN. The JSON declares a vendor extension in `extensionsUsed` (never `extensionsRequired`) that names the chunk, its length and its hash. Naming: Khronos reserves `EXT_` for extensions implemented by more than one vendor and `KHR_` for Khronos, so the extension needs a registered vendor prefix, for example `KHENSU_nu_media` (prefix to request from Khronos; `EXT_khensu_nu` would not be a valid name for a single-vendor extension). Tools that re-export a GLB will usually drop the chunk; khensu then falls back to the GLB content.

**USDZ.** An extra non-USD file in the zip would fail `usdchecker`, whose file-extension rule allows only USD layers, images (PNG, JPEG, EXR, AVIF) and audio (M4A, MP3, WAV), and Reality Composer Pro or AR Quick Look may refuse it. Instead, the payload sits inside the USDC root layer, on an inactive prim that renderers never compose:

```
def Scope "KhensuNu" (
    active = false
)
{
    custom uniform token khensu:nuVersion = "1"
    custom uniform uchar[] khensu:nuPayload = [...]     // the .nu object, bytes as stored
    custom uniform string khensu:nuHash = "..."          // H256 of the payload, hex
}
```

USD allows arbitrary custom attributes and inactive prims, so the file stays valid; khensu reads the attribute with its own crate parser, without composing the stage. Whether Reality Composer Pro preserves an inactive prim when it re-saves a file is to be tested (question 92).

**Binding.** The payload carries `fallback_binding`: the hash of the fallback's geometry and texture bytes as written. khensu checks it on open and shows "other apps will see a different version" if they differ (5.2).

## 8. File extension, UTI and media type

| Item | Proposal | Notes |
| --- | --- | --- |
| Extension | `.nu` for every nu-media object (image, video, audio, 3D), with `.numedia` kept as an alias | The IETF draft (`proposals/draft-staffer-nu-media-00.md`) lists `.numedia` today; the next revision would add `.nu` (question 91) |
| Base UTI | `nu.khensu.nu-media`, conforming to `public.data` and `public.content`; tags `.nu`, `.numedia`, `application/nu-media` | Exported by the khensu app |
| 3D UTI | `nu.khensu.nu-media.scene`, conforming to `nu.khensu.nu-media` and `public.3d-content` | Used for drag and drop and Share sheet filtering; a file's real kind comes from the stream header's profile, since one extension maps to one UTI |
| Media type | `model/nu-media` for `profile = scene`, alongside `application/nu-media` and `video/nu-media` | `model` is the IANA top-level type for 3D (RFC 2077), as used by `model/gltf-binary` and `model/vnd.usdz+zip`; to add to the IETF draft at its next revision |
| Wrapped files | Keep `.usdz` and `.glb` and their standard UTIs and media types | They are ordinary files to everyone else |
| Android | Intent filter on `model/nu-media` and `application/nu-media`; path pattern for `.nu` as a fallback | Android's extension matching is unreliable; sharing to other Android apps uses GLB |

**Existing uses of `.nu`.** `.nu` is the extension of Nushell scripts (`script.nu`, `config.nu`), an established cross-platform shell. On macOS a type conflict only arises if an installed app declares `.nu` as its own type (a Nushell editor or plug-in could), in which case Finder may open the file with that app. Since a `.nu` nu-media file starts with the magic `"nuMe"` and a Nushell script is text, the khensu Quick Look and document handlers can tell them apart by content, but the Finder association can still collide. The Niue country-code domain `.nu` is unrelated: domains and file extensions don't conflict. Other historical uses of `.nu` (to check in file-extension registries) and the conflict with Nushell are question 91.

## 9. Comparison with USDZ and GLB

### 9.1 Features

| | USDZ | GLB | `.nu` |
| --- | --- | --- | --- |
| Geometry compression | None (USDC stores float arrays; some integer arrays are compressed) | Draco or meshoptimizer extensions | Built in (3.3), optional learned context model |
| Texture codecs | PNG, JPEG, EXR, AVIF (AVIF support in RealityKit to check) | PNG, JPEG, KTX2 (Basis), WebP and AVIF by extension | `nu_image_v1` (learned, 12-bit), KTX2, HEVC video textures |
| Progressive loading | No | No (whole file, or streamed by viewers that support it) | Yes, from the first 1,990-byte chunk |
| Subdivision surfaces | Yes (USD); runtime support varies | No | Yes, with specified evaluation (3.4) |
| Gaussian splats | No | Extension in development | Yes (3.8) |
| External references | Composition arcs; package-relative in USDZ | External URIs allowed in `.gltf`; GLB usually self-contained | None, by rule (D3) |
| Executable or behavioural content | Reality Composer behaviours in `.reality`; none in plain USDZ | `KHR_interactivity` (in development) | None, by rule (D2) |
| Encryption and signatures | None in the format | None in the format | Sealed by khensu transport; per-unit provenance signed with ML-DSA-87 |
| Opens in RealityKit, AR Quick Look | Yes | No (Reality Converter imports it) | Via USDZ export or wrapped USDZ |
| Opens on Android and the web | Limited | Yes | Via GLB export or wrapped GLB |

### 9.2 Sizes

The small object and room-scale scan of 4.2. Every figure is an estimate (USDZ, GLB) or a design target (`.nu`).

| Format | Small object (10k triangles, 3 × 1K textures) | Room-scale scan (1M triangles, 8 × 4K textures) |
| --- | --- | --- |
| USDZ, PNG textures | about 4.7 MB | about 230 MB |
| USDZ, JPEG base colour and ORM, PNG normals | about 2.9 MB | about 110 MB |
| GLB, no compression, PNG | about 4.7 MB | about 230 MB |
| GLB, Draco + KTX2 ETC1S | about 0.4 MB (ETC1S texture quality is visibly lower) | about 19 MB |
| GLB, meshoptimizer + KTX2 UASTC | about 1.9 MB | about 75 MB |
| **`.nu`**, design target | **about 0.21 MB** | **about 10 MB** |
| Wrapped GLB (light fallback) | `.nu` plus about 0.3 MB | `.nu` plus about 10 MB |

How these were estimated: raw geometry at 32 bytes per vertex (position, normal, UV) plus 16- or 32-bit indices; PNG textures at about 12 bits per pixel for colour and 16 for normals; Draco at 14-bit positions about 8–10 times smaller than raw; ETC1S about 1 bit per pixel and UASTC with zstd about 4–5; `.nu` geometry about 25% below Draco at the same quantisation, and `nu_image_v1` textures at about 0.25–0.8 bit per pixel depending on the map. At equal rendered quality the fair comparison is with UASTC, not ETC1S. These are the claims section 10 has to test.

**What to expect honestly:** most of the saving comes from textures, where learned coding beats PNG and KTX2 by large factors. Geometry gains over Draco are modest (tens of percent, not multiples) unless subdivision replaces dense triangles. The cost is decode time: `nu_image_v1` textures run a network and an ASTC encode at load, where KTX2 transcodes almost instantly; the `ktx2` option (3.5) exists for that reason.

## 10. Benchmark plan

A planned script, `bench/model3d.py`, with a 3D page in the `bench/ios` NuBench app, measures size, load time and quality for every format in 9.2.

- **Formats.** USDZ written with OpenUSD's `usdzip` and Apple's Reality Converter; GLB with `gltf-transform` (MIT) for Draco, meshoptimizer and KTX2 (`toktx` from KTX-Software, Apache-2.0); `.nu` from the khensu encoder once it exists.
- **Measurements.**
  - Size in bytes and in tick chunks.
  - Load time on iPhone (NuBench): RealityKit `Entity(contentsOf:)` for USDZ, from file open to first rendered frame; the `.nu` decoder from first chunk to first frame and to full quality; energy with MetricKit.
  - Load time on Android (Pixel-class phone): Scene Viewer by stopwatch on screen capture, `<model-viewer>` in Chrome with performance marks.
  - Geometry error: symmetric Hausdorff and RMS distance against the source mesh (`trimesh`, MIT), in millimetres.
  - Rendered quality: NVIDIA FLIP (BSD-3-Clause) and PSNR on renders from 12 fixed cameras under fixed lighting, per format.
  - Validity: `usdchecker --arkit` on every USDZ, the Khronos glTF Validator on every GLB, both on wrapped files.
- **Content and licences.**

  | Set | Licence | Use |
  | --- | --- | --- |
  | Khronos glTF Sample Assets | Per model (many CC0 or CC BY 4.0; some carry trademark terms); check each model's licence file | Main set, publishable results where the licence allows |
  | Apple AR Quick Look gallery USDZ models | Apple's terms; not an open licence | Private benchmarking only; no redistribution or public images without permission |
  | Stanford 3D Scanning Repository (Bunny, Dragon, Lucy) | Free for research, with conditions per model | Dense scanned geometry |
  | Poly Haven models | CC0 | Textured PBR assets |
  | Smithsonian 3D (CC0 subset) | CC0 where marked | Photogrammetry scans |
  | Gaussian-splat scenes (Mip-NeRF 360 and similar) | To check per scene | Splat coding |
  | Our own Object Capture and RoomPlan captures | Ours | Real phone content |

- **Pass criteria (design targets):** at equal FLIP score, `.nu` is at most half the size of GLB with meshoptimizer and KTX2 UASTC; the first chunk shows a recognisable preview; `.nu` reaches full quality on iPhone 18 Pro no slower than RealityKit loads the equivalent USDZ; every export passes its validator.

Measured results go here, with the device, OS build and commit of each run.

## 11. Patent notes

For `PATENTS.md` (design only, not built; assess before publishing). Prior art to compare against: Draco and Edgebreaker (Rossignac, 1999), progressive meshes (Hoppe, 1996), meshoptimizer, MPEG mesh and point-cloud coding (V-DMC, ISO/IEC 23090-29; V-PCC and G-PCC, with patent pools that need a freedom-to-operate check before any MPEG-like tool is used), SPZ and other splat compressors, OpenSubdiv, glTF and USD extensions, KTX2 and Basis Universal. Candidate novelty for counsel:

1. Progressive 3D delivery inside constant-rate cover traffic, with a usable silhouette in the first fixed-size chunk.
2. A dual-payload wrapped USDZ or GLB whose native payload records a binding to the fallback, so the reader detects divergence between what other apps and the native app show.
3. Receiver-side neural surface detail kept outside an authoritative, bit-exact geometry that governs export, physics and measurement.

## 12. Open questions

1. **Extension and type conflicts** (question 91): keep `.nu` despite Nushell, or use `.numedia` or another extension as the registered default.
2. **Wrapped USDZ survival** (question 92): does Reality Composer Pro keep the inactive `KhensuNu` prim when it re-saves, and does AR Quick Look load a USDZ with a multi-megabyte custom attribute without slowing down?
3. **FBX** (question 93): ship FBX import with `ufbx`, or leave FBX to desktop tools that export USDZ or glTF.
4. **Splats in Apple's stack** (question 94): whether RealityKit or OpenUSD gains a splat primitive, which would change the USDZ export.
5. **Learned geometry** (question 95): whether a learned integer context model for meshes gains enough over the hand-designed coder to justify a model per device generation.
6. **Web viewer** (question 96): a WebAssembly build of the `khensu-core` decoder so `.nu` opens in browsers without a GLB copy, and whether that conflicts with keeping all decoding inside the sandboxed native app.
7. **Collision shapes and simple physics** as plain data in a later version.
