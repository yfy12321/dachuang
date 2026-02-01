<template>
  <div class="app-container">
    <!-- 顶部标题栏 -->
    <div class="top-bar">
      <div class="logo-section">
        <div class="logo-icon">⚡</div>
        <h1>HUST—Forecast 智能电力预测系统</h1>
      </div>
      <div class="status-indicator">
        <div class="status-dot"></div>
        <span>系统运行正常</span>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧导航栏 -->
      <div class="nav-bar">
        <div class="nav-header">
          <h3>功能导航</h3>
          <div class="nav-decoration"></div>
        </div>
        <ul class="nav-list">
          <li
            :class="currentView === 'functions' ? 'active-nav' : 'default-nav'"
            @click="showFunctions"
          >
            <span class="nav-icon">🏠</span>
            <span class="nav-text">功能列表</span>
          </li>
          
          <li
            :class="currentView === 'stations' ? 'active-nav' : 'default-nav'"
            @click="showStations"
          >
            <span class="nav-icon">🏭</span>
            <span class="nav-text">场站列表</span>
          </li>
          <li
            
            :class="currentView === 'prediction' ? 'active-nav' : 'default-nav'"
            @click="showPrediction"
          >
            <span class="nav-icon">📊</span>
            <span class="nav-text">预测结果</span>
          </li>
          <li
            :class="currentView === 'train' ? 'active-nav' : 'default-nav'"
            @click="showTrain"
          >
            <span class="nav-icon">🤖</span>
            <span class="nav-text">模型训练</span>
          </li>
          <li
            :class="currentView === 'trainList' ? 'active-nav' : 'default-nav'"
            @click="showTrainList"
          >
            <span class="nav-icon">📋</span>
            <span class="nav-text">训练任务</span>
          </li>
        </ul>
      </div>

      <!-- 场站列表 -->
      <div
        v-if="currentView === 'stations'"
        class="station-list"
      >
        <div class="station-header">
          <button @click="showFunctions" class="back-btn">
            <span>←</span>
          </button>
          <h3>场站列表</h3>
          <div class="station-count">共 {{ stations.length }} 个场站</div>
        </div>
        <div class="station-scroll">
          <ul class="station-items">
            <li
              v-for="station in stations"
              :key="station.id"
              :class="selectedStationId === station.id ? 'station-item active' : 'station-item'"
              @click="selectStation(station.id)"
            >
              <div class="station-icon">🏭</div>
              <div class="station-info">
                <div class="station-name">{{ station.station_name }}</div>
                <div class="station-id">ID: {{ station.id }}</div>
              </div>
              <div class="station-arrow">→</div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 预测结果页面（美化后） -->
      <div
        v-if="currentView === 'prediction'"
        class="prediction-list"
      >
        <!-- 标题栏：增加视觉层次与数据提示 -->
        <div class="prediction-header">
          <button @click="showFunctions" class="back-btn">
            <span>←</span>
          </button>
          <div class="header-title-group">
            <h3>预测结果管理</h3>
          </div>
          <div class="prediction-count">
            <span class="count-icon">📊</span>
            <span class="count-text">共 {{ predictions.length }} 个预测场站</span>
          </div>
        </div>

        <!-- 加载状态：美化动画 -->
        <div v-if="isLoadingPredictions" class="list-loading prediction-loading">
          <div class="loading-spinner prediction-spinner"></div>
          <p class="loading-text">正在加载最新预测数据...</p>
        </div>

        <!-- 错误状态：卡片式提示 -->
        <div v-else-if="predictionError" class="list-error prediction-error">
          <div class="error-card">
            <div class="error-icon">⚠️</div>
            <h4 class="error-title">获取预测结果失败</h4>
            <p class="error-desc">{{ predictionError }}</p>
            <button @click="fetchPredictions" class="retry-btn prediction-retry">
              <span>刷新重试</span>
              <span class="refresh-icon">🔄</span>
            </button>
          </div>
        </div>

        <!-- 空状态：场景化引导 -->
        <div v-else-if="predictions.length === 0" class="empty-state prediction-empty">
          <div class="empty-card">
            <div class="empty-icon prediction-empty-icon">📊</div>
            <h3>暂无预测数据</h3>
            <p class="empty-desc">当前暂无已生成的光伏/风电预测结果</p>
            <p class="empty-tip">提示：请先在「场站管理」中触发预测任务</p>
          </div>
        </div>

        <!-- 预测列表内容：美化列表项 + 补充业务字段 -->
        <div v-else class="prediction-scroll">
          <ul class="prediction-items">
            <li
              v-for="prediction in predictions"
              :key="prediction.id"
              class="prediction-item"
              :class="selectedPredictionId === prediction.id ? 'prediction-item-selected' : ''"
              @click="selectPrediction(prediction)"
              @mouseenter="prediction.hover = true"
              @mouseleave="prediction.hover = false"
            >
              <!-- 预测类型图标（光伏/风电区分） -->
              <div 
                class="prediction-icon"
                :class="prediction.type.includes('光伏') ? 'solar-icon' : 'wind-icon'"
              >
                {{ prediction.type.includes('光伏') ? '☀️' : '🌬️' }}
              </div>

              <!-- 核心信息区：补充预测精度 -->
              <div class="prediction-info">
                <div class="prediction-name">{{ prediction.name }}</div>
                <div class="prediction-meta">
                  <span class="prediction-type">
                    {{ prediction.type }}
                    <span class="type-tag" :class="prediction.type.includes('光伏') ? 'solar-tag' : 'wind-tag'">
                      {{ prediction.type.includes('光伏') ? 'SOLAR' : 'WIND' }}
                    </span>
                  </span>
                  <span class="prediction-accuracy">
                    精度：{{ prediction.accuracy || '--' }}%
                    <span class="accuracy-icon" :class="prediction.accuracy >= 90 ? 'high-accuracy' : 'normal-accuracy'">
                      {{ prediction.accuracy >= 90 ? '⭐' : '✓' }}
                    </span>
                  </span>
                </div>
              </div>

              <!-- 箭头与选中标识 -->
              <div class="prediction-action">
                <div class="prediction-arrow" :class="prediction.hover ? 'arrow-hover' : ''">→</div>
                <div class="selected-dot" v-if="selectedPredictionId === prediction.id"></div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content-area">
        <!-- 模型训练页面 -->
        <div v-if="currentView === 'train'" class="train-page">
          <TrainModel />
        </div>

        <!-- 训练任务列表页面 -->
        <div v-else-if="currentView === 'trainList'" class="train-list-page">
          <TrainTaskList />
        </div>

        <!-- 功能列表页面 -->
        <div v-else-if="currentView === 'functions'" class="welcome-section">
          <!-- 装饰性背景元素 -->
          <div class="bg-decorations">
            <div class="decoration decoration-1"></div>
            <div class="decoration decoration-2"></div>
            <div class="decoration decoration-3"></div>
          </div>
          
          <div class="welcome-hero">
            <div class="hero-icon">⚡</div>
            <h2>欢迎使用电力预测系统</h2>
            <p class="hero-subtitle">智能化电力预测，精准把控能源未来</p>
          </div>
          
          <div class="function-grid">
            <div class="function-card" v-for="func in functions" :key="func.id">
              <div class="func-icon">{{ func.icon }}</div>
              <h3>{{ func.title }}</h3>
              <p>{{ func.description }}</p>
              <div class="func-badge" @click="func.onClick && func.onClick()">{{ func.badge }}</div>
            </div>
          </div>
          
          <div class="action-prompt">
            <div class="prompt-icon">👈</div>
            <p>点击左侧"场站列表"开始使用系统功能</p>
          </div>
        </div>

        <div v-else-if="currentView === 'stations' && selectedStationId" class="detail-section">
          <div class="detail-header">
            <button @click="showStations" class="back-btn">
              <span>←</span>
            </button>
            <h2>场站详情</h2>
            <div class="detail-actions">
             
              <button class="action-btn secondary">⚙️ 设置</button>
            </div>
          </div>
          
          <div v-if="detail" class="detail-content">
            <div class="detail-card station-overview">
              <div class="card-header">
                <div class="station-avatar">🏭</div>
                <div class="station-meta">
                  <h3>{{ detail.name }}</h3>
                  <div class="station-tags">
                    <span class="tag primary">活跃</span>
                    <span class="tag secondary">ID: {{ detail.id }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="info-grid">
              <!-- 基本信息 -->
              <div class="detail-card">
                <div class="card-header">
                  <h4>📋 基本信息</h4>
                </div>
                <div class="info-items">
                  <div class="info-item">
                    <span class="info-label">机组配置</span>
                    <span class="info-value">{{ detail.unit_config || '暂无数据' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">装机容量</span>
                    <span class="info-value highlight">{{ detail.installed_capacity || '暂无数据' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">覆盖面积</span>
                    <span class="info-value">{{ detail.area_km2 ? detail.area_km2 + ' km²' : '暂无数据' }}</span>
                  </div>
                </div>
              </div>

              <!-- 地理信息 -->
              <div class="detail-card">
                <div class="card-header">
                  <h4>🌍 地理信息</h4>
                </div>
                <div class="info-items">
                  <div class="info-item">
                    <span class="info-label">纬度</span>
                    <span class="info-value">{{ detail.latitude || '暂无数据' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">经度</span>
                    <span class="info-value">{{ detail.longitude || '暂无数据' }}</span>
                  </div>
                  <div class="location-map">
                    <div class="map-placeholder">
                      <span>🗺️</span>
                      <p>地理位置可视化</p>
                      <Map></Map>
                      <!-- <A></A> --- IGNORE --- -->
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 预测规则 -->
            <div class="detail-card rules-card">
              <div class="card-header">
                <h4>🤖 预测规则配置</h4>
              </div>
              <div class="rules-grid">
                <div class="rule-item ultra-short">
                  <div class="rule-header">
                    <div class="rule-icon">⚡</div>
                    <div class="rule-info">
                      <h5>超短期预测</h5>
                      <span class="rule-period">4小时预测</span>
                    </div>
                  </div>
                  <div class="rule-content">
                    <p>{{ detail.ultra_short_term_rule || '暂无配置规则' }}</p>
                  </div>
                </div>
                
                <div class="rule-item day-ahead">
                  <div class="rule-header">
                    <div class="rule-icon">🌅</div>
                    <div class="rule-info">
                      <h5>日前预测</h5>
                      <span class="rule-period">24小时预测</span>
                    </div>
                  </div>
                  <div class="rule-content">
                    <p>{{ detail.day_ahead_rule || '暂无配置规则' }}</p>
                  </div>
                </div>
                
                <div class="rule-item mid-long">
                  <div class="rule-header">
                    <div class="rule-icon">📈</div>
                    <div class="rule-info">
                      <h5>中长期预测</h5>
                      <span class="rule-period">7天预测</span>
                    </div>
                  </div>
                  <div class="rule-content">
                    <p>{{ detail.mid_long_term_rule || '暂无配置规则' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载场站详情...</p>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">🏭</div>
          <h3>请选择场站</h3>
          <p>从左侧列表中选择一个场站查看详细信息</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import A from './components/a.vue'
import Map from './components/Map.vue'
import TrainModel from './components/TrainModel.vue'
import TrainTaskList from './components/TrainTaskList.vue'
import ModelPrediction from './components/ModelPrediction.vue' 
const stations = ref([])
const selectedStationId = ref(null)
const detail = ref(null)
const currentView = ref('functions')

const goToReport = (stationName) => {
  // 方式1：直接跳转到 Django 的 dashboard URL（绝对路径）
  window.location.href = `http://localhost:8000/station-report/${stationName}/`;
}

const navigateToCoreFunction = () => {  // 使用模板字符串正确拼接URL
  window.location.href = 'http://localhost:8000/core-function/';
}

const showFunctions = () => {
  currentView.value = 'functions'
  selectedStationId.value = null
  detail.value = null
}

const showStations = () => {
  currentView.value = 'stations'
  selectedStationId.value = null
  detail.value = null
}

const showTrain = () => {
  currentView.value = 'train'
  selectedStationId.value = null
  detail.value = null
}

const showTrainList = () => {
  currentView.value = 'trainList'
  selectedStationId.value = null
  detail.value = null
}

const showPrediction = () => {
  currentView.value = 'modelPrediction'
  selectedStationId.value = null
  detail.value = null
}

const functions = ref([
  {
    id: 1,
    icon: '🏭',
    title: '场站管理',
    description: '查看和管理所有电力场站信息，实时监控运行状态',
    badge: '核心功能',
    onClick: navigateToCoreFunction
  },
  {
    id: 2,
    icon: '🤖',
    title: '模型训练',
    description: '配置训练参数，启动模型训练任务',
    badge: 'AI智能',
    onClick: showTrain
  },
  {
    id: 3,
    icon: '📋',
    title: '训练任务',
    description: '查看和管理所有训练任务，监控训练状态',
    badge: '任务管理',
    onClick: showTrainList
  },
  {
    id: 4,
    icon: '⚡',
    title: '容量管理',
    description: '管理场站机组配置和装机容量信息',
    badge: '容量优化'
  }
])

const fetchStations = async () => {
  try {
    const res = await fetch('/tables/api/stations/')
    if (res.ok) {
      stations.value = await res.json()
    } else {
      const errorData = await res.json().catch(() => ({ error: `HTTP ${res.status}` }))
      console.error('获取场站列表失败:', res.status, errorData)
    }
  } catch (error) {
    console.error('获取场站列表出错:', error)
    // 静默处理错误，避免未捕获的Promise
  }
}

const fetchDetail = async (id) => {
  try {
    const res = await fetch(`/tables/api/stations/${id}/`);
    if (res.ok) {
      detail.value = await res.json()
    } else {
      const errorData = await res.json().catch(() => ({ error: `HTTP ${res.status}` }))
      console.error('获取场站详情失败:', res.status, errorData)
    }
  } catch (error) {
    console.error('获取场站详情出错:', error)
    // 静默处理错误，避免未捕获的Promise
  }
}

const selectStation = (id) => {
  selectedStationId.value = id
  fetchDetail(id)
}

// 预测结果相关：新增美化所需变量与优化函数
const predictions = ref([])
const selectedPredictionId = ref(null)
const isLoadingPredictions = ref(false) // 新增加载状态
const predictionError = ref('') // 新增错误状态

// 添加导航函数
const showPrediction = () => {
  currentView.value = 'prediction'
  selectedStationId.value = null
  selectedPredictionId.value = null
  detail.value = null
  fetchPredictions() // 切换到预测页面时主动加载数据
}


// 修改 fetchPredictions 方法中的预测数据
const fetchPredictions = async () => {
  isLoadingPredictions.value = true;
  predictionError.value = '';
  try {
    predictions.value = [
      { 
        id: 1, 
        name: '新乐凤鸣光伏电站', 
        type: '光伏预测', 
        accuracy: 92.5,
        // 修改URL指向Django仪表板
        url: 'http://localhost:8000/power-dashboard/?station=新乐凤鸣光伏电站&type=solar',
        hover: false
      },
      { 
        id: 2, 
        name: '巨鹿腾煌风电场站', 
        type: '风电预测', 
        accuracy: 88.3,
        // 修改URL指向Django仪表板
        url: 'http://localhost:8000/power-dashboard/?station=巨鹿腾煌风电场站&type=wind',
        hover: false
      }
    ];
  } catch (error) {
    predictionError.value = `请求超时或接口异常（${error.message}）`;
    console.error('获取预测列表出错:', error);
  } finally {
    isLoadingPredictions.value = false;
  }
}




// 优化预测选择逻辑：增加选中状态与错误处理
const selectPrediction = (prediction) => {
  selectedPredictionId.value = prediction.id;
  
  // 根据预测类型和名称构建正确的URL
  let dashboardUrl;
  
  if (prediction.type.includes('光伏')) {
    // 光伏场站跳转到光伏仪表板
    dashboardUrl = `http://localhost:8000/power-dashboard/?station=${encodeURIComponent(prediction.name)}&type=solar`;
  } else if (prediction.type.includes('风电')) {
    // 风电场站跳转到风电仪表板
    dashboardUrl = `http://localhost:8000/power-dashboard/?station=${encodeURIComponent(prediction.name)}&type=wind`;
  } else {
    alert('未知的场站类型');
    return;
  }
  
  try {
    const newTab = window.open(dashboardUrl, '_blank');
    if (!newTab) {
      alert('浏览器阻止了弹窗，请允许弹出窗口后重试！');
    }
  } catch (error) {
    alert(`跳转仪表板失败：${error.message}`);
    console.error('仪表板跳转错误:', error);
  }
}

// 在onMounted中添加fetchPredictions调用
onMounted(() => {
  fetchStations()
  fetchPredictions()
})
</script>

<style>
/* 全局样式重置 - 确保铺满屏幕且无滚动条 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}
</style>
<style>
/* 全局样式重置 - 确保铺满屏幕且无滚动条 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

#app {
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8, #6a42a0);
}
</style>

<style scoped>
.app-container {
  position:fixed;
  top:0;
  bottom:0;
  left:0;
  right:0;
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  overflow: hidden;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 顶部标题栏 */
.top-bar {
  height: 70px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(30px);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.5) inset;
  z-index: 1000;
  position: relative;
}

.top-bar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
  opacity: 0.3;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4), 0 0 0 3px rgba(102, 126, 234, 0.1);
  animation: pulse-glow 3s ease-in-out infinite;
  position: relative;
}

.logo-icon::before {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.3;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4), 0 0 0 3px rgba(102, 126, 234, 0.1); }
  50% { box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6), 0 0 0 5px rgba(102, 126, 234, 0.15); }
}

.top-bar h1 {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #2c3e50 0%, #667eea 50%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #27ae60;
  font-size: 14px;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #27ae60;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.main-content {
  flex: 1;
  display: flex;
  width: 100%;
  overflow: hidden;
}

/* 左侧导航栏 */
.nav-bar {
  width: 240px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(30px);
  border-right: 1px solid rgba(102, 126, 234, 0.1);
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 30px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 100;
}

.nav-bar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, #667eea, #764ba2, transparent);
  opacity: 0.3;
}

.nav-header {
  padding: 24px 16px 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.nav-header h3 {
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.nav-decoration {
  width: 40px;
  height: 3px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 2px;
}

.nav-list {
  list-style: none;
  padding: 16px;
  flex: 1;
}

.nav-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  margin: 6px 0;
  border-radius: 12px;
  font-weight: 500;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.active-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4), 0 1px 0 rgba(255, 255, 255, 0.2) inset;
  transform: translateX(4px);
}

.active-nav::before {
  transform: scaleY(1) !important;
}

.default-nav {
  background: transparent;
  color: #2c3e50;
}

.default-nav:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
  transform: translateX(6px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.default-nav:hover::before {
  transform: scaleY(0.6);
}

.sub-nav {
  background: rgba(102, 126, 234, 0.1) !important;
  border: 1px solid rgba(102, 126, 234, 0.2);
  margin-left: 0px;
}

/* 场站列表 */
.station-list {
  width: 320px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
}

.station-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 16px 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.station-header h3 {
  flex: 1;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.station-count {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.station-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.station-items {
  list-style: none;
}

.station-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  margin: 10px 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.1);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.station-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.station-item:hover::before {
  opacity: 1;
}

.station-item:hover {
  transform: translateY(-3px) translateX(3px);
  box-shadow: 0 10px 35px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.station-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4), 0 1px 0 rgba(255, 255, 255, 0.2) inset;
  transform: scale(1.03) translateX(5px);
}

.station-item.active::before {
  opacity: 0;
}

.station-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.station-item.active .station-icon {
  background: rgba(255, 255, 255, 0.2);
}

.station-info {
  flex: 1;
}

.station-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.station-id {
  font-size: 12px;
  opacity: 0.7;
}

.station-arrow {
  font-size: 14px;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.station-item:hover .station-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.back-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3), 0 1px 0 rgba(255, 255, 255, 0.2) inset;
  position: relative;
  overflow: hidden;
}

.back-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.3), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.back-btn:hover::before {
  opacity: 1;
}

.back-btn:hover {
  transform: scale(1.15) rotate(-5deg);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5), 0 1px 0 rgba(255, 255, 255, 0.3) inset;
}

.back-btn:active {
  transform: scale(1.05);
}

/* 内容区域 */
.content-area {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 24px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  position: relative;
}

.content-area::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.05), transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.05), transparent 50%);
  pointer-events: none;
}

/* 欢迎页面 */
.welcome-section {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: relative;
  overflow: hidden;
}

/* 装饰性背景元素 */
.bg-decorations {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.decoration {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1), transparent);
  animation: float-decoration 20s ease-in-out infinite;
}

.decoration-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: 5%;
  animation-delay: 0s;
}

.decoration-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: 10%;
  animation-delay: 5s;
}

.decoration-3 {
  width: 250px;
  height: 250px;
  bottom: 10%;
  left: 50%;
  animation-delay: 10s;
}

@keyframes float-decoration {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.3;
  }
  25% {
    transform: translate(30px, -30px) scale(1.1);
    opacity: 0.5;
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
    opacity: 0.4;
  }
  75% {
    transform: translate(40px, 10px) scale(1.05);
    opacity: 0.45;
  }
}

.welcome-hero {
  text-align: center;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.hero-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: white;
  margin: 0 auto 24px;
  box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4), 0 0 0 10px rgba(102, 126, 234, 0.1), 0 0 0 20px rgba(102, 126, 234, 0.05);
  animation: float 3s ease-in-out infinite, rotate-slow 20s linear infinite;
  position: relative;
}

.hero-icon::before {
  content: '';
  position: absolute;
  inset: -10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0.2;
  animation: pulse-ring 2s ease-out infinite;
}

@keyframes rotate-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.2; }
  50% { transform: scale(1.1); opacity: 0.1; }
  100% { transform: scale(1.2); opacity: 0; }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.welcome-hero h2 {
  color: #2c3e50;
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #2c3e50 0%, #667eea 50%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: title-shine 3s ease-in-out infinite;
}

@keyframes title-shine {
  0%, 100% { 
    filter: brightness(1);
  }
  50% { 
    filter: brightness(1.2);
  }
}

.hero-subtitle {
  color: #7f8c8d;
  font-size: 18px;
  font-weight: 400;
  opacity: 0;
  animation: fade-in-up 0.8s ease-out 0.3s forwards;
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.function-grid {
  display: grid;
  grid-template-columns:repeat(3,1fr);
  flex-direction: row;
  gap: 50px;
  padding:50px;
  width:100%;
  overflow-x: auto;
  padding-bottom: 16px;
  margin:0 auto;
  position: relative;
  z-index: 1;
}

.function-card {
  flex: 0 0 240px;
  background: rgba(255, 255, 255, 0.95);
  padding: 32px 28px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.8) inset;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.function-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.function-card::after {
  content: '';
  position: absolute;
  inset: -100%;
  background: radial-gradient(circle at center, rgba(102, 126, 234, 0.1), transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.function-card:hover::after {
  opacity: 1;
}

.function-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25), 0 1px 0 rgba(255, 255, 255, 0.9) inset;
  border-color: rgba(102, 126, 234, 0.3);
}

.func-icon {
  font-size: 48px;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.2));
  transition: all 0.3s ease;
}

.function-card:hover .func-icon {
  transform: scale(1.15) rotate(5deg);
  filter: drop-shadow(0 6px 20px rgba(102, 126, 234, 0.4));
}

.function-card h3 {
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.function-card p {
  color: #7f8c8d;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
  flex-grow :1;
}

.func-badge {
  align-self: flex-start;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.func-badge:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 点击瞬间效果：轻微缩小 */
.func-badge:active {
  transform: translateY(-1px) scale(0.98);
}

.action-prompt {
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 28px 32px;
  border-radius: 20px;
  border: 2px dashed rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.action-prompt:hover {
  border-color: rgba(102, 126, 234, 0.5);
  transform: scale(1.02);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
}

.action-prompt p {
  font-size: 16px;
  color: #667eea;
  font-weight: 500;
  margin: 0;
}

.prompt-icon {
  font-size: 40px;
  margin-bottom: 12px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateX(0); }
  40% { transform: translateX(-8px); }
  60% { transform: translateX(-4px); }
}

/* 详情页面 */
.detail-section {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-header h2 {
  flex: 1;
  color: #2c3e50;
  font-size: 26px;
  font-weight: 600;
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.action-btn:hover::before {
  transform: translateX(0);
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3), 0 1px 0 rgba(255, 255, 255, 0.2) inset;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: 2px solid rgba(102, 126, 234, 0.2);
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.action-btn:active {
  transform: translateY(-1px);
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.8) inset;
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.detail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 50px rgba(102, 126, 234, 0.15), 0 1px 0 rgba(255, 255, 255, 0.9) inset;
}

.station-overview {
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.station-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.station-meta h3 {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 6px;
}

.station-tags {
  display: flex;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 500;
}

.tag.primary {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
}

.tag.secondary {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.detail-card h4 {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  padding: 0 24px 12px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.info-items {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(102, 126, 234, 0.05);
}

.info-label {
  color: #7f8c8d;
  font-size: 13px;
  font-weight: 500;
}

.info-value {
  color: #2c3e50;
  font-size: 14px;
  font-weight: 600;
}

.info-value.highlight {
  background: linear-gradient(135deg, #667eea, #764ba2);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.location-map {
  margin-top: 20px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 10px;
  height: 250px;
  border-radius: 12px;
  overflow: hidden;
}

.chart-section {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px 24px;
}

.rule-item {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  padding: 24px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.rule-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.rule-item:hover::before {
  transform: scaleY(1);
}

.rule-item:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.rule-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.rule-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.rule-info h5 {
  color: #2c3e50;
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.rule-period {
  color: #7f8c8d;
  font-size: 11px;
  font-weight: 500;
}

.rule-content p {
  color: #2c3e50;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #7f8c8d;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.15);
  border-top-color: #667eea;
  border-right-color: #764ba2;
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
  position: relative;
}

.loading-spinner::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: rgba(102, 126, 234, 0.2);
  animation: spin 1.5s linear infinite reverse;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #2c3e50;
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 12px;
}

.empty-state p {
  color: #7f8c8d;
  font-size: 15px;
}

/* 预测结果页面：新增美化样式 */
.prediction-list {
  width: 320px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

/* 预测结果标题栏美化 */
.prediction-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  background: linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(245,247,250,0.9) 100%);
}

.header-title-group {
  flex: 1;
}

.header-title-group h3 {
  color: #2c3e50;
  font-size: 19px;
  font-weight: 600;
  margin: 0;
}

.prediction-count {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.count-icon {
  font-size: 16px;
}

/* 加载状态美化 */
.prediction-loading {
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.prediction-spinner {
  width: 40px;
  height: 40px;
  border: 5px solid rgba(102, 126, 234, 0.1);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 16px;
  font-size: 14px;
  color: #667eea;
  font-weight: 500;
}

/* 错误状态美化 */
.prediction-error {
  padding: 40px 20px;
}

.error-card {
  width: 100%;
  background: white;
  border-radius: 16px;
  padding: 30px 20px;
  text-align: center;
  border: 1px solid rgba(231, 76, 60, 0.1);
  box-shadow: 0 6px 20px rgba(231, 76, 60, 0.05);
}

.error-icon {
  font-size: 48px;
  color: #e74c3c;
  margin-bottom: 12px;
}

.error-title {
  color: #e74c3c;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.error-desc {
  color: #7f8c8d;
  font-size: 13px;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.prediction-retry {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  padding: 9px 22px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 auto;
  cursor: pointer;
  transition: all 0.3s ease;
}

.prediction-retry:hover {
  background: linear-gradient(135deg, #c0392b, #a52c1d);
  box-shadow: 0 6px 15px rgba(231, 76, 60, 0.2);
}

/* 空状态美化 */
.prediction-empty {
  padding: 60px 20px;
}

.empty-card {
  width: 100%;
  background: white;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.05);
}

.prediction-empty-icon {
  font-size: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 20px;
}

.empty-desc {
  color: #7f8c8d;
  font-size: 14px;
  margin: 8px 0 0 0;
}

.empty-tip {
  color: #95a5a6;
  font-size: 12px;
  margin: 12px 0 0 0;
  font-style: italic;
}

/* 预测列表项美化 */
.prediction-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.prediction-items {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prediction-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 16px;
  background: white;
  border: 2px solid rgba(220, 220, 220, 0.3);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.prediction-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03), rgba(118, 75, 162, 0.03));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.prediction-item:hover::before {
  opacity: 1;
}

/* 列表项hover动画 */
.prediction-item:hover {
  transform: translateY(-4px) translateX(2px);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

/* 列表项选中状态 */
.prediction-item-selected {
  border-color: rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2), 0 1px 0 rgba(255, 255, 255, 0.5) inset;
  transform: scale(1.02);
}

/* 光伏/风电图标区分 */
.prediction-icon {
  font-size: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

/* 光伏图标样式 */
.solar-icon {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 165, 0, 0.1) 100%);
  color: #f39c12;
  border: 1px solid rgba(255, 165, 0, 0.2);
}

.prediction-item:hover .solar-icon {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
  transform: scale(1.1);
}

/* 风电图标样式 */
.wind-icon {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, rgba(41, 128, 185, 0.1) 100%);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.prediction-item:hover .wind-icon {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  transform: scale(1.1);
}

/* 信息区样式 */
.prediction-info {
  flex: 1;
  overflow: hidden;
}

.prediction-name {
  font-weight: 600;
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prediction-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.prediction-type {
  font-size: 13px;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 光伏/风电标签区分 */
.type-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.solar-tag {
  background: rgba(243, 156, 18, 0.15);
  color: #e67e22;
}

.wind-tag {
  background: rgba(52, 152, 219, 0.15);
  color: #2980b9;
}

/* 预测精度样式 */
.prediction-accuracy {
  font-size: 13px;
  color: #27ae60;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.high-accuracy {
  color: #f1c40f;
  font-size: 14px;
}

.normal-accuracy {
  color: #27ae60;
  font-size: 14px;
}

/* 箭头与选中标识 */
.prediction-action {
  display: flex;
  align-items: center;
  gap: 8px;
}

.prediction-arrow {
  font-size: 16px;
  color: #bdc3c7;
  transition: all 0.3s ease;
}

.arrow-hover {
  color: #667eea;
  transform: translateX(4px);
}

/* 选中圆点标识 */
.selected-dot {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.prediction-item-selected .selected-dot {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-bar {
    width: 100%;
    position: absolute;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  .nav-bar.active {
    transform: translateX(0);
  }
  .station-list, .prediction-list {
    width: 100%;
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
  .function-grid {
    flex-wrap: nowrap;
  }
  .prediction-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>


