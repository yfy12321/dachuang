<template>
  <div class="prediction-container">
    <!-- 背景装饰 -->
    <div class="bg-pattern">
      <div class="pattern-circle circle-1"></div>
      <div class="pattern-circle circle-2"></div>
    </div>

    <!-- 页面头部 -->
    <div class="pred-header">
      <div class="header-icon">🔮</div>
      <div class="header-text">
        <h2>模型预测</h2>
        <p class="subtitle">使用已训练模型进行电力预测</p>
      </div>
    </div>

    <!-- 预测配置卡片 -->
    <div class="config-card">
      <div class="card-title">⚙️ 预测配置</div>
      
      <el-form
        :model="predForm"
        :rules="rules"
        ref="predFormRef"
        label-width="140px"
        label-position="top"
      >
        <div class="form-grid">
          <el-form-item label="选择场站" prop="station_id" class="form-item">
            <el-select
              v-model="predForm.station_id"
              placeholder="请选择场站"
              style="width: 100%"
              @change="handleStationChange"
            >
              <el-option
                v-for="station in stations"
                :key="station.id"
                :label="station.station_name"
                :value="station.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="选择模型" prop="model_id" class="form-item">
            <el-select
              v-model="predForm.model_id"
              placeholder="请选择已训练的模型"
              style="width: 100%"
              :loading="loadingModels"
            >
              <el-option
                v-for="model in availableModels"
                :key="model.id"
                :label="`${model.model_type} - ${model.station_name}`"
                :value="model.id"
              >
                <span>{{ model.model_type }}</span>
                <span style="color: #8492a6; font-size: 12px; margin-left: 8px">
                  精度: {{ model.mape?.toFixed(2) }}%
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="预测时长" prop="forecast_hours" class="form-item">
            <el-select
              v-model="predForm.forecast_hours"
              placeholder="请选择预测时长"
              style="width: 100%"
            >
              <el-option label="4小时" value="4" />
              <el-option label="24小时" value="24" />
              <el-option label="168小时 (7天)" value="168" />
            </el-select>
          </el-form-item>

          <el-form-item label="预测开始时间" prop="start_time" class="form-item">
            <el-date-picker
              v-model="predForm.start_time"
              type="datetime"
              placeholder="选择预测开始时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm"
              style="width: 100%"
            />
          </el-form-item>
        </div>

        <el-form-item>
          <button 
            class="predict-btn"
            :disabled="isPredicting"
            @click="startPrediction"
          >
            <span class="btn-icon">{{ isPredicting ? '⏳' : '🚀' }}</span>
            <span>{{ isPredicting ? '预测中...' : '开始预测' }}</span>
          </button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 预测结果展示 -->
    <div v-if="predictionResult" class="result-card">
      <div class="card-title">📊 预测结果</div>
      
      <div class="result-content">
        <!-- 预测图表 -->
        <div class="chart-wrapper">
          <div class="chart-title">预测曲线</div>
          <div ref="predictionChartContainer" class="chart-container"></div>
        </div>

        <!-- 预测数据表格 -->
        <div class="data-table">
          <div class="table-title">预测数据详表</div>
          <div class="table-scroll">
            <table class="pred-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>预测值</th>
                  <th>置信度</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in predictionResult.predictions" :key="index">
                  <td>{{ item.timestamp }}</td>
                  <td class="value-cell">{{ item.value.toFixed(2) }}</td>
                  <td class="confidence-cell">
                    <div class="confidence-bar">
                      <div class="confidence-fill" :style="{ width: (item.confidence * 100) + '%' }"></div>
                    </div>
                    <span>{{ (item.confidence * 100).toFixed(1) }}%</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 预测统计 -->
        <div class="statistics-grid">
          <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <div class="stat-label">平均预测值</div>
              <div class="stat-value">{{ avgPrediction.toFixed(2) }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-label">最大预测值</div>
              <div class="stat-value">{{ maxPrediction.toFixed(2) }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📉</div>
            <div class="stat-info">
              <div class="stat-label">最小预测值</div>
              <div class="stat-value">{{ minPrediction.toFixed(2) }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <div class="stat-info">
              <div class="stat-label">平均置信度</div>
              <div class="stat-value">{{ (avgConfidence * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>

        <!-- 导出按钮 -->
        <div class="action-buttons">
          <button class="export-btn primary" @click="exportData">
            <span>💾</span>
            <span>导出数据</span>
          </button>
          <button class="export-btn secondary" @click="downloadChart">
            <span>📥</span>
            <span>下载图表</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-alert">
      <span class="error-icon">⚠️</span>
      <span>{{ errorMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const predFormRef = ref(null)
const stations = ref([])
const availableModels = ref([])
const isPredicting = ref(false)
const loadingModels = ref(false)
const predictionResult = ref(null)
const errorMessage = ref('')
let predictionChart = null

const predForm = reactive({
  station_id: null,
  model_id: null,
  forecast_hours: '24',
  start_time: ''
})

const rules = {
  station_id: [
    { required: true, message: '请选择场站', trigger: 'change' }
  ],
  model_id: [
    { required: true, message: '请选择模型', trigger: 'change' }
  ],
  forecast_hours: [
    { required: true, message: '请选择预测时长', trigger: 'change' }
  ],
  start_time: [
    { required: true, message: '请选择预测开始时间', trigger: 'change' }
  ]
}

const avgPrediction = computed(() => {
  if (!predictionResult.value) return 0
  const sum = predictionResult.value.predictions.reduce((a, b) => a + b.value, 0)
  return sum / predictionResult.value.predictions.length
})

const maxPrediction = computed(() => {
  if (!predictionResult.value) return 0
  return Math.max(...predictionResult.value.predictions.map(p => p.value))
})

const minPrediction = computed(() => {
  if (!predictionResult.value) return 0
  return Math.min(...predictionResult.value.predictions.map(p => p.value))
})

const avgConfidence = computed(() => {
  if (!predictionResult.value) return 0
  const sum = predictionResult.value.predictions.reduce((a, b) => a + b.confidence, 0)
  return sum / predictionResult.value.predictions.length
})

const fetchStations = async () => {
  try {
    const response = await fetch('/api/stations/')
    if (response.ok) {
      const data = await response.json()
      stations.value = Array.isArray(data) ? data : []
      
      if (stations.value.length === 0) {
        // 模拟数据
        stations.value = [
          { id: 1, station_name: '巨鹿腾煌风电场' },
          { id: 2, station_name: '新乐凤鸣光伏电站' }
        ]
      }
    } else {
      throw new Error(`HTTP ${response.status}`)
    }
  } catch (error) {
    console.error('获取场站列表出错:', error)
    // 获取失败时显示模拟数据
    stations.value = [
      { id: 1, station_name: '巨鹿腾煌风电场' },
      { id: 2, station_name: '新乐凤鸣光伏电站' }
    ]
  }
}

const handleStationChange = async () => {
  if (!predForm.station_id) return
  
  loadingModels.value = true
  predForm.model_id = null
  
  try {
    // 暂时使用模拟数据，因为后端接口还未实现
    // 后期可改为调用真实 API: /api/train/models/?station_id=${predForm.station_id}
    
    const stationName = stations.value.find(s => s.id === predForm.station_id)?.station_name || `场站${predForm.station_id}`
    
    // 生成基于场站的示例模型
    availableModels.value = [
      { id: `${predForm.station_id}_1`, model_type: 'LSTM', station_name: stationName, mape: 8.5, created_at: '2026-01-15' },
      { id: `${predForm.station_id}_2`, model_type: 'Random Forest', station_name: stationName, mape: 9.2, created_at: '2026-01-10' },
      { id: `${predForm.station_id}_3`, model_type: 'XGBoost', station_name: stationName, mape: 7.8, created_at: '2026-01-20' },
      { id: `${predForm.station_id}_4`, model_type: 'ARIMA', station_name: stationName, mape: 10.1, created_at: '2026-01-05' }
    ]
    
    ElMessage.success(`已加载 ${stationName} 的 ${availableModels.value.length} 个模型`)
  } catch (error) {
    console.error('获取模型列表出错:', error)
    const stationName = stations.value.find(s => s.id === predForm.station_id)?.station_name || `场站${predForm.station_id}`
    availableModels.value = [
      { id: `${predForm.station_id}_1`, model_type: 'LSTM', station_name: stationName, mape: 8.5, created_at: '2026-01-15' },
      { id: `${predForm.station_id}_2`, model_type: 'Random Forest', station_name: stationName, mape: 9.2, created_at: '2026-01-10' },
      { id: `${predForm.station_id}_3`, model_type: 'XGBoost', station_name: stationName, mape: 7.8, created_at: '2026-01-20' }
    ]
    ElMessage.info('显示模型列表示例')
  } finally {
    loadingModels.value = false
  }
}

const startPrediction = async () => {
  if (!predFormRef.value) return
  
  try {
    await predFormRef.value.validate()
    
    isPredicting.value = true
    errorMessage.value = ''
    predictionResult.value = null

    try {
      const response = await fetch('/api/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: predForm.model_id,
          forecast_hours: parseInt(predForm.forecast_hours),
          start_time: predForm.start_time
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.predictions) {
          predictionResult.value = {
            predictions: data.predictions
          }
          ElMessage.success('预测完成！')
          renderPredictionChart()
          return
        }
      }
    } catch (e) {
      console.warn('调用实际 API 失败，使用模拟预测:', e)
    }

    // API 不可用时，使用模拟预测数据
    predictionResult.value = {
      predictions: generateMockPredictions()
    }
    ElMessage.success('预测完成！（演示数据）')
    renderPredictionChart()
  } catch (error) {
    console.error('预测出错:', error)
    ElMessage.error('预测出错: ' + error.message)
    errorMessage.value = '预测出错: ' + error.message
  } finally {
    isPredicting.value = false
  }
}

const generateMockPredictions = () => {
  const predictions = []
  const hours = parseInt(predForm.forecast_hours) || 24
  
  let currentTime
  try {
    currentTime = new Date(predForm.start_time)
    // 验证日期是否有效
    if (isNaN(currentTime.getTime())) {
      currentTime = new Date()
    }
  } catch (e) {
    currentTime = new Date()
  }
  
  for (let i = 0; i < hours; i++) {
    try {
      predictions.push({
        timestamp: currentTime.toLocaleString('zh-CN', { 
          month: '2-digit', 
          day: '2-digit', 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        value: Math.random() * 100 + 50,
        confidence: 0.85 + Math.random() * 0.1
      })
      currentTime = new Date(currentTime.getTime() + 60 * 60 * 1000)
    } catch (e) {
      console.warn('生成预测数据时出错:', e)
    }
  }
  
  return predictions
}

const renderPredictionChart = () => {
  if (!predictionResult.value) {
    console.warn('没有预测结果数据')
    return
  }
  
  if (!predictionResult.value.predictions || predictionResult.value.predictions.length === 0) {
    console.warn('预测数据列表为空')
    return
  }
  
  setTimeout(() => {
    try {
      const predChartContainer = document.querySelector('.chart-container')
      if (!predChartContainer) {
        console.warn('图表容器不存在')
        return
      }

      if (predictionChart) {
        predictionChart.dispose()
      }
      
      predictionChart = echarts.init(predChartContainer, null, { renderer: 'canvas' })
      
      const predictions = predictionResult.value.predictions
      const timestamps = predictions.map(p => p.timestamp)
      const values = predictions.map(p => p.value)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: timestamps,
          axisLabel: {
            rotate: 45,
            interval: Math.floor(timestamps.length / 10)
          }
        },
        yAxis: {
          type: 'value',
          name: '功率值'
        },
        series: [
          {
            name: '预测值',
            type: 'line',
            data: values,
            smooth: true,
            itemStyle: { color: '#667eea' },
            lineStyle: { width: 2 },
            areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0)' }
            ])}
          }
        ]
      }
      
      predictionChart.setOption(option)
      window.addEventListener('resize', () => {
        if (predictionChart) predictionChart.resize()
      })
    } catch (err) {
      console.error('渲染预测图表出错:', err)
      errorMessage.value = '图表渲染失败: ' + err.message
    }
  }, 100)
}

const exportData = () => {
  if (!predictionResult.value) return
  
  const csv = predictionResult.value.predictions.map(p => 
    `${p.timestamp},${p.value.toFixed(2)},${(p.confidence * 100).toFixed(1)}%`
  ).join('\n')
  
  const header = '时间,预测值,置信度\n'
  const blob = new Blob([header + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `预测结果_${new Date().toLocaleString()}.csv`
  link.click()
  
  ElMessage.success('数据已导出')
}

const downloadChart = () => {
  if (!predictionChart) return
  
  const url = predictionChart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  
  const link = document.createElement('a')
  link.href = url
  link.download = `预测图表_${new Date().toLocaleString()}.png`
  link.click()
  
  ElMessage.success('图表已下载')
}

onMounted(() => {
  fetchStations()
})

onUnmounted(() => {
  if (predictionChart) {
    predictionChart.dispose()
  }
})
</script>

<style scoped>
.prediction-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  min-height: 100vh;
}

/* 背景装饰 */
.bg-pattern {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.pattern-circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.08), transparent);
  animation: float-pattern 20s ease-in-out infinite;
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: 50px;
  left: 10%;
  animation-delay: 10s;
}

@keyframes float-pattern {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

/* 页面头部 */
.pred-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  animation: pulse-icon 3s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.header-text h2 {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 6px 0;
}

.subtitle {
  color: #7f8c8d;
  font-size: 15px;
  margin: 0;
}

/* 配置卡片 */
.config-card,
.result-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.5);
  position: relative;
  z-index: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.form-item {
  margin-bottom: 0 !important;
}

.predict-btn {
  width: 100%;
  padding: 16px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.predict-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.predict-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 结果内容 */
.result-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.chart-wrapper {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
}

.chart-container {
  width: 100%;
  height: 400px;
  min-height: 350px;
}

/* 数据表格 */
.data-table {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
}

.table-scroll {
  overflow-x: auto;
}

.pred-table {
  width: 100%;
  border-collapse: collapse;
}

.pred-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.pred-table th {
  padding: 14px;
  text-align: left;
  font-weight: 600;
}

.pred-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.pred-table tbody tr:hover {
  background: rgba(102, 126, 234, 0.05);
}

.value-cell {
  color: #667eea;
  font-weight: 600;
}

.confidence-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-bar {
  width: 80px;
  height: 6px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #27ae60, #2ecc71);
  border-radius: 3px;
}

/* 统计网格 */
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}

.stat-icon {
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 6px;
  font-weight: 500;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 16px;
}

.export-btn {
  flex: 1;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.export-btn.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.export-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.export-btn.secondary {
  background: white;
  color: #667eea;
  border: 2px solid rgba(102, 126, 234, 0.2);
}

.export-btn.secondary:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

/* 错误提示 */
.error-alert {
  padding: 16px 20px;
  background: rgba(231, 76, 60, 0.05);
  border: 1px solid rgba(231, 76, 60, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #e74c3c;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.error-icon {
  font-size: 20px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .prediction-container {
    padding: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .pred-table th,
  .pred-table td {
    padding: 10px 8px;
    font-size: 13px;
  }
}
</style>
