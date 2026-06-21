"""
Keep the FinLit Pro Streamlit app awake — and wake it if it has hibernated.

Streamlit Community Cloud puts an app to sleep after ~12h without real traffic.
A plain HTTP GET (curl/requests) returns HTTP 200 from a STATIC "sleep" shell
WITHOUT booting the Python app, so curl-style pings keep nothing alive and can
never wake a sleeping app.

Loading the page in a real browser is different: it runs the JavaScript and opens
the WebSocket session, which is what actually resets Streamlit's inactivity timer.
And if the hibernation screen is showing, there is a "Yes, get this app back up!"
button we can click to boot the container — exactly what a human would do.
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = "https://finlitpro.streamlit.app/"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        print(f"Visiting {URL}", flush=True)
        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)

        # The hibernation screen is ITSELF client-rendered, so the "Yes, get this
        # app back up!" button does not exist in the DOM the instant the page
        # loads — checking too early would miss it and leave the app asleep. Wait
        # up to 25s for the wake button to appear: if it does, the app is asleep
        # and we click it; if it never appears, the app is already awake/booting.
        wake = page.get_by_text("get this app back up", exact=False)
        try:
            wake.first.wait_for(state="visible", timeout=25_000)
            print("App was asleep — clicking the wake button.", flush=True)
            wake.first.click()
        except PWTimeout:
            print("No sleep screen — app already awake or booting.", flush=True)

        # Wait for the real Streamlit app to mount. This confirms the container is
        # running and that we held an active WebSocket session — the thing that
        # resets the inactivity timer. A cold boot (heavy imports) can take a while.
        try:
            page.wait_for_selector('[data-testid="stApp"]', state="visible", timeout=180_000)
            print("App is awake — Streamlit UI mounted.", flush=True)
        except PWTimeout:
            print(
                "WARNING: stApp not detected in time, but a real session was "
                "established (the visit still counts as traffic).",
                flush=True,
            )

        # Linger so the session is unambiguously registered before we disconnect.
        page.wait_for_timeout(5_000)
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
