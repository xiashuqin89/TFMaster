/**
 * @file app store
 * @author
 */

import http from '@/api';
import queryString from 'query-string';

export default {
  namespaced: true,
  state: {
  },
  mutations: {
  },
  actions: {
    getExample(context, params, config = {}) {
      // eslint-disable-next-line no-undef
      return http.get(`/table?&${queryString.stringify(params)}`, params, config);
    },
    addPanoramicTopologyData(context, params, config = {}) {
      // return http.post(`/api/v1/panoramic/topology/?&${queryString.stringify(params)}`, params, config);
      const { id, username } = params;
      delete params.id;
      delete params.username;
      return http.post(`/v1/state/upload_json/${username}/${id}`, params, config);
    },
    getPanoramicTopologyData(context, params, config = {}) {
      // return http.get(`/api/v1/panoramic/topology/?&${queryString.stringify(params)}`, params, config);
      const { id, username } = params;
      delete params.id;
      delete params.username;
      return http.post(`/v1/analyze/query/${username}/${id}`, params, config);
    },
  },
};
