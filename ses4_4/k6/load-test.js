import http from 'k6/http';
import { check, sleep } from 'k6';

// This hits the REAL Helios evidence-review pipeline: ui/server.py shells
// out to `claude -p` for every request, which dispatches query-planner,
// literature-agent, trial-agent, evidence-synthesizer, citation-validator,
// and confidence-scorer against the live evidence MCP server. That's
// nothing like a cheap mocked route — each request can take up to the
// server's 240s pipeline timeout and consumes real Claude usage. The
// default profile below is deliberately light (2 VUs, ~4 iterations total)
// for that reason. Override BASE_URL/VUS/ITERATIONS via -e if you
// deliberately want more load.
const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8787';
const VUS = Number(__ENV.VUS || 2);
const ITERATIONS = Number(__ENV.ITERATIONS || 4);

const QUESTION = 'What evidence supports KRAS G12C inhibitors in lung cancer?';

export const options = {
  scenarios: {
    helios_smoke: {
      executor: 'shared-iterations',
      vus: VUS,
      iterations: ITERATIONS,
      maxDuration: '15m', // generous: each iteration may run a real multi-agent pipeline
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.post(
    `${BASE_URL}/api/ask`,
    JSON.stringify({ question: QUESTION }),
    { headers: { 'Content-Type': 'application/json' }, timeout: '245s' },
  );

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response is JSON with a status field': (r) => {
      try {
        return typeof JSON.parse(r.body).status === 'string';
      } catch {
        return false;
      }
    },
  });

  sleep(1);
}
