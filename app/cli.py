import asyncio
import random
from dataclasses import dataclass
from typing import Dict, Optional

from app import database as db
from app.config import DEFAULT_LANG, NEXTDNS_KEY, NUM_WORKERS, T, TOKEN_SETS
from app.services import locket, nextdns


@dataclass
class RequestItem:
    request_id: int
    username: str
    uid: str


class LocalActivatorApp:
    """Local orchestrator + CLI replacing Telegram bot transport."""

    def __init__(self) -> None:
        self.queue: asyncio.Queue[RequestItem] = asyncio.Queue()
        self.pending: list[RequestItem] = []
        self.pending_lock = asyncio.Lock()
        self.lang = DEFAULT_LANG
        self.running = True
        self.request_counter = 0

    async def start_workers(self) -> None:
        for i in range(NUM_WORKERS):
            asyncio.create_task(self.worker(i + 1))

    async def worker(self, worker_id: int) -> None:
        while self.running:
            item = await self.queue.get()
            async with self.pending_lock:
                self.pending = [x for x in self.pending if x.request_id != item.request_id]

            print(T("processing", self.lang).format(item.username))
            token_config = random.choice(TOKEN_SETS)

            def log_line(msg: str) -> None:
                print(f"[Worker-{worker_id}] {msg}")

            ok, detail = await locket.inject_gold(item.uid, token_config, log_callback=log_line)
            db.log_request(0, item.uid, "SUCCESS" if ok else detail)

            if ok:
                print(T("generating_dns", self.lang))
                _, dns_link = await nextdns.create_profile(NEXTDNS_KEY, log_callback=log_line)
                if dns_link:
                    print(T("success_title", self.lang))
                    print(T("dns_msg", self.lang).format(dns_link, dns_link.split("=")[-1]))
                else:
                    print("Activated Gold but could not generate NextDNS profile.")
            else:
                print(T("fail_title", self.lang), detail)

            self.queue.task_done()

    async def enqueue_username(self, username: str) -> None:
        print(T("resolving", self.lang))
        uid = await locket.resolve_uid(username)
        if not uid:
            print(T("not_found", self.lang))
            return

        print(T("checking_status", self.lang))
        status = await locket.check_status(uid)
        if status and status.get("active"):
            print(T("gold_active", self.lang).format(status.get("expires")))

        self.request_counter += 1
        item = RequestItem(request_id=self.request_counter, username=username, uid=uid)

        async with self.pending_lock:
            self.pending.append(item)
            pos = len(self.pending)

        await self.queue.put(item)
        print(T("queued", self.lang).format(username, pos, pos - 1))

    def show_help(self) -> None:
        print(
            """
Commands:
  activate <username_or_locket_link>  Queue activation
  stats                               Show local statistics
  setlang <VI|EN>                     Switch language
  queue                               Show queue status
  help                                Show this help
  exit                                Quit app
""".strip()
        )

    async def repl(self) -> None:
        print("=== Locket Gold Local Activator ===")
        self.show_help()

        while self.running:
            raw = await asyncio.to_thread(input, "\nlocket> ")
            cmd = raw.strip()
            if not cmd:
                continue

            if cmd in {"exit", "quit"}:
                self.running = False
                break
            if cmd == "help":
                self.show_help()
                continue
            if cmd == "stats":
                print(db.get_stats())
                continue
            if cmd == "queue":
                async with self.pending_lock:
                    if not self.pending:
                        print("Queue empty")
                    else:
                        for i, p in enumerate(self.pending, start=1):
                            print(f"#{i}: {p.username} ({p.uid})")
                continue
            if cmd.startswith("setlang "):
                lang = cmd.split(" ", 1)[1].strip().upper()
                if lang in {"VI", "EN"}:
                    self.lang = lang
                    print(T("lang_set", self.lang))
                else:
                    print("Language must be VI or EN")
                continue
            if cmd.startswith("activate "):
                value = cmd.split(" ", 1)[1].strip()
                if "locket.cam/" in value:
                    value = value.split("locket.cam/")[-1].split("?")[0]
                await self.enqueue_username(value)
                continue

            print("Unknown command. Type: help")


async def run_cli_app() -> None:
    app = LocalActivatorApp()
    await app.start_workers()
    await app.repl()
