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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const props = defineProps({
  taskId: {
    type: Number,
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

const fetchPredictionData = async () => {
  loading.value = true
  error.value = ''
  chartData.value = null
  metrics.value = null
  
  try {
    console.log('开始获取预测数据, task_id:', props.taskId)
    const response = await fetch(`/api/train/prediction-data/?task_id=${props.taskId}`)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP ${response.status}: ${errorText}`)
    }
    
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
      
      // 等待DOM更新后再渲染图表
      await new Promise(resolve => setTimeout(resolve, 500))
      renderCharts()
    } else {
      error.value = data.error || '获取预测数据失败'
      ElMessage.error(error.value)
      console.error('API返回错误:', data)
    }
  } catch (err) {
    error.value = '获取预测数据出错: ' + err.message
    ElMessage.error(error.value)
    console.error('获取预测数据出错:', err)
  } finally {
    loading.value = false
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
  
  // 使用nextTick确保DOM已更新
  setTimeout(() => {
    if (!chartContainer.value) {
      console.warn('图表容器不存在，重试...')
      setTimeout(renderCharts, 200)
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
      
      // 创建预测对比图表
      chartInstance = echarts.init(chartContainer.value)
  const option = {
    title: {
      text: '预测值 vs 实际值',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['实际值', '预测值'],
      top: 30
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
        itemStyle: { color: '#5470c6' },
        lineStyle: { width: 2 }
      },
      {
        name: '预测值',
        type: 'line',
        data: chartData.value.predicted,
        smooth: true,
        itemStyle: { color: '#91cc75' },
        lineStyle: { width: 2 }
      }
    ]
  }
      chartInstance.setOption(option)
      console.log('预测对比图表已渲染')
      
      // 创建误差分析图表
      if (errorChartContainer.value) {
        errorChartInstance = echarts.init(errorChartContainer.value)
    
    // 计算误差
    const errors = chartData.value.actual.map((actual, idx) => {
      const predicted = chartData.value.predicted[idx]
      return actual - predicted
    })
    
    const errorOption = {
      title: {
        text: '预测误差分布',
        left: 'center'
      },
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
              return params.value >= 0 ? '#ee6666' : '#73c0de'
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
      
      // 响应式调整
      window.addEventListener('resize', handleResize)
    } catch (err) {
      console.error('渲染图表时出错:', err)
      error.value = '渲染图表失败: ' + err.message
    }
  }, 100)
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
  if (errorChartInstance) {
    errorChartInstance.resize()
  }
}

watch(() => props.taskId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('taskId变化，重新获取数据:', newId)
    fetchPredictionData()
  }
}, { immediate: true })

onMounted(() => {
  console.log('组件已挂载, taskId:', props.taskId)
  if (props.taskId) {
    // 延迟一下确保对话框已完全打开
    setTimeout(() => {
      fetchPredictionData()
    }, 100)
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
.visualization-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.visualization-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

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