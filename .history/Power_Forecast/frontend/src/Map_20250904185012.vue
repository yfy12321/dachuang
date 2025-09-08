<template>
  <div id="container"></div>
</template>
<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";

// 位置数据
const markersData = ref([
  {
    id: 1,
    lng: '114.4',
    title: "新乐凤鸣光伏场站",
    lat: '37.65',
    description: "河北省石家庄凤鸣",
  },
  {
    id: 2,
    lng: '115.07',
    lat: '37.33',
    title: "巨鹿腾煌风电场",
    description: "位于河北省邢台市巨鹿县",
  }
]);

let map = null;
let infoWindow = null; // 信息窗口实例

onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: "15c4bf5c576137c14c60312f4075f417",
  };
  
  AMapLoader.load({
    key: "16a9fbdb5e335e784feaff3d012b76fe", // 开发者Key
    version: "2.0", // SAPI 的版本
    plugins: ["AMap.Scale", "AMap.Marker", "AMap.InfoWindow"], // 添加需要的插件
  })
  .then((AMap) => {
    // 初始化地图
    map = new AMap.Map("container", {
      viewMode: "3D",
      zoom: 8, // 调整缩放级别以同时看到两个点
      center: [114.735, 37.49], // 调整中心点到两个点之间
    });

    // 创建信息窗口
    infoWindow = new AMap.InfoWindow({
      offset: new AMap.Pixel(0, -30) // 信息窗口偏移量，避免遮挡标记点
    });

    // 添加标记点
    markersData.value.forEach(marker => {
      // 创建标记点
      const markerObj = new AMap.Marker({
        position: [marker.lng, marker.lat], // 位置
        title: marker.title,
        map: map, // 添加到地图
        icon: new AMap.Icon({
          size: new AMap.Size(32, 32), // 图标大小
          image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_bs.png',
        }),
        anchor: 'bottom-center' // 锚点位置
      });

      // 给标记点添加点击事件
      markerObj.on('click', () => {
        // 设置信息窗口内容
        const content = `
          <div style="padding: 10px;">
            <h3 style="margin: 0 0 10px 0; color: #333;">${marker.title}</h3>
            <p style="margin: 5px 0; font-size: 14px;">经纬度: ${marker.lng}, ${marker.lat}</p>
            <p style="margin: 5px 0; font-size: 14px;">${marker.description}</p>
          </div>
        `;
        
        // 打开信息窗口
        infoWindow.setContent(content);
        infoWindow.open(map, [marker.lng, marker.lat]);
      });
    });
  })
  .catch((e) => {
    console.log(e);
  });
});

onUnmounted(() => {
  if (map) {
    map.destroy();
    map = null;
  }
  infoWindow = null;
});
</script>

<style scoped>
#container {
  width: 100%;
  height: 500px; /* 增加高度以便更好地查看地图 */
}
</style>

