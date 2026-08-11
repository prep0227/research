"""Real-robot latency timestamp hooks (template).

Insert calls at the six measurement points in your auto-aim pipeline.
All timestamps use time.monotonic_ns(); write one JSON event per line to a file.
Adjust to your framework (camera SDK / detect / PnP / serial / MCU status).

Example usage (adapt):
    from record_timestamps import EventLogger
    log = EventLogger("events.jsonl")
    ...
    log.event("cam_exposure_mid", info={"frame_id": i})     # camera callback
    log.event("proc_enter", info={"frame_id": i})           # pipeline start
    log.event("proc_exit", info={"frame_id": i, "det": ..., "solve": ...})
    log.event("serial_send", info={"cmd": ...})
    # MCU status packet received:
    log.event("mcu_recv", info={"cmd_time_ns": ..., "settle_time_ns": ...})
    log.event("fire_cmd", info={})
    log.event("fire_trigger", info={})   # optional optical/acoustic sensor
"""
import json, time

class EventLogger:
    def __init__(self, path):
        self.path = path
        self.f = open(path, "a", encoding="utf-8")

    def event(self, name, info=None, ts_ns=None):
        rec = {"ts_ns": int(ts_ns) if ts_ns is not None else time.monotonic_ns(),
               "name": name, "info": info or {}}
        self.f.write(json.dumps(rec) + "\n")
        self.f.flush()

    def close(self):
        self.f.close()

# --- MCU-side (C) pseudo-code for gimbal settle detection ---
MCU_PSEUDO = r"""
// In the MCU control loop (e.g., 1 kHz):
// 1) on receiving a gimbal command packet: record cmd_recv_time = now();
// 2) maintain settle flag: |cmd_target - encoder_angle| < eps for N consecutive
//    control cycles (e.g., N=5 @ 1kHz) -> settle_time = now();
// 3) include cmd_recv_time and settle_time in the next status packet to host.
// The host logs: mcu_recv with cmd_time_ns, settle_time_ns -> tau_gimbal = settle - cmd_recv.
"""

if __name__ == "__main__":
    print(__doc__)
    print(MCU_PSEUDO)
