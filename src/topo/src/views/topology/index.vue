<template>
  <div class="topology">
    <section style="width: 100%; height: 100%;">
      <div id="container">
      </div>
    </section>
    <bk-dialog
      v-model="nodeData.visible"
      width="840"
      header-position="left"
      :title="nodeData.title"
      :show-footer="false"
      :fullscreen="true"
      @after-leave="clearNodeData"
      ext-cls="node-detail">
      <div class="main">
        <bk-form :label-width="200" form-type="vertical" ext-cls="node-form">
          <bk-form-item :label="'Summary'">
            <div v-if="nodeData.summary.length > 0">
              Change:
              <bk-tag v-for="(item, index) in nodeData.summary" :key="index" theme="danger">{{ item }}</bk-tag>
            </div>
            <span v-else>Everything is up to date</span>
          </bk-form-item>
          <bk-form-item :label="'List'">
            <bk-table
              :data="nodeData.table.data"
              :pagination="nodeData.table.pagination"
              :highlight-current-row="true"
              size="small"
              ref="nodeDataTableRef"
              ext-cls="node-data-table-class"
              @row-click="handleRowClick"
              @page-change="nodeData.table.handlePageChange($event)">
              <bk-table-column type="index" label="No." width="60"></bk-table-column>
              <bk-table-column
                v-for="(item, index) in nodeData.table.header"
                v-if="item !== 'diff'"
                :key="index"
                :label="item"
                :prop="item">
                <template slot-scope="props">
                  <span v-if="typeof props.row[item] === 'string' || typeof props.row[item] === 'number'">
                    {{ props.row[item] }}
                  </span>
                  <bk-popover placement="right" v-else-if="props.row[item] instanceof Array">
                    <span style="text-decoration: underline dotted red;">
                      {{ props.row[item].join(',').substring(0, 20) + '...' }}
                    </span>
                    <div slot="content">
                      <div v-for="(detail, j) in props.row[item]" :key="j" class="bk-text-primary">
                        {{ detail }}
                      </div>
                    </div>
                  </bk-popover>
                  <span v-else-if="props.row[item] === null">N/A</span>
                </template>
              </bk-table-column>
            </bk-table>
          </bk-form-item>
          <bk-form-item :label="'Diff'" v-bind:style="{ 'display': nodeData.diff.visible }">
            <bk-diff
              theme="dark"
              :old-content="nodeData.diff.old"
              :new-content="nodeData.diff.new"
              :format="'side-by-side'"
              language="javascript"></bk-diff>
          </bk-form-item>
        </bk-form>
      </div>
      <!--
      <p>{{ nodeData.data }}</p>
      -->
    </bk-dialog>
  </div>
</template>

<script>
import { Graph, Node } from '@antv/x6';
import { register } from '@antv/x6-vue-shape';
import Device from '../../components/nodes/device/index.vue';
import Cluster from '../../components/nodes/cluster/index.vue';
import IaaSData from '../../store/mock.json';

register({
  shape: 'device-node',
  inherit: 'vue-shape',
  width: 80,
  height: 80,
  component: {
    template: '<device />',
    components: {
      Device,
      Cluster,
    },
  },
});

register({
  shape: 'cluster-node',
  inherit: 'vue-shape',
  width: 160,
  height: 40,
  component: {
    template: '<cluster />',
    components: {
      Device,
      Cluster,
    },
  },
});

class ParentGroup extends Node {
  collapsed = false;
  expandSize = { width: 0, height: 0 };

  postprocess() {
    this.toggleCollapse(false);
  }

  isCollapsed() {
    return this.collapsed;
  }

  toggleCollapse(collapsed) {
    const target = collapsed == null ? !this.collapsed : collapsed;
    if (target) {
      this.attr('buttonSign', { d: 'M 1 5 9 5 M 5 1 5 9' });
      this.expandSize = this.getSize();
      this.resize(100, 32);
    } else {
      this.attr('buttonSign', { d: 'M 2 5 8 5' });
      if (this.expandSize) {
        this.resize(this.expandSize.width, this.expandSize.height);
      }
    }
    this.collapsed = target;
  }
}

ParentGroup.config({
  markup: [
    {
      tagName: 'rect',
      selector: 'body',
    },
    {
      tagName: 'text',
      selector: 'label',
    },
    {
      tagName: 'g',
      selector: 'buttonGroup',
      children: [
        {
          tagName: 'rect',
          selector: 'button',
          attrs: {
            'pointer-events': 'visiblePainted',
          },
        },
        {
          tagName: 'path',
          selector: 'buttonSign',
          attrs: {
            fill: 'none',
            'pointer-events': 'none',
          },
        },
      ],
    },
  ],
  attrs: {
    body: {
      refWidth: '100%',
      refHeight: '100%',
      strokeWidth: 1,
      fill: '#ffffff',
      stroke: 'none',
    },
    buttonGroup: {
      refX: 8,
      refY: 8,
    },
    button: {
      height: 14,
      width: 16,
      rx: 2,
      ry: 2,
      fill: '#f5f5f5',
      stroke: '#ccc',
      cursor: 'pointer',
      event: 'node:collapse',
    },
    buttonSign: {
      refX: 3,
      refY: 2,
      stroke: '#808080',
    },
    label: {
      fontSize: 12,
      fill: '#fff',
      refX: 32,
      refY: 10,
    },
  },
});

export default {
  name: 'Topology',
  components: {},
  props: {
    mode: {
      type: String,
      default() {
        return 'full';
      },
    },
    cloud: {
      type: String,
      default() {
        return 'tencentcloud';
      },
    },
    region: {
      type: String,
      default() {
        return 'ap-shanghai';
      },
    },
    vpc: {
      type: String,
      default() {
        return 'vpc-xxx';
      },
    },
    iaas: {
      type: Array,
      default() {
        return IaaSData;
      },
    },
  },
  data() {
    return {
      config: {
        tencentcloud: {
          vm: 'CloudVirtualMachine.png',
          bm: 'CVMDedicatedHost.png',
          lb: 'CloudLoadBalancer.png',
          bucket: 'CloudObjectStorage.png',
          sg: 'SecurityOperationsCenter.png',
          db: 'TencentDBforTcaplusDB.png',
          cache: 'TencentDBforRedis.png',
          region: '',
          vpc: 'VirtualPrivateCloud.png',
          subnet: 'DirectConnect.png',
          nat: 'NATGateway.png',
          router: 'CloudStorageGateway(CSG).png',
          disk: 'CloudBlockStorage.png',
          ddos: 'ddos.png',
          cdn: 'ContentDeliveryNetwork.png',
          ip: 'ElasticIP.png',
          k8s: 'ElasticKubernetesService.png',
          iam: 'FaceRecognition.png',
          user: 'FaceRecognition.png',
          group: 'TencentCloudConference.png',
          aksk: 'KeyManagementService.png',
          log: 'CloudLogService.png',
          dns: 'TencentCloudDomainNameSystem.png',
        },
        aws: {},
        gcp: {},
        azure: {},
        zenlayer: {},
      },
      coordinate: {
        internet: { x: 100, y: 80, type: 'internet', component: '' },
        vendor: { x: 100, y: 200, type: 'vendor', component: '' },
        iam: { x: 1000, y: 700, type: 'block', component: 'block-node' },
        user: { x: 680, y: 710, type: 'account', component: 'device-node' },
        group: { x: 780, y: 710, type: 'account', component: 'device-node' },
        aksk: { x: 880, y: 710, type: 'account', component: 'device-node' },
        sg: { x: 250, y: 300, type: 'security', component: 'device-node' },
        lb: { x: 400, y: 150, type: 'network', component: 'device-node' },
        cdn: { x: 400, y: 250, type: 'network', component: 'device-node' },
        dns: { x: 400, y: 350, type: 'network', component: 'device-node' },
        ip: { x: 400, y: 450, type: 'network', component: 'device-node' },
        router: { x: 550, y: 320, type: 'router', component: '' },
        // vpc: { x: 650, y: 120, type: 'block', component: 'block-node', width: 800, height: 440 },
        network: { x: 380, y: 120, type: 'block', component: 'block-node', width: 120, height: 440 },
        compute: { x: 700, y: 175, type: 'block', component: 'block-node', width: 720, height: 80 },
        storage: { x: 700, y: 295, type: 'block', component: 'block-node', width: 720, height: 80 },
        vlan: { x: 700, y: 415, type: 'block', component: 'block-node', width: 720, height: 80 },
        vm: { x: 730, y: 200, type: 'compute', component: 'cluster-node' },
        bm: { x: 900, y: 200, type: 'compute', component: 'cluster-node' },
        k8s: { x: 1070, y: 200, type: 'compute', component: 'cluster-node' },
        bucket: { x: 730, y: 320, type: 'storage', component: 'cluster-node' },
        db: { x: 900, y: 320, type: 'storage', component: 'cluster-node' },
        cache: { x: 1070, y: 320, type: 'storage', component: 'cluster-node' },
        log: { x: 1240, y: 320, type: 'storage', component: 'cluster-node' },
        subnet: { x: 730, y: 440, type: 'vlan', component: 'cluster-node' },
        nat: { x: 900, y: 440, type: 'vlan', component: 'cluster-node' },
      },
      staticPrefix: '',
      graph: null,
      nodes: [],
      edges: [],
      graphData: {},
      nodeData: {
        visible: false,
        fullscreen: true,
        raw: {},
        title: 'Detail',
        diff: {
          data: [],
          raw: [],
          old: '',
          new: '',
          visible: 'none',
        },
        summary: [],
        table: {
          header: [],
          data: [],
          raw: [],
          pagination: {
            current: 1,
            count: 0,
            limit: 10,
            'limit-list': [10],
          },
          handlePageChange: (page) => {
            this.nodeData.table.pagination.current = page;
            // eslint-disable-next-line max-len
            this.nodeData.table.data = this.nodeData.table.raw.slice((page - 1) * this.nodeData.table.pagination.limit, page * this.nodeData.table.pagination.limit);
            setTimeout(() => {
              for (let i = 0; i < this.nodeData.table.data.length; i++) {
                const element = document.querySelector(`tr[data-table-row='row-${i}']`);
                element.setAttribute('class', 'bk-table-row');
                if (this.nodeData.table.data[i].diff) {
                  element.setAttribute('class', 'bk-table-row diff-row');
                }
              }
            }, 10);
          },
        },
      },
    };
  },
  created() {
  },
  mounted() {
    this.init();
  },
  methods: {
    buildNode(node) {
      this.nodeData.raw = node;
      this.nodeData.title = node.group.toLocaleUpperCase();
      switch (node.id) {
        case 'lb':
        case 'cdn':
        case 'vm':
        case 'bm':
        case 'k8s':
        case 'bucket':
        case 'db':
        case 'cache':
        case 'subnet':
        case 'sg':
        case 'nat':
        case 'dns':
        case 'ip':
        case 'log':
          // summary
          this.nodeData.summary = node.changes.map((item) => {
            if (typeof item.name !== 'undefined') {
              return item.name;
            }
            return item.id;
          });
          this.nodeData.diff.visible = 'none';
          this.nodeData.table.header = Object.keys(node.data[0]);
          this.nodeData.table.data = node.data;
          this.nodeData.table.pagination.count = node.count;
          this.nodeData.table.pagination.current = 1;
          this.nodeData.table.raw = [...node.data];
          this.nodeData.table.data = this.nodeData.table.raw.slice(0, this.nodeData.table.pagination.limit);
          this.nodeData.visible = true;
          setTimeout(() => {
            for (let i = 0; i < this.nodeData.table.data.length; i++) {
              const element = document.querySelector(`tr[data-table-row='row-${i}']`);
              element.setAttribute('class', 'bk-table-row');
              if (this.nodeData.table.data[i].diff) {
                element.setAttribute('class', 'bk-table-row diff-row');
              }
            }
          }, 10);
          break;
        case 'vpc':
        case 'router':
          break;
      }
    },
    clearNodeData() {},
    handleRowClick(row, event, column, rowIndex, columnIndex) {
      if (row.diff) {
        this.nodeData.diff.data = row.diff;
        this.nodeData.diff.raw = { ...row.diff };
        this.nodeData.diff.old = JSON.stringify(row.diff.before, null, 2);
        this.nodeData.diff.new = JSON.stringify(row.diff.after, null, 2);
        this.nodeData.diff.visible = 'block';
        setTimeout(() => {
          const element = document.querySelector(`tr[data-table-row='row-${rowIndex}']`);
          element.setAttribute('class', 'bk-table-row diff-row');
        }, 10);
      } else {
        this.nodeData.diff.visible = 'none';
      }
    },
    buildFrame() {
      const _self = this;
      function createGroup(id, x, y, width, height, fill = '#fffbe6', stroke = '#ffe7ba') {
        const group = new ParentGroup({
          id,
          x,
          y,
          width,
          height,
          attrs: {
            body: { fill, stroke },
            label: { text: id.toUpperCase(), fill: '#000' },
          },
          zIndex: 1,
        });
        _self.graph.addNode(group);
        return group;
      }

      function createEdge(id, source, target) {
        return _self.graph.addEdge({
          id,
          source,
          target,
          router: { name: 'manhattan' },
          connector: { name: 'rounded' },
          attrs: {
            line: {
              stroke: '#faad14',
              targetMarker: 'classic',
            },
          },
        });
      }
      switch (this.cloud) {
        case 'tencentcloud':
          // eslint-disable-next-line no-case-declarations
          const internet = this.graph.addNode({
            shape: 'image',
            x: 100,
            y: 80,
            width: 60,
            height: 40,
            imageUrl: '/static/images/other/entry_internet.png',
            label: 'Internet',
            zIndex: 50,
            attrs: {
              body: {
                fill: '#fff',
                stroke: '#8f8f8f',
                strokeWidth: 1,
              },
              label: {
                refX: 0.5,
                refY: '100%',
                refY2: 4,
                textAnchor: 'middle',
                textVerticalAnchor: 'top',
              },
            },
          });
          // eslint-disable-next-line no-case-declarations
          const vendor = this.graph.addNode({
            shape: 'image',
            x: 100,
            y: 200,
            width: 60,
            height: 40,
            imageUrl: `/static/images/other/${this.cloud}.png`,
            // label: this.cloud,
            attrs: {
              body: {
                fill: '#fff',
                stroke: '#8f8f8f',
                strokeWidth: 1,
              },
              label: {
                refX: 0.5,
                refY: '100%',
                refY2: 4,
                textAnchor: 'middle',
                textVerticalAnchor: 'top',
              },
            },
          });
          createEdge('0', internet, vendor);
          // eslint-disable-next-line no-case-declarations
          const vpc = createGroup('vpc', 650, 120, 800, 440, '#E1F5FE', '#E1F5FE');

          // eslint-disable-next-line no-case-declarations
          const cache = Object();
          // eslint-disable-next-line no-unused-vars,no-case-declarations
          let network = null;
          // eslint-disable-next-line no-unused-vars,no-case-declarations
          let compute = null;
          // eslint-disable-next-line no-unused-vars,no-case-declarations
          let storage = null;
          // eslint-disable-next-line no-unused-vars,no-case-declarations
          let vlan = null;
          // eslint-disable-next-line no-unused-vars,no-case-declarations
          let router = null;
          this.iaas.forEach((product) => {
            const tmp = { ...product };
            if (product.id in this.coordinate) {
              tmp.x = this.coordinate[product.id].x;
              tmp.y = this.coordinate[product.id].y;
              tmp.component = this.coordinate[product.id].component;
              tmp.type = this.coordinate[product.id].type;
              if (tmp.type in this.coordinate && !(tmp.type in cache)) {
                const block = { ...this.coordinate[tmp.type] };
                block.id = tmp.type;
                cache[block.id] = true;
                if (block.id === 'network' && !network) {
                  network = createGroup('network', block.x, block.y, block.width, block.height, '#F3E5F5', '#F3E5F5');
                  router = this.graph.addNode({
                    shape: 'image',
                    x: 550,
                    y: 320,
                    width: 40,
                    height: 40,
                    imageUrl: '/static/images/other/router.png',
                    label: 'Router',
                    zIndex: 50,
                    attrs: {
                      body: {
                        fill: '#fff',
                        stroke: '#8f8f8f',
                        strokeWidth: 1,
                      },
                      label: {
                        refX: 0.5,
                        refY: '100%',
                        refY2: 4,
                        textAnchor: 'middle',
                        textVerticalAnchor: 'top',
                      },
                    },
                  });
                  createEdge('network->router', network, router);
                }

                if (block.id === 'compute' && !compute) {
                  compute = createGroup('compute', block.x, block.y, block.width, block.height);
                  vpc.addChild(compute);
                  if (router) {
                    createEdge('router->compute', router, compute);
                  }
                }

                if (block.id === 'storage' && !storage) {
                  storage = createGroup('storage', block.x, block.y, block.width, block.height);
                  vpc.addChild(storage);
                  if (router) {
                    createEdge('router->storage', router, storage);
                  }
                }

                if (block.id === 'vlan' && !vlan) {
                  vlan = createGroup('vlan', block.x, block.y, block.width, block.height);
                  vpc.addChild(vlan);
                  if (router) {
                    createEdge('router->vlan', router, vlan);
                  }
                }
              }
              const node = this.graph.addNode({
                shape: tmp.component,
                x: tmp.x,
                y: tmp.y,
                zIndex: 5,
                data: {
                  label: tmp.id.toUpperCase(),
                  status: 'success',
                  device: `${this.config[this.cloud][tmp.id]}`,
                  raw: product,
                  type: tmp.type,
                },
              });
              this.nodes.push(node);
            }
          });

          this.nodes.forEach((node) => {
            if ('data' in node && node.data.type === 'security') {
              createEdge('vendor->security', vendor, node);
              if (network) {
                createEdge('security->network', node, network);
              }
            }

            if ('data' in node && node.data.type === 'network') {
              network.addChild(node);
            }

            if ('data' in node && node.data.type === 'compute') {
              compute.addChild(node);
            }

            if ('data' in node && node.data.type === 'storage') {
              storage.addChild(node);
            }

            if ('data' in node && node.data.type === 'vlan') {
              vlan.addChild(node);
            }
          });
          break;
        case 'gcp':
          break;
      }
    },
    buildEvent() {
      this.graph.on('node:click', ({ e, x, y, node, view }) => {
        try {
          this.buildNode(node.data.raw);
          this.$emit('topologyNodeClick', node.data.raw);
        } catch (e) {
          console.warn(e);
        }
      });

      this.graph.on('node:collapse', ({ node }) => {
        node.toggleCollapse();
        const collapsed = node.isCollapsed();
        const collapse = (parent) => {
          const cells = parent.getChildren();
          if (cells) {
            cells.forEach((cell) => {
              if (collapsed) {
                cell.hide();
              } else {
                cell.show();
              }

              if (cell instanceof ParentGroup) {
                if (!cell.isCollapsed()) {
                  collapse(cell);
                }
              }
            });
          }
        };

        collapse(node);
      });
    },
    build() {
      this.graph = new Graph({
        container: document.getElementById('container'),
        grid: true,
        autoResize: true,
        panning: true,
        translating: {
          restrict(view) {
            const { cell } = view;
            if (cell.isNode()) {
              const parent = cell.getParent();
              if (parent) {
                return parent.getBBox();
              }
            }

            return null;
          },
        },
        // width: "100%",
        // height: "100%",
      });
      this.buildFrame();
      this.buildEvent();
      // this.graph.centerContent();
    },
    init() {
      this.build();
    },
  },
};
</script>

<style>
    @import './index.css';
</style>
