<template>
  <div class="visualization-wrapper">
    <!-- 页面头部 -->
    <div class="viz-header">
      <div class="header-title">
        <span class="title-icon">📊</span>
        <div>
          <h2>训练结果可视化</h2>
          <p class="subtitle">预测结果分析与误差评估</p>
        </div>
      </div>
      <button class="close-btn" @click="$emit('close')">
        <span>✕</span>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载可视化数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
    </div>

    <!-- 空数据 -->
    <div v-else-if="!chartData || !chartData.timestamps || chartData.timestamps.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <h3>暂无数据</h3>
      <p>该训练任务暂无预测数据</p>
    </div>

    <!-- 正常内容 -->
    <div v-else class="viz-content">
      <!-- 指标卡片 -->
      <div class="metrics-cards" v-if="metrics">
        <div class="metric-card metric-mae">
          <div class="metric-header">
            <span class="metric-icon">📏</span>
            <span class="metric-name">平均绝对误差</span>
          </div>
          <div class="metric-body">
            <div class="metric-value">{{ metrics.mae?.toFixed(4) || '--' }}</div>
            <div class="metric-label">MAE</div>
          </div>
        </div>

        <div class="metric-card metric-rmse">
          <div class="metric-header">
            <span class="metric-icon">📊</span>
            <span class="metric-name">均方根误差</span>
          </div>
          <div class="metric-body">
            <div class="metric-value">{{ metrics.rmse?.toFixed(4) || '--' }}</div>
            <div class="metric-label">RMSE</div>
          </div>
        </div>

        <div class="metric-card metric-mape">
          <div class="metric-header">
            <span class="metric-icon">📈</span>
            <span class="metric-name">平均百分比误差</span>
          </div>
          <div class="metric-body">
            <div class="metric-value">{{ metrics.mape?.toFixed(2) || '--' }}%</div>
            <div class="metric-label">MAPE</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <!-- 预测 vs 实际 -->
        <div class="chart-wrapper">
          <div class="chart-title">
            <span class="chart-icon">📉</span>
            <span>预测值 vs 实际值对比</span>
          </div>
          <div ref="chartContainer" class="chart-container"></div>
        </div>

        <!-- 误差分析 -->
        <div class="chart-wrapper">
          <div class="chart-title">
            <span class="chart-icon">⚖️</span>
            <span>预测误差分布</span>
          </div>
          <div ref="errorChartContainer" class="chart-container"></div>
        </div>
      </div>

      <!-- 数据统计 -->
      <div class="statistics-section">
        <div class="stat-item">
          <span class="stat-label">样本数量</span>
          <span class="stat-value">{{ chartData.timestamps?.length || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最大误差</span>
          <span class="stat-value">{{ maxError.toFixed(2) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">平均误差</span>
          <span class="stat-value">{{ avgError.toFixed(2) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">准确度</span>
          <span class="stat-value">{{ (100 - (metrics?.mape || 0)).toFixed(2) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const props = defineProps({
  taskId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref('')
const metrics = ref(null)
const chartData = ref(null)
const chartContainer = ref(null)
const errorChartContainer = ref(null)
let chartInstance = null
let errorChartInstance = null

const maxError = computed(() => {
  if (!chartData.value) return 0
  const errors = chartData.value.actual.map((actual, idx) => {
    return Math.abs(actual - chartData.value.predicted[idx])
  })
  return Math.max(...errors)
})

const avgError = computed(() => {
  if (!chartData.value) return 0
  const errors = chartData.value.actual.map((actual, idx) => {
    return Math.abs(actual - chartData.value.predicted[idx])
  })
  return errors.reduce((a, b) => a + b, 0) / errors.length
})

const fetchPredictionData = async () => {
  loading.value = true
  error.value = ''
  chartData.value = null
  metrics.value = null
  
  try {
    console.log('开始获取预测数据, task_id:', props.taskId)
    
    try {
      const response = await fetch(`/api/train/prediction-data/?task_id=${props.taskId}`)
      
      if (response.ok) {
        const data = await response.json()
        console.log('API响应:', data)
        
        if (data.success && data.data) {
          chartData.value = data.data
          metrics.value = data.data.metrics
          console.log('数据已设置:', {
            timestamps: data.data.timestamps?.length,
            actual: data.data.actual?.length,
            predicted: data.data.predicted?.length
          })
          
          await new Promise(resolve => setTimeout(resolve, 500))
          renderCharts()
          return
        }
      }
    } catch (e) {
      console.warn('调用 API 失败，将使用模拟数据:', e)
    }
    
    // API 不可用时，使用模拟数据
    console.log('使用模拟数据...')
    chartData.value = generateMockData()
    metrics.value = chartData.value.metrics
    
    await new Promise(resolve => setTimeout(resolve, 500))
    renderCharts()
    ElMessage.success('已加载模拟训练结果数据')
  } catch (err) {
    error.value = '获取预测数据出错: ' + err.message
    ElMessage.error(error.value)
    console.error('获取预测数据出错:', err)
  } finally {
    loading.value = false
  }
}

const generateMockData = () => {
  // 生成模拟数据
  const timestamps = []
  const actual = []
  const predicted = []
  
  let baseValue = 50
  for (let i = 0; i < 48; i++) {
    const date = new Date()
    date.setHours(date.getHours() - (47 - i))
    timestamps.push(date.toLocaleString('zh-CN', { 
      month: '2-digit', 
      day: '2-digit', 
      hour: '2-digit', 
      minute: '2-digit' 
    }))
    
    // 生成逼真的数据波动
    const noise1 = (Math.random() - 0.5) * 20
    const noise2 = (Math.random() - 0.5) * 15
    const trend = Math.sin(i / 10) * 10
    
    const actualValue = baseValue + trend + noise1
    const predictedValue = baseValue + trend + noise2
    
    actual.push(Math.max(0, actualValue))
    predicted.push(Math.max(0, predictedValue))
    
    baseValue += (Math.random() - 0.5) * 5
  }
  
  // 计算误差指标
  const errors = actual.map((a, i) => Math.abs(a - predicted[i]))
  const mae = errors.reduce((a, b) => a + b, 0) / errors.length
  const rmse = Math.sqrt(errors.reduce((a, b) => a + b * b, 0) / errors.length)
  const mape = (errors.reduce((sum, err, i) => sum + (err / Math.max(1, actual[i]) * 100), 0) / errors.length)
  
  return {
    timestamps,
    actual,
    predicted,
    metrics: {
      mae: mae,
      rmse: rmse,
      mape: mape
    }
  }
}

const renderCharts = () => {
  if (!chartData.value) {
    console.warn('没有图表数据')
    return
  }
  
  if (!chartData.value.timestamps || chartData.value.timestamps.length === 0) {
    console.warn('时间戳数据为空')
    return
  }
  
  // 多次重试确保容器可用
  let retryCount = 0
  const maxRetries = 5
  
  const tryRenderCharts = () => {
    setTimeout(() => {
      if (!chartContainer.value) {
        console.warn(`图表容器不存在，重试... (${retryCount + 1}/${maxRetries})`)
        retryCount++
        if (retryCount < maxRetries) {
          tryRenderCharts()
        } else {
          console.error('多次重试后仍未找到图表容器')
          error.value = '图表容器初始化失败'
        }
        return
      }
      
      try {
        // 销毁旧图表
        if (chartInstance) {
          chartInstance.dispose()
          chartInstance = null
        }
        if (errorChartInstance) {
          errorChartInstance.dispose()
          errorChartInstance = null
        }
        
        console.log('开始初始化图表容器...')
        console.log('图表容器大小:', chartContainer.value.offsetWidth, 'x', chartContainer.value.offsetHeight)
        
        // 创建预测对比图表
        chartInstance = echarts.init(chartContainer.value, null, { renderer: 'canvas' })
        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross'
            }
          },
          legend: {
            data: ['实际值', '预测值'],
            top: 10
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
            data: chartData.value.timestamps,
            axisLabel: {
              rotate: 45,
              interval: Math.floor(chartData.value.timestamps.length / 10)
            }
          },
          yAxis: {
            type: 'value',
            name: '功率值'
          },
          series: [
            {
              name: '实际值',
              type: 'line',
              data: chartData.value.actual,
              smooth: true,
              itemStyle: { color: '#667eea' },
              lineStyle: { width: 2 },
              areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                { offset: 1, color: 'rgba(102, 126, 234, 0)' }
              ])}
            },
            {
              name: '预测值',
              type: 'line',
              data: chartData.value.predicted,
              smooth: true,
              itemStyle: { color: '#27ae60' },
              lineStyle: { width: 2 },
              areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(39, 174, 96, 0.3)' },
                { offset: 1, color: 'rgba(39, 174, 96, 0)' }
              ])}
            }
          ]
        }
        chartInstance.setOption(option)
        console.log('预测对比图表已渲染，数据点:', chartData.value.timestamps.length)
        
        // 创建误差分析图表
        if (errorChartContainer.value) {
          console.log('误差图表容器大小:', errorChartContainer.value.offsetWidth, 'x', errorChartContainer.value.offsetHeight)
          
          errorChartInstance = echarts.init(errorChartContainer.value, null, { renderer: 'canvas' })
          
          const errors = chartData.value.actual.map((actual, idx) => {
            const predicted = chartData.value.predicted[idx]
            return actual - predicted
          })
          
          const errorOption = {
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
              data: chartData.value.timestamps,
              axisLabel: {
                rotate: 45,
                interval: Math.floor(chartData.value.timestamps.length / 10)
              }
            },
            yAxis: {
              type: 'value',
              name: '误差值'
            },
            series: [
              {
                name: '预测误差',
                type: 'bar',
                data: errors,
                itemStyle: {
                  color: function(params) {
                    return params.value >= 0 ? '#e74c3c' : '#3498db'
                  }
                }
              }
            ]
          }
          errorChartInstance.setOption(errorOption)
          console.log('误差分析图表已渲染')
        } else {
          console.warn('误差图表容器不存在')
        }
        
        window.addEventListener('resize', handleResize)
      } catch (err) {
        console.error('渲染图表时出错:', err)
        error.value = '渲染图表失败: ' + err.message
      }
    }, 200)
  }
  
  tryRenderCharts()
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
  if (errorChartInstance) {
    errorChartInstance.resize()
  }
}

onMounted(() => {
  console.log('组件已挂载, taskId:', props.taskId, '类型:', typeof props.taskId)
  if (props.taskId) {
    setTimeout(() => {
      fetchPredictionData()
    }, 50)
  } else {
    console.warn('缺少 taskId')
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
  if (errorChartInstance) {
    errorChartInstance.dispose()
  }
})
</script>

<style scoped>
.visualization-wrapper {
  padding: 32px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 600px;
}

/* 页面头部 */
.viz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  font-size: 32px;
}

.viz-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.subtitle {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}

.close-btn {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.close-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

/* 加载状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(102, 126, 234, 0.1);
  border-top-color: #667eea;
  border-right-color: #764ba2;
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #667eea;
  font-size: 16px;
  font-weight: 500;
}

.empty-icon {
  font-size: 64px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-state h3 {
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.empty-state p {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 16px;
  padding: 40px 20px;
  background: rgba(231, 76, 60, 0.05);
  border-radius: 16px;
}

.error-icon {
  font-size: 56px;
}

.error-state h3 {
  font-size: 22px;
  font-weight: 600;
  color: #e74c3c;
  margin: 0;
}

.error-state p {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

/* 内容区域 */
.viz-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 指标卡片 */
.metrics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.metric-mae::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.metric-rmse::before { background: linear-gradient(90deg, #f39c12, #e67e22); }
.metric-mape::before { background: linear-gradient(90deg, #27ae60, #2ecc71); }

.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.metric-icon {
  font-size: 24px;
}

.metric-name {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.metric-body {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.metric-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 24px;
}

.chart-wrapper {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
}

.chart-icon {
  font-size: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
  min-height: 350px;
}

/* 统计信息 */
.statistics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border: 1px solid rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.stat-label {
  display: block;
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

/* 旧样式保留兼容 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metric-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.metric-item .metric-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
  color: white;
}

.metric-item .metric-value {
  font-size: 24px;
  font-weight: 600;
  color: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .visualization-wrapper {
    padding: 16px;
  }
  
  .viz-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .metrics-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>

.metrics-card {
  margin-bottom: 24px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.metric-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.metric-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 12px;
}

.metric-value {
  font-size: 32px;
  font-weight: 600;
}

.chart-card {
  margin-bottom: 24px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.chart-container {
  width: 100%;
  height: 400px;
  min-height: 400px;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>