<template>
  <div class="map-location-display">
    <header>
      <h1>地图位置展示</h1>
      <p class="subtitle">
        新乐凤鸣光伏场站与巨鹿腾煌风电场地的位置及经纬度信息
      </p >
    </header>

    <div class="container">
      <div id="map" ref="mapContainer"></div>

    </div>

    <footer>
      <p>© 2023 地图位置展示 | 使用Leaflet.js制作</p >
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// 地图引用
const mapContainer = ref(null);
let map = null;
let markerA = null;
let markerB = null;
let line = null;

// 位置数据
const locations = {
  a: {
    name: "新乐凤鸣光伏场站",
    coords: [38.03, 114.29],
    description: "河北省石家庄凤鸣",
  },
  b: {
    name: "巨鹿腾煌风电场",
    coords: [36.50, 115.07],
    description: "位于河北省邢台市巨鹿县",
  },
};

// 初始化地图
const initMap = async () => {
  if (!mapContainer.value) return;

  // 等待DOM更新完成
  await nextTick();

  // 检查容器尺寸
  const container = mapContainer.value;
  if (container.offsetWidth === 0 || container.offsetHeight === 0) {
    // 如果容器尺寸为0，延迟初始化
    setTimeout(initMap, 100);
    return;
  }

  map = L.map(container).setView([37.5, 114.7], 9);

  // 添加图片图层
  const imageUrl =
    "https://3wt.img.zhangtiandi.cn/2025/08-23/19d4621e4d104f66ae06eae59fc2dff83wcn766371.jpeg";
  const imageBounds = [
    [-90, -180],
    [90, 180],
  ];

  L.imageOverlay(imageUrl, imageBounds, {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  addMarkers();
  addConnectionLine();
  addLegend();
  adjustMapView();

  // 监听窗口大小变化
  window.addEventListener("resize", handleResize);
};

// 处理窗口大小变化
const handleResize = () => {
  if (map) {
    map.invalidateSize();
  }
};


const createCustomIcon = (iconUrl, iconSize = [40, 40], iconAnchor = [20, 40], popupAnchor = [0, -40]) => {
  return L.icon({
    iconUrl: iconUrl,
    iconSize: iconSize,      // 图标的尺寸 [宽, 高]
    iconAnchor: iconAnchor,  // 图标尖端对应的坐标点 [x, y]
    popupAnchor: popupAnchor // 弹出窗口相对于图标尖端的偏移量 [x, y]
  });
};

// 修改 addMarkers 函数
const addMarkers = () => {
  // 为光伏场站创建一个图标 (例如，一个太阳的图标)
  const iconA = createCustomIcon(
    'https://cdn-icons-png.flaticon.com/512/979/979585.png', // 太阳图标 URL
    [40, 40],
    [20, 40],
    [0, -40]
  );

  // 为风电场创建一个图标 (例如，一个风车的图标)
  const iconB = createCustomIcon(
    'https://edit-upload-pic.cdn.bcebos.com/7f83f62ccb58c67177c4493af1df9bbe.jpeg?authorization=bce-auth-v1%2FALTAKh1mxHnNIyeO93hiasKJqq%2F2025-08-29T03%3A57%3A30Z%2F3600%2Fhost%2F125e187ab0c95832539082a5d8e38ca11da8d3fc1803ae3b016416f81fabd11c', // 风车图标 URL
    [40, 40],
    [20, 40],
    [0, -40]
  );

  markerA = L.marker(locations.a.coords, { icon: iconA }).addTo(map).bindPopup(`
      <div style="text-align: center;">
        <h3 style="font-size: 24px;">${locations.a.name}</h3>
        <p style="font-size: 18px;">${locations.a.description}</p >
        <p style="font-size: 18px;">经纬度: ${locations.a.coords[1]}° E,${locations.a.coords[0]}° N</p >
      </div>
    `);

  markerB = L.marker(locations.b.coords, { icon: iconB }).addTo(map).bindPopup(`
      <div style="text-align: center;">
        <h3 style="font-size: 24px;">${locations.b.name}</h3>
        <p style="font-size: 18px;">${locations.b.description}</p >
        <p style="font-size: 18px;">经纬度: ${locations.b.coords[1]}° E,${locations.b.coords[0]}° N</p >
      </div>
    `);
};




// 添加连接线
const addConnectionLine = () => {
  line = L.polyline([locations.a.coords, locations.b.coords], {
    color: "#3498db",
    weight: 3,
    dashArray: "5, 10",
  }).addTo(map);
};

// 添加图例
const addLegend = () => {
  const legend = L.control({ position: "bottomright" });

  legend.onAdd = () => {
    const div = L.DomUtil.create("div", "legend");
    div.innerHTML = `
      <h4>图例</h4>
      <div class="legend-item">
        <div class="legend-color legend-a"></div>
        <span>${locations.a.name}</span>
      </div>
      <div class="legend-item">
        <div class="legend-color legend-b"></div>
        <span>${locations.b.name}</span>
      </div>
    `;
    return div;
  };

  legend.addTo(map);
};

// 调整地图视图
const adjustMapView = () => {
  const bounds = L.latLngBounds([locations.a.coords, locations.b.coords]);
  map.fitBounds(bounds, { padding: [50, 50] });
};

// 清理地图
const cleanupMap = () => {
  if (map) {
    window.removeEventListener("resize", handleResize);
    map.remove();
    map = null;
  }
};

// 生命周期钩子
onMounted(() => {
  initMap();
});

onUnmounted(() => {
  cleanupMap();
});
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.map-location-display {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  color: #333;
}

header {
  background: #2c3e50;
  color: white;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

h1 {
  font-size: clamp(1.5rem, 4vw, 2.2rem);
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: clamp(0.9rem, 2.5vw, 1.1rem);
  opacity: 0.8;
}

.container {
  display: flex;
  flex: 1;
  padding: 20px;
  gap: 20px;
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 768px) {
  .container {
    flex-direction: column;
    padding: 15px;
    gap: 15px;
  }
}

#map {
  flex: 7;
  min-height: 400px;
  height: 100%;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  z-index: 1;
  position: relative;
}

.locations-info {
  flex: 3;
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  display: flex;

  gap: 25px;
  min-height: 0;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .locations-info {
    padding: 20px;
    gap: 20px;
  }
}

.location-card {
  padding: 20px;
  border-radius: 8px;
  color: white;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .location-card {
    padding: 15px;
  }
}

.location-a {
  background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
}

.location-b {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.location-name {
  font-size: 12px;
  font-weight: 600;
}

.coordinates {
  font-family: "Courier New", monospace;
  font-size: clamp(0.9rem, 2.5vw, 1.1rem);
  background: rgba(0, 0, 0, 0.2);
  padding: 8px 12px;
  border-radius: 4px;
  word-break: break-all;
}

.location-details {
  margin-top: 15px;
  font-size: clamp(0.8rem, 2vw, 0.95rem);
  line-height: 1.6;
}

footer {
  text-align: center;
  padding: 20px;
  background: #2c3e50;
  color: white;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  footer {
    padding: 15px;
  }
}

.legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  font-size: 14px;
  max-width: 200px;
}

.legend h4 {
  margin-bottom: 8px;
  font-size: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin: 5px 0;
  font-size: 12px;
}

.legend-color {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-a {
  background: #3498db;
}

.legend-b {
  background: #e74c3c;
}

/* 响应式调整 */
@media (max-width: 480px) {
  header {
    padding: 1rem;
  }

  .container {
    padding: 10px;
    gap: 10px;
  }

  .locations-info {
    padding: 15px;
    gap: 15px;
  }

  .location-card {
    padding: 12px;
  }

  .legend {
    bottom: 10px;
    right: 10px;
padding: 8px;
    font-size: 12px;
  }
}

/* 确保地图容器能够正确显示 */
#map :deep(.leaflet-container) {
  width: 100% !important;
  height: 100% !important;
}

/* 处理小屏幕上的地图显示 */
@media (max-width: 768px) {
  #map {
    min-height: 300px;
  }
}
</style>