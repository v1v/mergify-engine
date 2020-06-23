import requests
import urllib3

from mergify_engine import config
from mergify_engine.tests.functional import httpx_vcr_stubs  # noqa


httpx_vcr_stubs.monkeypatch()

real_session_init = requests.sessions.Session.__init__

RETRY = urllib3.Retry(
    total=None,
    redirect=3,
    connect=5,
    read=5,
    status=5,
    backoff_factor=0.2,
    status_forcelist=list(range(500, 599)) + [429],
    method_whitelist=[
        "HEAD",
        "TRACE",
        "GET",
        "PUT",
        "OPTIONS",
        "DELETE",
        "POST",
        "PATCH",
    ],
    raise_on_status=False,
)


def retring_session_init(self, *args, **kwargs):
    real_session_init(self, *args, **kwargs)

    adapter = requests.adapters.HTTPAdapter(max_retries=RETRY)

    self.mount(config.GITHUB_API_URL, adapter)


requests.sessions.Session.__init__ = retring_session_init