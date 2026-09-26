import http from 'k6/http';
import { check, sleep } from 'k6';

// Target endpoint under test. Swap for a real local/internal service, e.g. http://localhost:8000.
const BASE_URL = __ENV.BASE_URL || 'http://test.k6.io';

export const options = {
  stages: [
    { duration: '10s', target: 10 }, // ramp up to 10 VUs
    { duration: '40s', target: 10 }, // hold at 10 VUs
    { duration: '10s', target: 0 },  // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],   // fewer than 1% of requests may fail
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
  },
};

export default function () {
  const res = http.get(BASE_URL);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
