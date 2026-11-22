import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main() -> int:
    environment = os.environ.copy()
    backend_path = str(ROOT / "backend")
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (backend_path, existing_python_path) if part
    )

    subprocess.run(
        [sys.executable, "scripts/seed_dashboard.py"],
        cwd=ROOT,
        env=environment,
        check=True,
    )

    port = os.environ.get("PORT", "8000")
    web = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ],
        cwd=ROOT,
        env=environment,
    )
    processes = [web]

    token_configured = bool(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip())
    bot = None
    if token_configured:
        bot = subprocess.Popen(
            [sys.executable, "bot/telegram_bot.py"],
            cwd=ROOT,
            env=environment,
        )
        processes.append(bot)
    else:
        print("TELEGRAM_BOT_TOKEN is not set; starting the website without the bot.", flush=True)

    restart_delay = 5
    restart_at = None

    def handle_shutdown(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        while True:
            web_exit_code = web.poll()
            if web_exit_code is not None:
                return web_exit_code or 1

            if bot is not None:
                bot_exit_code = bot.poll()
                if bot_exit_code is not None:
                    print(
                        f"Telegram bot exited with code {bot_exit_code}; "
                        f"restarting in {restart_delay} seconds.",
                        flush=True,
                    )
                    processes.remove(bot)
                    bot = None
                    restart_at = time.monotonic() + restart_delay
                    restart_delay = min(restart_delay * 2, 60)
            elif token_configured and restart_at is not None and time.monotonic() >= restart_at:
                bot = subprocess.Popen(
                    [sys.executable, "bot/telegram_bot.py"],
                    cwd=ROOT,
                    env=environment,
                )
                processes.append(bot)

            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
