"""Engine benchmarks for main.py (CPython, graphics stand-ins).

Measures the cost of the program logic only: no browser, no drawing.
In-browser timing is recorded separately in results/browser_measurements.json.

Usage:  python eval/benchmark.py
"""
import json
import os
import platform
import statistics
import sys
import time
import timeit
import tracemalloc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
from stubs import MAIN_PATH, load_game  # noqa: E402

OUT = os.path.join(ROOT, "eval", "results", "benchmark.json")


def percentile(sorted_values, p):
    return sorted_values[min(len(sorted_values) - 1, int(p * len(sorted_values)))]


def summarise(nanoseconds):
    values = sorted(n / 1000.0 for n in nanoseconds)      # microseconds
    return {
        "n": len(values),
        "mean_us": round(statistics.fmean(values), 3),
        "median_us": round(statistics.median(values), 3),
        "p95_us": round(percentile(values, 0.95), 3),
        "p99_us": round(percentile(values, 0.99), 3),
        "max_us": round(values[-1], 3),
    }


def bench_decision(game, calls=1_000_000):
    """nextDifficulty() alone, over a spread of realistic inputs."""
    cases = [(t, s, m, sec, e)
             for t in (1, 2, 3) for s in (0, 1, 3) for m in (0, 2)
             for sec in (2.0, 8.0, 20.0) for e in (0, 1, 2)]
    fn = game.nextDifficulty
    loops = calls // len(cases)
    seconds = timeit.timeit(lambda: [fn(*c) for c in cases], number=loops)
    return {"calls": loops * len(cases),
            "mean_ns_per_call": round(seconds / (loops * len(cases)) * 1e9, 1)}


def bench_answer_cycle(game, cycles=200_000):
    """One correct key press: onKeyPress -> applyDDA -> loadScenario."""
    app, press, clock = game.app, game.onKeyPress, time.perf_counter_ns
    samples = []
    for i in range(cycles):
        app.timeTicks = (i * 37) % 200            # 0 to 19.9 s on the question
        app.globalTimeTicks = 0
        key = app.correctKey
        start = clock()
        press(key)
        samples.append(clock() - start)
    stats = summarise(samples)
    stats["throughput_per_s"] = round(1e6 / stats["mean_us"])
    return stats


def bench_step(game, ticks=200_000):
    """One clock tick: onStep()."""
    app, step, clock = game.app, game.onStep, time.perf_counter_ns
    samples = []
    for _ in range(ticks):
        app.globalTimeTicks = 0
        start = clock()
        step()
        samples.append(clock() - start)
    return summarise(samples)


def bench_load(repeats=200):
    """Compile and execute main.py from source (program start-up)."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        load_game(seed=1)
        samples.append(time.perf_counter_ns() - start)
    values = sorted(s / 1e6 for s in samples)
    return {"n": repeats, "median_ms": round(statistics.median(values), 3),
            "p95_ms": round(percentile(values, 0.95), 3)}


def bench_memory():
    """Python heap used by main.py: while loading, once loaded, and in play."""
    tracemalloc.start()
    game = load_game(seed=1)
    after_load, load_peak = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()
    app = game.app
    while not app.isGameOver:
        for _ in range(60):                       # 6 s per question
            game.onStep()
        if not app.isGameOver:
            game.onKeyPress(app.correctKey)
    after_session, session_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"load_peak_kib": round(load_peak / 1024, 1),
            "after_load_kib": round(after_load / 1024, 1),
            "session_peak_kib": round(session_peak / 1024, 1),
            "after_session_kib": round(after_session / 1024, 1),
            "source_bytes": os.path.getsize(MAIN_PATH),
            "questions_in_session": app.totalQuestions}


def main():
    game = load_game(seed=6)
    results = {
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": f"{platform.system()} {platform.machine()}",
            "note": "CPython with graphics stand-ins; excludes browser drawing",
        },
        "decision": bench_decision(game),
        "answer_cycle": bench_answer_cycle(game),
        "step": bench_step(game),
        "load": bench_load(),
        "memory": bench_memory(),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    env, d, a, s = results["environment"], results["decision"], results["answer_cycle"], results["step"]
    ld, m = results["load"], results["memory"]
    print("Dynamic CS Vocabulary Engine - engine benchmark")
    print(f"  {env['implementation']} {env['python']} on {env['system']} ({env['note']})")
    print()
    print(f"  nextDifficulty()            {d['mean_ns_per_call']:>9.1f} ns mean   ({d['calls']:,} calls)")
    print(f"  answer cycle (key -> next)  {a['median_us']:>9.3f} us median  p95 {a['p95_us']:.3f}  "
          f"p99 {a['p99_us']:.3f}  max {a['max_us']:.1f}  (n={a['n']:,})")
    print(f"  answer-cycle throughput     {a['throughput_per_s']:>9,} per second")
    print(f"  onStep() tick               {s['median_us']:>9.3f} us median  p95 {s['p95_us']:.3f}  "
          f"p99 {s['p99_us']:.3f}  max {s['max_us']:.1f}  (n={s['n']:,})")
    print(f"  load main.py                {ld['median_ms']:>9.3f} ms median  p95 {ld['p95_ms']:.3f}  (n={ld['n']})")
    print(f"  peak heap while loading     {m['load_peak_kib']:>9.1f} KiB   (compiling the source)")
    print(f"  heap held after load        {m['after_load_kib']:>9.1f} KiB")
    print(f"  peak heap, full session     {m['session_peak_kib']:>9.1f} KiB   ({m['questions_in_session']} questions, "
          f"{m['after_session_kib']:.1f} KiB at the end)")
    print(f"  main.py source size         {m['source_bytes']:>9,} bytes")
    print()
    print(f"  NFR: a decision in under 1 s. Slowest answer cycle observed: {a['max_us'] / 1000:.3f} ms")
    print(f"  results written to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
