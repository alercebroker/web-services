import http from 'k6/http';
import { check, group, sleep } from 'k6';

const BASE_URL = 'https://dev.api.alerce.online/alerts/v1/';

export const options = {
    stages: [
	  { target: 50, duration: '1m' },  // Ramp-up
	  { target: 50, duration: '10m' },
	  { target: 0, duration: '1m' },
    ],
    thresholds: {
      'http_req_duration': ['p(90) < 1500']
    }
};

export default function () {
  const URL = BASE_URL + 'objects';
  const SLEEP = 0.5;
  const PER_PAGE = 5;

  const SEARCH_STR = 'ranking=1' + '&' +
                 'classifier=lc_classifier' + '&' +
                 'probability=0.7' + '&' +
                 'ndet=20' + '&' +
                 'order_by=probability' + '&' +
                 'order_mode=DESC' + '&' +
                 'page_size=' + PER_PAGE;

  group('transientWorkflow', (_) => {
    const query_response = http.get(URL + '?' + SEARCH_STR + '&class=SNIa');
    check(query_response, {
      'is query status 200': (r) => r.status === 200
    });
    sleep(SLEEP);

    for (let i = 0; i < PER_PAGE; i++){
      const oid = query_response.json()['items'][i]['oid'];
      const lightcurve_response = http.get(URL + '/' + oid + '/lightcurve');
      check(lightcurve_response, {
        'is lightcurve status 200': (r) => r.status === 200
      });
      const magstats_response = http.get(URL + '/' + oid + '/magstats');
      check(magstats_response, {
        'is magstats status 200': (r) => r.status === 200
      });
      const probabilities_response = http.get(URL + '/' + oid + '/probabilities');
      check(probabilities_response, {
        'is probabilities status 200': (r) => r.status === 200
      });
      sleep(SLEEP);
    }
  });

}
