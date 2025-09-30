import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'], // 95% of requests must complete below 300ms
    http_req_failed: ['rate<0.01'],   // Error rate must be below 1%
    errors: ['rate<0.01'],            // Custom error rate below 1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function() {
  // Test 1: Health check
  let response = http.get(`${BASE_URL}/api/healthz/`);
  check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 100ms': (r) => r.timings.duration < 100,
  }) || errorRate.add(1);

  sleep(1);

  // Test 2: Product listing
  response = http.get(`${BASE_URL}/api/products/`);
  check(response, {
    'product list status is 200': (r) => r.status === 200,
    'product list response time < 500ms': (r) => r.timings.duration < 500,
    'product list has products': (r) => JSON.parse(r.body).results.length > 0,
  }) || errorRate.add(1);

  sleep(1);

  // Test 3: Product detail
  const products = JSON.parse(http.get(`${BASE_URL}/api/products/`).body);
  if (products.results.length > 0) {
    const productId = products.results[0].id;
    response = http.get(`${BASE_URL}/api/products/${productId}/`);
    check(response, {
      'product detail status is 200': (r) => r.status === 200,
      'product detail response time < 300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);
  }

  sleep(1);

  // Test 4: Category listing
  response = http.get(`${BASE_URL}/api/categories/`);
  check(response, {
    'category list status is 200': (r) => r.status === 200,
    'category list response time < 200ms': (r) => r.timings.duration < 200,
  }) || errorRate.add(1);

  sleep(1);

  // Test 5: Search functionality
  response = http.get(`${BASE_URL}/api/products/?search=test`);
  check(response, {
    'search status is 200': (r) => r.status === 200,
    'search response time < 400ms': (r) => r.timings.duration < 400,
  }) || errorRate.add(1);

  sleep(2);
}

export function setup() {
  // Setup function - runs once before the test
  console.log('Starting load test...');
  
  // Verify API is accessible
  const response = http.get(`${BASE_URL}/api/healthz/`);
  if (response.status !== 200) {
    throw new Error(`API not accessible: ${response.status}`);
  }
  
  console.log('API is accessible, starting load test');
}

export function teardown(data) {
  // Teardown function - runs once after the test
  console.log('Load test completed');
}
