#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
PoE2 character downloader (Mac-friendly OAuth).

This is a faithful port of PathOfBuilding-PoE2's OAuth import
(src/Classes/PoEAPI.lua + src/LaunchServer.lua), adapted so it runs on macOS
without the Windows PoB runtime:

  * PoB's `OpenURL(...)`          -> webbrowser.open (uses `open` on macOS)
  * PoB's lua `socket` subscript  -> Python http.server on localhost

Everything else is ported verbatim: the OAuth endpoints, client_id=pob, the
scopes, PKCE (S256), the 49082-49084 redirect ports, the token-refresh logic,
and the API paths (api.pathofexile.com/character/poe2[/<name>]).

Login happens ONCE in the browser; the refresh token is saved locally and
future runs refresh silently — no cookie, no per-request copying.

Usage:
    uv run python poe2_import.py                 # list your PoE2 characters
    uv run python poe2_import.py <CharacterName>  # download one character
    uv run python poe2_import.py --logout         # forget saved tokens

Output (for <CharacterName>): a JSON normalized into the same shape the legacy
importer produced, so build_expander_poe2.py consumes it unchanged:
    PathOfBuilding-PoE2/tools/<CharacterName>_YYYYMMDDHHMM.json
plus the raw API response alongside it as *_raw.json for debugging.
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime

# --- Ported constants (PoEAPI.lua) ---
AUTH_URL = "https://www.pathofexile.com/oauth/authorize"
TOKEN_URL = "https://www.pathofexile.com/oauth/token"
API_BASE = "https://api.pathofexile.com"
CLIENT_ID = "pob"
SCOPES = ["account:profile", "account:leagues", "account:characters", "account:trade"]
REALM = "poe2"  # PoB-PoE2 uses realm code "poe2"; the authenticated account decides which chars come back
REDIRECT_PORTS = [49082, 49083, 49084]
# GGG's API policy requires a descriptive User-Agent, else requests are rejected.
USER_AGENT = "OAuth pob/2.0 (contact: poe2-mac-harness) StrictMode"

TOOLS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "PathOfBuilding-PoE2", "tools"
)
TOKEN_FILE = os.path.join(TOOLS_DIR, ".poe2_token.json")

# Success/failure page shown in the browser after redirect (from LaunchServer.lua).
_HTML_HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>PoB 2 - Authentication</title><style>
body{font-family:Arial,sans-serif;background:#121212;color:#fff;display:flex;
justify-content:center;align-items:center;height:100vh;margin:0}
.card{background:#1E1E1E;padding:20px;border-radius:10px;text-align:center;max-width:400px}
.card h1{color:#4CAF50}</style></head><body><div class="card">"""
_HTML_TAIL = "</div></body></html>"
_HTML_OK = _HTML_HEAD + "<h1>Authentication Successful</h1><p>You can return to the terminal.</p>" + _HTML_TAIL
_HTML_FAIL = _HTML_HEAD + "<h1>Authentication Failed</h1><p>Please try again.</p>" + _HTML_TAIL


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


# ---------------------------------------------------------------- token store
def _load_token() -> dict | None:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return None


def _save_token(tok: dict) -> None:
    os.makedirs(TOOLS_DIR, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tok, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)


def _post_form(url: str, fields: dict) -> dict:
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


# ---------------------------------------------------------- OAuth authorize
class _RedirectHandler(http.server.BaseHTTPRequestHandler):
    captured: dict = {}

    def do_GET(self):  # noqa: N802
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        code = params.get("code", [None])[0]
        ok = code is not None
        _RedirectHandler.captured = {
            "code": code,
            "state": params.get("state", [None])[0],
            "error": params.get("error", [None])[0],
        }
        page = (_HTML_OK if ok else _HTML_FAIL).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, *args):  # silence
        pass


def _authorize() -> dict:
    """Run the one-time browser OAuth flow, return a token dict."""
    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    state = secrets.token_hex(8)  # 16 hex chars, matching PoB

    # Bind the redirect server first so we know the port (LaunchServer.lua order).
    httpd = None
    for port in REDIRECT_PORTS:
        try:
            httpd = http.server.HTTPServer(("localhost", port), _RedirectHandler)
            break
        except OSError:
            continue
    if httpd is None:
        raise SystemExit(f"Could not bind any redirect port in {REDIRECT_PORTS}")
    port = httpd.server_address[1]
    redirect_uri = f"http://localhost:{port}"

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "redirect_uri": redirect_uri,
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    print("Opening browser to log in to pathofexile.com ...")
    print(f"If it doesn't open, visit:\n{url}\n")
    webbrowser.open(url)

    # Wait up to 30s for the redirect (LaunchServer.lua behaviour), ignoring
    # spurious connections that carry no OAuth code.
    _RedirectHandler.captured = {}
    httpd.timeout = 1
    deadline = time.time() + 30
    while time.time() < deadline and not _RedirectHandler.captured.get("code"):
        httpd.handle_request()
        if _RedirectHandler.captured.get("error"):
            break
    httpd.server_close()

    cap = _RedirectHandler.captured
    if not cap.get("code"):
        raise SystemExit(f"OAuth failed: {cap.get('error') or 'timeout waiting for redirect'}")
    if cap.get("state") != state:
        raise SystemExit("OAuth state mismatch — aborting")

    resp = _post_form(TOKEN_URL, {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "code": cap["code"],
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "code_verifier": verifier,
    })
    tok = {
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token"),
        "expiry": time.time() + resp.get("expires_in", 0),
    }
    _save_token(tok)
    print("Logged in. Token saved for future runs.")
    return tok


def _refresh(tok: dict) -> dict:
    print("Refreshing access token ...")
    resp = _post_form(TOKEN_URL, {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": tok["refresh_token"],
    })
    tok = {
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token", tok["refresh_token"]),
        "expiry": time.time() + resp.get("expires_in", 0),
    }
    _save_token(tok)
    return tok


def get_valid_token() -> dict:
    tok = _load_token()
    if not tok:
        return _authorize()
    if tok.get("expiry", 0) < time.time() + 30:
        if tok.get("refresh_token"):
            try:
                return _refresh(tok)
            except Exception as e:  # refresh failed -> full re-auth
                print(f"Refresh failed ({e}); re-authorizing.")
                return _authorize()
        return _authorize()
    return tok


# ------------------------------------------------------------------- API
def _api_get(endpoint: str, tok: dict) -> dict:
    req = urllib.request.Request(
        API_BASE + endpoint,
        headers={
            "Authorization": "Bearer " + tok["access_token"],
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _char_path(name: str | None) -> str:
    # PoEAPI.lua: "/character" .. (realm=="pc" and "" or "/"..realm) .. optional "/"..name
    base = "/character" + ("" if REALM == "pc" else "/" + REALM)
    return base + ("/" + urllib.parse.quote(name) if name else "")


def list_characters(tok: dict) -> list:
    data = _api_get(_char_path(None), tok)
    return data.get("characters", data if isinstance(data, list) else [])


def normalize(raw: dict) -> dict:
    """Map the OAuth /character/poe2/<name> response into the legacy shape that
    build_expander_poe2.py expects (character / passive_tree / items.items)."""
    char = raw.get("character", raw)
    passives = char.get("passives", {}) or {}
    # Tree-socketed jewels: OAuth returns them under character.jewels.
    passive_tree = dict(passives)
    passive_tree.setdefault("items", char.get("jewels", []) or [])
    equipment = (char.get("equipment", []) or []) + (char.get("inventory", []) or [])
    return {
        "character": {
            "name": char.get("name"),
            "class": char.get("class"),
            "ascendancyClass": char.get("ascendancy") or char.get("ascendancyClass"),
            "level": char.get("level"),
            "league": char.get("league"),
            "realm": char.get("realm", REALM),
            "experience": char.get("experience"),
        },
        "passive_tree": passive_tree,
        "items": {"items": equipment},
        # PoE2 skill gems live in character.skills (main skill + socketed supports),
        # NOT in item sockets (those hold runes). Carry them through for the expander.
        "skills_raw": char.get("skills", []) or [],
    }


def main():
    ap = argparse.ArgumentParser(description="Download a PoE2 character via OAuth (Mac).")
    ap.add_argument("character", nargs="?", help="Character name (omit to list characters)")
    ap.add_argument("--logout", action="store_true", help="Delete saved tokens and exit")
    args = ap.parse_args()

    if args.logout:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            print("Logged out (token deleted).")
        else:
            print("No saved token.")
        return

    tok = get_valid_token()

    if not args.character:
        chars = list_characters(tok)
        if not chars:
            print("No PoE2 characters found for this account.")
            return
        print(f"\n{len(chars)} PoE2 character(s):")
        for c in chars:
            print(f"  {c.get('name'):24} L{c.get('level', '?'):<4} {c.get('class', '?'):16} {c.get('league', '')}")
        print("\nRun again with a character name to download it.")
        return

    print(f"Downloading '{args.character}' ...")
    raw = _api_get(_char_path(args.character), tok)

    os.makedirs(TOOLS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M")
    base = os.path.join(TOOLS_DIR, f"{args.character}_{ts}")
    with open(base + "_raw.json", "w") as f:
        json.dump(raw, f, indent=2)
    normalized = normalize(raw)
    with open(base + ".json", "w") as f:
        json.dump(normalized, f, indent=2)

    ch = normalized["character"]
    print(f"Saved: {base}.json")
    print(f"  {ch.get('name')}  L{ch.get('level')}  {ch.get('class')}  {ch.get('league')}")
    print(f"  passive hashes: {len(normalized['passive_tree'].get('hashes', []))}  "
          f"items: {len(normalized['items']['items'])}")
    print(f"\nNext: uv run python build_expander_poe2.py {base}.json")


if __name__ == "__main__":
    main()
