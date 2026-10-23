#!/usr/bin/env python3
"""Public host entry point: serve the x402 gated recall API.

This is the start command for the public deployment (see render.yaml).
It serves api.payment_gate:app, the recall check API behind its x402
payment gate, with the standard library's threaded WSGI server, so
concurrent paid calls do not serialize behind one slow source fetch.

Configuration is the gate's, environment only: PAYOUT_WALLET_ADDRESS
is required (the build refuses to start without it, because a paid
endpoint with nowhere to pay is pointless), FACILITATOR_URL,
X402_PRICE_ATOMIC, X402_NETWORK and X402_ASSET have defaults in
api/payment_gate.py. PORT is the host's port, default 8000.

    PAYOUT_WALLET_ADDRESS=0x... python3 server.py
"""

import os
import sys
from pathlib import Path
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import payment_gate, recall_api  # noqa: E402


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """A WSGI server that handles each request on its own thread."""

    daemon_threads = True


def main():
    try:
        gated = payment_gate.build_app()
    except recall_api.ConfigError as err:
        sys.stderr.write("refusing to start: %s\n" % err)
        return 2
    port = int(os.environ.get("PORT", "8000"))
    config = gated.config
    sys.stderr.write(
        "gated recall API on http://0.0.0.0:%d/  payout wallet: %s  "
        "facilitator: %s  price: %s atomic on %s\n"
        % (port, config.pay_to, config.facilitator_url,
           config.price, config.network))
    with make_server("0.0.0.0", port, gated,
                     server_class=ThreadingWSGIServer) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
