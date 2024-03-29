<template>
  <div class="panoramic" v-bkloading="{ isLoading: isLoading, zIndex: 10 }">
    <div class="canvas" v-if="iaas.length !== 0">
      <bk-dropdown-menu trigger="click" v-if="edit">
        <div class="dropdown-trigger-btn" slot="dropdown-trigger">
          <div class="custom-add-button">
            <svg width="36" height="36" viewBox="0 0 36 36">
              <path fill="#34A853" d="M16 16v14h4V20z"></path>
              <path fill="#4285F4" d="M30 16H20l-4 4h14z"></path>
              <path fill="#FBBC05" d="M6 16v4h10l4-4z"></path>
              <path fill="#EA4335" d="M20 16V6h-4v14z"></path>
              <path fill="none" d="M0 0h36v36H0z"></path>
            </svg>
          </div>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li><a href="javascript:;" @click="handleSelectOperation('create')">Create</a></li>
          <!--
          <li><a href="javascript:;" @click="handleSelectOperation('search')">Search</a></li>
          <li><a href="javascript:;" @click="handleSelectOperation('edit')" style="pointer-events: none;">Edit</a></li>
          -->
        </ul>
      </bk-dropdown-menu>
      <div class="mini-map">
        <div class="main">
          <bk-select
            v-model="vendor"
            ext-cls="select-custom"
            ext-popover-cls="select-popover-custom"
            placeholder="please select a vendor"
            @change="handleConditionChange($event, 'vendor')"
            searchable>
            <bk-option v-for="option in vendorList"
                       :key="option.id"
                       :id="option.id"
                       :name="option.label"
                       :disabled="option.disabled">
            </bk-option>
          </bk-select>
        </div>
      </div>
      <div class="main">
        <topology :cloud="vendor" :region="region" :vpc="vpc" :iaas="iaas" />
      </div>
      <div class="menu" v-bind:style="{ 'display': shapes.isShow ? 'block' : 'none' }">
        <div class="header">
          <span class="title">{{ shapes.name }}</span>
          <bk-button :theme="'default'" title="close" @click="clearOperationData" style="margin-left: auto" text>
            Close
          </bk-button>
        </div>
        <div v-if="shapes.name === 'Create'" v-bkloading="{ isLoading: shapes.loading, zIndex: 10 }">
          <div class="main mt20">
            <div>
              <bk-upload
                :with-credentials="true"
                :multiple="false"
                :limit="1"
                :handle-res-code="handleUploadResponse"
                :custom-request="handleCustomUpload"
              ></bk-upload>
            </div>
          </div>
          <div class="footer mt20">
            <bk-button
              theme="primary"
              text
              @click="createPanoramicTopology"
              :disabled="shapes.stateFile === null">
              Commit
            </bk-button>
          </div>
        </div>
        <div v-else-if="shapes.name === 'Search'" v-bkloading="{ isLoading: shapes.loading, zIndex: 10 }">
          <div class="main mt20">
            <bk-radio-group v-model="shapes.filter.mode" class="mb20" @change="clearPanoramicTopologyParameters">
              <bk-radio-button value="condition">
                Condition
              </bk-radio-button>
              <bk-radio-button value="fuzzy">
                Fuzzy
              </bk-radio-button>
            </bk-radio-group>
            <div v-if="shapes.filter.mode === 'condition'">
              <div class="mb20">
                <span class="label">Region</span>
                <bk-select
                  v-model="shapes.filter.region"
                  searchable
                  class="mt5"
                  @clear="searchPanoramicTopology">
                  <bk-option v-for="option in regionList"
                             :key="option.id"
                             :id="option.id"
                             :name="option.label">
                  </bk-option>
                </bk-select>
              </div>
              <div class="mb20">
                <span class="label">Resource</span>
                <bk-select
                  v-model="shapes.filter.block_name"
                  searchable
                  class="mt5"
                  @clear="searchPanoramicTopology">
                  <bk-option v-for="option in Object.keys(terraform.tencent.product)"
                             :key="option"
                             :id="option"
                             :name="option">
                  </bk-option>
                </bk-select>
              </div>
              <div class="mb20">
                <span class="label">VPC</span>
                <bk-select
                  v-model="shapes.filter.block_name"
                  searchable
                  class="mt5"
                  disabled>
                  <bk-option v-for="option in vpcList"
                             :key="option.id"
                             :id="option.id"
                             :name="option.name">
                  </bk-option>
                </bk-select>
              </div>
              <div class="mb20">
                <span class="label">Plan</span>
                <bk-select
                  v-model="shapes.filter.block_name"
                  searchable
                  class="mt5"
                  disabled>
                  <bk-option v-for="option in terraform.plan"
                             :key="option.id"
                             :id="option.id"
                             :name="option.label">
                  </bk-option>
                </bk-select>
              </div>
            </div>
            <div v-else-if="shapes.filter.mode === 'fuzzy'">
              <bk-input :clearable="true" v-model="shapes.query" @clear="searchPanoramicTopology"></bk-input>
            </div>
          </div>
          <div class="footer mt20">
            <bk-button
              theme="primary"
              text
              @click="searchPanoramicTopology"
              :disabled="isSearchDisable">
              Search
            </bk-button>
          </div>
        </div>
      </div>
    </div>
    <bk-exception class="exception-wrap-item" type="empty" v-else>
      <bk-upload
        v-if="!shapes.loading"
        :with-credentials="true"
        :multiple="false"
        :limit="1"
        :handle-res-code="handleUploadResponse"
        :custom-request="handleCustomUpload"
      ></bk-upload>
      <bk-spin icon="circle-2-1" v-else></bk-spin>
    </bk-exception>
  </div>
</template>

<script>
import Topology from '../topology/index.vue';
import IaaSData from '../../store/mock.json';

export default {
  name: 'Panoramic',
  components: {
    Topology,
  },
  props: {
    bizId: {
      type: Number,
      default: -1,
    },
  },
  data() {
    return {
      vendorList: [
        {
          id: 'tencentcloud',
          label: 'Tencent',
          icon: '/static/other/yun.png',
          disabled: false,
        },
        {
          id: 'gcp',
          label: 'GCP',
          icon: '/static/other/yun.png',
          disabled: true,
        },
      ],
      regionList: [],
      vpcList: [],
      edit: true,
      vendor: 'tencentcloud',
      region: '',
      vpc: '',
      iaas: [],
      backup: [],
      shapes: {
        isShow: false,
        name: 'Create',
        stateFile: null,
        loading: false,
        filter: {
          mode: 'condition',
          region: '',
          vpc: '',
          block_name: '',
          plan: '',
        },
        query: '',
      },
      terraform: {
        raw: {},
        data: {},
        locations: [],
        tencent: {
          product: {
            LB: {
              name: 'lb',
            },
            VM: {
              name: 'vm',
            },
            NAT: {
              name: 'nat',
            },
            SecurityGroup: {
              name: 'sg',
            },
            Subnet: {
              name: 'subnet',
            },
            VPCEndPoint: {
              name: 'vep',
            },
            VPC: {
              name: 'vpc',
            },
            LOG: {
              name: 'log',
            },
            EIP: {
              name: 'ip',
            },
            ObjectStorage: {
              name: 'bucket',
            },
            MySql: {
              name: 'db',
            },
            Redis: {
              name: 'cache',
            },
            Kubernetes: {
              name: 'k8s',
            },
            DNS: {
              name: 'dns',
            },
            CDN: {
              name: 'cdn',
            },
          },
        },
        plan: [
          { id: 'add', label: 'add' },
          { id: 'change', label: 'change' },
          { id: 'destroy', label: 'destroy' },
        ],
      },
      isLoading: true,
    };
  },
  computed: {
    isSearchDisable() {
      return (this.shapes.filter.mode === 'fuzzy' && this.shapes.query === '')
          || (this.shapes.filter.mode === 'condition' && this.shapes.filter.plan === ''
              && this.shapes.filter.region === '' && this.shapes.filter.vpc === ''
              && this.shapes.filter.block_name === '');
    },
  },
  watch: {},
  created() {
    this.init();
  },
  methods: {
    async init() {
      this.vendor = 'tencentcloud';
      await this.getPanoramicData();
      this.isLoading = false;
    },
    handleSelectOperation(operation) {
      if (operation === 'create') {
        this.shapes.name = 'Create';
      } else if (operation === 'edit') {
        this.shapes.name = 'Edit';
      } else if (operation === 'search') {
        this.shapes.name = 'Search';
      }
      this.shapes.isShow = !this.shapes.isShow;
    },
    async handleConditionChange(val, condition) {
      switch (condition) {
        case 'vendor':
          this.vendor = val;
          await this.getPanoramicData();
          break;
        case 'region':
          break;
        case 'vpc':
          if (this[condition] === '') {
            this.iaas = [...this.backup];
            if (condition === 'region') {
              this.vpc = '';
              break;
            } else {
              condition = 'region';
            }
          } else {
            if (condition === 'vpc' && this.region === '') {
              this.vpc = '';
              break;
            }
          }

          for (let i = 0; i < this.iaas.length; i++) {
            const tmp = [];
            for (let j = 0; j < this.iaas[i].data.length; j++) {
              // eslint-disable-next-line max-len
              if (this.iaas[i].data[j].hasOwnProperty(condition) && this[condition] === this.iaas[i].data[j][condition]) {
                tmp.push(this.iaas[i].data[j]);
              }
            }
            if (this.iaas[i].data[0].hasOwnProperty(condition)) {
              this.iaas.data = tmp;
            }
          }
          this.iaas = this.iaas.filter(item => item.data.length > 0);
          break;
      }
    },
    normalizeVendor() {
      // need to filter cloud / region / vpc / subnet
      switch (this.vendor) {
        case 'tencentcloud':
          /**
           * 0, build product match relationship
           * 1, find vendor, region, vpc, subnet
           * 2, find network group
           * 3, find compute group
           * 4, find storage group
           * 5, find iam group
           * 6, generate new data structure
           * 7, output {
           *   id: 'internet',
           *   type: 'internet',
           *   group: '',
           *   x: 0,
           *   y: 0,
           *   count: 100,
           *   data: [
           *     {
           *       id: lb-adasdas,
           *       name: test,
           *       vip: 1.1.1.1,
           *       network_type: Open,
           *       region: ap-shanghai,
           *       out_bandwidth: 1234
           *     }
           *   ]
           * }
           * */
          // eslint-disable-next-line no-case-declarations
          const regionMap = Object();

          this.iaas = this.terraform.data.resources.map((product) => {
            let id = '';
            let group = '';
            const resources = [];
            const changes = [];
            product.instances.forEach((instance) => {
              if (this.terraform.tencent.product.hasOwnProperty(instance.name)) {
                if (id === '' && group === '') {
                  id = this.terraform.tencent.product[instance.name].name;
                  group = instance.name.toLowerCase();
                }
                const item = {};
                instance.fields.forEach((field) => {
                  item[field.key] = field.value;
                  if (field.key === 'region') {
                    regionMap[field.key] = field.value;
                  }
                });
                if (id === 'vpc') {
                  this.vpcList.push(item);
                }

                if (instance.change.state !== 0) {
                  item.diff = instance.change;
                  changes.push(item);
                } else {
                  item.diff = null;
                }
                resources.push(item);
              } else {
                console.warn(`${instance.name} have not been add to default product list..`);
              }
            });
            return {
              id,
              group,
              count: product.count,
              data: resources,
              changes,
            };
          }).filter(item => item.id !== '');
          this.backup = [...this.iaas];
          this.regionList = Object.keys(regionMap).map(key => ({
            id: regionMap[key],
            label: regionMap[key],
            icon: '',
          }));
          break;
        case 'gcp':
          break;
      }
    },
    handleUploadResponse(response) {
      if (response.id) {
        return true;
      }
      return false;
    },
    handleCustomUpload(options) {
      setTimeout(() => {
        options.fileObj.progress = '100%';
        options.onProgress({}, 100);
        try {
          const reader = new FileReader();
          reader.readAsText(options.fileObj.origin, 'UTF-8');
          reader.onload = async (e) => {
            const content = e.target.result;
            this.shapes.stateFile = JSON.parse(content);
            if (this.iaas.length === 0) {
              await this.createPanoramicTopology();
            }
          };
          options.onSuccess({ id: 200 }, options.fileObj);
          options.onDone(options.fileObj);
        } catch (e) {
          this.$bkMessage({
            theme: 'error',
            message: 'file parse error...',
            limit: 1,
          });
        }
      });
    },
    async getPanoramicData() {
      try {
        const params = {
          id: this.bizId,
          username: this.$store.state.user.username,
          vendor: this.vendor,
        };

        if (this.shapes.filter.mode === 'fuzzy') {
          if (this.shapes.query !== '') {
            params.query_str = this.shapes.query;
          }
        } else if (this.shapes.filter.mode === 'condition') {
          if (this.shapes.filter.region !== '') {
            params.query_str = this.shapes.filter.region;
          }
          if (this.shapes.filter.block_name !== '') {
            params.block_name = this.shapes.filter.block_name;
          }
        }

        const res = await this.$store.dispatch('example/getPanoramicTopologyData', params, { fromCache: true });
        if (res.data.length > 0) {
          this.terraform.raw = res.data[0];
          this.vendor = this.terraform.raw.vendor;
          this.terraform.data = JSON.parse(JSON.stringify(this.terraform.raw));
        } else {
          this.terraform.raw = [];
          this.terraform.data = [];
        }
        this.iaas = [];
        this.normalizeVendor();
      } catch (e) {
        console.error(e);
      }
    },
    async createPanoramicTopology() {
      const params = {
        id: this.bizId,
        username: this.$store.state.user.username,
        state_file: this.shapes.stateFile,
      };
      try {
        this.shapes.loading = true;
        const res = await this.$store.dispatch('example/addPanoramicTopologyData', params, { fromCache: true });
        let message = 'upload success...';
        if (!res.result) {
          message = 'some error happen...';
        } else {
          await this.init();
        }
        this.$bkMessage({
          theme: 'primary',
          message: message,
          limit: 1,
        });
        await this.clearOperationData();
      } catch (e) {
        console.warn(e);
      }
    },
    async searchPanoramicTopology() {
      await this.getPanoramicData();
    },
    async clearOperationData() {
      this.shapes = {
        isShow: false,
        name: 'Create',
        stateFile: null,
        loading: false,
        filter: {
          mode: 'condition',
          region: '',
          vpc: '',
          block_name: '',
          plan: '',
        },
        query: '',
      };
      await this.getPanoramicData();
    },
    clearPanoramicTopologyParameters() {
      this.shapes.filter.region = '';
      this.shapes.filter.block_name = '';
      this.shapes.filter.vpc = '';
      this.shapes.filter.plan = '';
      this.shapes.query = '';
    },
  },
};
</script>

<style>
    @import './index.css';
</style>
