# Calls: Picture in Picture and Live Activities

Status: built in `khensu-apple` (iOS). System PiP shows **remote and local** video together; the Live Activity shows **live duration** from the connected timestamp.

## Picture in Picture

- API: `AVPictureInPictureVideoCallViewController` + `AVPictureInPictureController.ContentSource` video-call source (`App/Calls/CallPiP.swift`).
- PiP window contents: remote `AVSampleBufferDisplayLayer` full bleed; local `AVCaptureVideoPreviewLayer` in the bottom-trailing corner (hidden for live viewers with no camera).
- Automatic start when leaving the app (`canStartPictureInPictureAutomaticallyFromInline`).
- Manual start from the call chrome (picture-in-picture control).
- Camera capture may continue while backgrounded under the video-call PiP path; `UIBackgroundModes` includes `audio`.

## Live Activity

- Attributes: `CallActivityAttributes` (`startedAt`, mode, local name) + content state (peer name, mute, cameras, viewer count, safety code).
- Duration: `Text(startedAt, style: .timer)` on the Lock Screen and Dynamic Island — no push updates required for the clock.
- Widget extension: `CallActivity` (`nu.khensu.ptah.call-activity`), `NSSupportsLiveActivities` on the app and the extension.
- Started when the session reaches `.connected`; updated on mute / camera / peer / viewer changes; ended on teardown.

## Out of scope here

- CallKit / PushKit incoming UI (separate PLAN item).
- macOS PiP (iOS video-call PiP API only).
