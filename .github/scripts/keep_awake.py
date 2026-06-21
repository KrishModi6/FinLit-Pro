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

        # If the hibernation screen is up, click the wake button. Try the precise
        # button role first, then a looser text match in case the wording shifts.
        clicked = False
        for locator in (
            page.get_by_role("button", name="Yes, get this app back up!"),
            page.get_by_text("get this app back up", exact=False),
        ):
            try:
                if locator.count() > 0:
                    locator.first.click(timeout=10_000)
                    clicked = True
                    print("App was asleep — clicked the wake button.", flush=True)
                    break
            except PWTimeout:
                pass

        if not clicked:
            print("No sleep screen detected (app already awake or booting).", flush=True)

        # Wait for the real Streamlit app to mount. This confirms the container is
        # running and that we held an active WebSocket session — the thing that
        # resets the inactivity timer. Booting from cold can take ~1-2 min.
        try:
            page.wait_for_selector('[data-testid="stApp"]', timeout=120_000)
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
