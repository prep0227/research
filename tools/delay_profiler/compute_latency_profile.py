"""Compute latency profile (mean/std/p50/p95/p99) per segment from events.jsonl.

Usage: python3 compute_latency_profile.py events.jsonl [out.yaml]
Events are paired by info['frame_id'] or info['cmd_id'] (see pairing rules below).
"""
import json, sys, collections
import numpy as np

def load_events(path):
    evs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            evs.append(json.loads(line))
    return evs

def segment_deltas(evs, start_names, end_names, key_field="frame_id"):
    """Pair start/end events by key_field (or by order if None)."""
    starts = collections.defaultdict(dict)
    deltas = []
    for e in evs:
        if e["name"] in start_names:
            k = e["info"].get(key_field) if key_field else None
            starts[e["name"]][k] = e["ts_ns"]
        elif e["name"] in end_names:
            k = e["info"].get(key_field) if key_field else None
            for sname in start_names:
                if k in starts.get(sname, {}):
                    deltas.append((e["ts_ns"] - starts[sname][k]) / 1e9)
                    break
    return deltas

def summarize(name, deltas):
    if not deltas:
        return {"segment": name, "n": 0}
    d = np.asarray(deltas) * 1e3  # ms
    return {"segment": name, "n": len(deltas),
            "mean_ms": float(d.mean()), "std_ms": float(d.std(ddof=1)),
            "p50_ms": float(np.percentile(d, 50)), "p95_ms": float(np.percentile(d, 95)),
            "p99_ms": float(np.percentile(d, 99))}

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    evs = load_events(sys.argv[1])
    out_path = sys.argv[2] if len(sys.argv) > 2 else "latency_profile.yaml"

    cam = segment_deltas(evs, ["cam_exposure_mid"], ["cam_arrived"], key_field="frame_id")
    proc = segment_deltas(evs, ["proc_enter"], ["proc_exit"], key_field="frame_id")
    serial = segment_deltas(evs, ["serial_send"], ["mcu_recv"], key_field="cmd_id")
    gimbal = segment_deltas(evs, ["mcu_recv"], ["gimbal_settle"], key_field="cmd_id")
    fire = segment_deltas(evs, ["fire_cmd"], ["fire_trigger"], key_field="cmd_id")

    segs = [summarize("cam", cam), summarize("proc", proc), summarize("serial", serial),
            summarize("gimbal", gimbal), summarize("fire", fire)]
    lines = ["# Latency profile (auto-generated)", ""]
    for s in segs:
        lines.append(f"{s['segment']}:\n" + "\n".join(f"  {k}: {v}" for k, v in s.items() if k != "segment"))
        lines.append("")
    # sim-compatible summary
    vision = next((s for s in segs if s["segment"]=="cam"), None)
    g = next((s for s in segs if s["segment"]=="gimbal"), None)
    lines.append("# Sim/DelayPair-compatible fields (seconds)")
    lines.append(f"vision_mean: {vision['mean_ms']/1e3 if vision and vision['n'] else 0.03:.4f}")
    lines.append(f"vision_p95:  {vision['p95_ms']/1e3 if vision and vision['n'] else 0.045:.4f}")
    lines.append(f"gimbal_mean: {g['mean_ms']/1e3 if g and g['n'] else 0.06:.4f}")
    lines.append(f"gimbal_p95:  {g['p95_ms']/1e3 if g and g['n'] else 0.09:.4f}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
