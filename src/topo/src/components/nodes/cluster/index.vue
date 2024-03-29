<template>
  <div class="compute-tpl" :class="diff">
    <div class="iaas-image">
      <img class="cloud-icon" :src="'/static/images/tencentcloud_icon/' + device" />
    </div>
    <div class="iaas-desc">
      <span>{{ label }} x {{ typeof raw.count === 'undefined' ? 0 : raw.count }}</span>
    </div>
  </div>
</template>

<script>

export default {
  name: 'Device',
  inject: ['getGraph', 'getNode'],
  data() {
    return {
      status: 'logo',
      imgCot: {},
      label: '',
      device: 'Anti-CheatExpert',
      raw: {},
    };
  },
  computed: {
    imageUrl() {
      return `/static/images/tencentcloud_icon/${this.device}.png`;
    },
    diff() {
      if (this.raw.hasOwnProperty('changes') && this.raw.changes.length !== 0) {
        return 'diff'
      }
      return '';
    },
  },
  mounted() {
    const self = this;
    const node = this.getNode();
    this.label = node.data.label;
    this.device = node.data.device;
    this.raw = node.data.raw;

    // 监听数据改变事件
    node.on('change:data', ({ current }) => {
      self.label = current.label;
      self.status = current.status;
      self.device = current.device;
    });
  },
};
</script>
<style xml:lang="scss" scoped>
  .compute-tpl {
      display: flex;
      min-width: 160px;
      height: 40px;
      border: 2px solid #d4d6dc;
      border-radius: 5px;
      .iaas-image {
          padding-top: 5%;
          padding-left: 5%;
          width: 25%;
          .cloud-icon {
            width: 24px;
            height: 24px;
          }
      }
      .iaas-desc {
          width: 75%;
          padding-top: 5%;
          text-align: center;
          background-color: #f4f5f9;
          border-left: 2px solid #d4d6dc;
          text-wrap: nowrap;
          color: rgb(0, 82, 217);
          font-weight: 600;
          font-size: 14px;
          font-family: "Hiragino Sans GB", Tahoma, "microsoft yahei ui", "microsoft yahei", simsun;
      }
  }
</style>
