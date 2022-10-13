import http from 'k6/http';
import { check, fail, group, sleep } from 'k6';

const BASE_URL = 'http://k8s-default-wsingres-e3857e829f-1074464700.us-east-1.elb.amazonaws.com/';
//const BASE_URL = 'http://dev.api.alerce.online/alerts/v1/';

export const options = {
    scenarios: {
      constant_load_transient: {
        executor: 'constant-vus',
        vus: 25,
        duration: '20m',
        // gracefulStop: '0s',  // this is for sequential tests
        env: {CLASS: 'SNIa'},
        exec: 'query_and_view_object',
      },
      constant_load_variable: {
        executor: 'constant-vus',
        vus: 25,
        duration: '20m',
        // gracefulStop: '0s',  // this is for sequential tests
        // startTime: '1m',  // this is for sequential tests
        env: {CLASS: 'CEP'},
        exec: 'query_and_view_object',
      },
      constant_load_stochastic: {
        executor: 'constant-vus',
        vus: 25,
        duration: '20m',
        // gracefulStop: '0s',  // this is for sequential tests
        // startTime: '2m',  // this is for sequential tests
        env: {CLASS: 'AGN'},
        exec: 'query_and_view_object',
      },
    },
    thresholds: {
      'group_duration{group:::retrieveObjectData}': ['p(90) < 2000']
    }
};

export function query_and_view_object() {
  const URL = BASE_URL + 'objects';
  const SLEEP = 1;
  const PER_PAGE = 10;
  const CLASS = __ENV.CLASS;

  const SEARCH_STR = 'ranking=1' + '&' +
                 'classifier=lc_classifier' + '&' +
                 'probability=0.5' + '&' +
                 'ndet=10' + '&' +
                 'order_by=probability' + '&' +
                 'order_mode=DESC' + '&' +
                 'page_size=' + PER_PAGE + '&' +
                 'class=' + CLASS;

  const query_response = http.get(URL + '?' + SEARCH_STR);
  if (
    !check(query_response, {
      'is query status 200': (r) => r.status === 200
    })
  )  {
    fail('query status is ' + query_response.status); // Do not go on with the iteration unless there's something there
  }
  sleep(SLEEP);

  const items = query_response.json()['items']
  const ind = Math.floor(Math.random() * items.length)

  const oid = items[ind]['oid'];
  group('retrieveObjectData', (_) => {
    const responses = http.batch([
      ['GET', URL + '/' + oid + '/lightcurve'],
      ['GET', URL + '/' + oid + '/magstats'],
      ['GET', URL + '/' + oid + '/probabilities'],
    ]);

    check(responses[0], {'lightcurve status is 200': (r) => r.status === 200});
    check(responses[1], {'magstats status is 200': (r) => r.status === 200});
    check(responses[2], {'probabilities status is 200': (r) => r.status === 200});
  });
}
