<template>
  <div class="train-model-container">
    <!-- 背景装饰 -->
    <div class="bg-pattern">
      <div class="pattern-circle circle-1"></div>
      <div class="pattern-circle circle-2"></div>
    </div>

    <!-- 页面头部 -->
    <div class="train-header">
      <div class="header-icon">🤖</div>
      <div class="header-text">
        <h2>模型训练</h2>
        <p class="subtitle">配置参数启动模型训练，监控训练进度</p>
      </div>
    </div>

    <!-- 训练配置卡片 -->
    <div class="config-card">
      <div class="card-title">⚙️ 训练配置</div>
      
      <el-form
        :model="trainForm"
        :rules="rules"
        ref="trainFormRef"
        label-width="140px"
        label-position="top"
      >
        <div class="form-grid">
          <el-form-item label="选择场站" prop="station_id" class="form-item">
            <el-select
              v-model="trainForm.station_id"
              placeholder="请选择场站"
              style="width: 100%"
              @change="handleStationChange"
            >
              <el-option
                v-for="station in stations"
                :key="station.id"
                :label="station.station_name"
                :value="station.id"
              >
                <span>{{ station.station_name }}</span>
                <span style="color: #8492a6; font-size: 12px; margin-left: 8px">
                  (ID: {{ station.id }})
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="预测任务类型" prop="task_id" class="form-item">
            <el-select
              v-model="trainForm.task_id"
              placeholder="请选择预测任务类型"
              style="width: 100%"
            >
              <el-option label="超短期预测 (4小时)" :value="1" />
              <el-option label="日前预测 (24小时)" :value="2" />
              <el-option label="中长期预测 (7天)" :value="3" />
            </el-select>
          </el-form-item>

          <el-form-item label="模型类型" prop="model_type" class="form-item">
            <el-select
              v-model="trainForm.model_type"
              placeholder="请选择模型类型"
              style="width: 100%"
            >
              <el-option label="线性回归 (Linear)" value="linear" />
              <el-option label="随机森林 (Random Forest)" value="random_forest" />
              <el-option label="LSTM (深度学习)" value="lstm" />
            </el-select>
          </el-form-item>

          <el-form-item label="测试集开始时间" prop="test_start_time" class="form-item">
            <el-date-picker
              v-model="trainForm.test_start_time"
              type="datetime"
              placeholder="选择测试集开始时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm"
              style="width: 100%"
            />
          </el-form-item>
        </div>

        <el-form-item>
          <button 
            class="train-btn"
            :disabled="isTraining"
            @click="startTraining"
          >
            <span class="btn-icon">{{ isTraining ? '⏳' : '🚀' }}</span>
            <span>{{ isTraining ? '训练中...' : '启动训练' }}</span>
          </button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 训练状态卡片 -->
    <div v-if="currentTaskId" class="status-card">
      <div class="card-title">📊 训练状态</div>
      
      <div class="status-content">
        <!-- 进度条 -->
        <div class="progress-section">
          <div class="progress-label">
            <span>训练进度</span>
            <span class="progress-status" :class="`status-${statusType}`">{{ statusText }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <div class="progress-steps">
            <div class="step" :class="{ active: currentStep >= 1 }">
              <div class="step-circle">1</div>
              <div class="step-label">初始化</div>
            </div>
            <div class="step" :class="{ active: currentStep >= 2 }">
              <div class="step-circle">2</div>
              <div class="step-label">数据准备</div>
            </div>
            <div class="step" :class="{ active: currentStep >= 3 }">
              <div class="step-circle">3</div>
              <div class="step-label">模型训练</div>
            </div>
            <div class="step" :class="{ active: currentStep >= 4 }">
              <div class="step-circle">4</div>
              <div class="step-label">评估完成</div>
            </div>
          </div>
        </div>

        <!-- 训练指标 -->
        <div v-if="trainingMetrics" class="metrics-grid">
          <div class="metric-card metric-mae">
            <div class="metric-icon">📏</div>
            <div class="metric-info">
              <div class="metric-label">MAE</div>
              <div class="metric-value">{{ trainingMetrics.MAE?.toFixed(4) || '--' }}</div>
            </div>
          </div>
          <div class="metric-card metric-rmse">
            <div class="metric-icon">📊</div>
            <div class="metric-info">
              <div class="metric-label">RMSE</div>
              <div class="metric-value">{{ trainingMetrics.RMSE?.toFixed(4) || '--' }}</div>
            </div>
          </div>
          <div class="metric-card metric-mape">
            <div class="metric-icon">📈</div>
            <div class="metric-info">
              <div class="metric-label">MAPE</div>
              <div class="metric-value">{{ trainingMetrics.MAPE?.toFixed(2) || '--' }}%</div>
            </div>
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="errorMessage" class="error-alert">
          <span class="error-icon">⚠️</span>
          <span>{{ errorMessage }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const trainFormRef = ref(null)
const stations = ref([])
const isTraining = ref(false)
const currentTaskId = ref(null)
const trainingMetrics = ref(null)
const errorMessage = ref('')
const statusPolling = ref(null)
const currentStep = ref(0)

const trainForm = reactive({
  station_id: null,
  task_id: null,
  model_type: '',
  test_start_time: ''
})

const rules = {
  station_id: [
    { required: true, message: '请选择场站', trigger: 'change' }
  ],
  task_id: [
    { required: true, message: '请选择预测任务类型', trigger: 'change' }
  ],
  model_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  test_start_time: [
    { required: true, message: '请选择测试集开始时间', trigger: 'change' }
  ]
}

const statusType = computed(() => {
  if (errorMessage.value) return 'error'
  if (trainingMetrics.value) return 'success'
  if (currentTaskId.value) return 'running'
  return 'pending'
})

const statusText = computed(() => {
  if (errorMessage.value) return '训练失败'
  if (trainingMetrics.value) return '训练完成'
  if (currentTaskId.value) return '训练中'
  return '未开始'
})

const progressPercent = computed(() => {
  if (!currentTaskId.value) return 0
  if (trainingMetrics.value) return 100
  if (currentStep.value === 1) return 25
  if (currentStep.value === 2) return 50
  if (currentStep.value === 3) return 75
  return 0
})

const fetchStations = async () => {
  try {
    const response = await fetch('/api/stations/')
    if (response.ok) {
      stations.value = await response.json()
    } else {
      ElMessage.error('获取场站列表失败')
    }
  } catch (error) {
    console.error('获取场站列表出错:', error)
    ElMessage.error('获取场站列表出错')
  }
}

const handleStationChange = () => {
  // 场站变化时的处理逻辑
}

const startTraining = async () => {
  if (!trainFormRef.value) return
  
  try {
    await trainFormRef.value.validate()
    
    isTraining.value = true
    errorMessage.value = ''
    trainingMetrics.value = null
    currentStep.value = 0

    const response = await fetch('/api/train/start/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        station_id: trainForm.station_id.toString(),
        task_id: trainForm.task_id.toString(),
        model_type: trainForm.model_type,
        test_start_time: trainForm.test_start_time
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: '服务器错误' }))
      throw new Error(errorData.message || `HTTP错误: ${response.status}`)
    }

    const data = await response.json()

    if (data.success) {
      currentTaskId.value = data.task_id
      currentStep.value = 1
      ElMessage.success('训练任务已启动')
      startPolling()
    } else {
      isTraining.value = false
      ElMessage.error(data.message || '启动训练失败')
      errorMessage.value = data.message || '启动训练失败'
    }
  } catch (error) {
    isTraining.value = false
    console.error('启动训练出错:', error)
    ElMessage.error('启动训练出错: ' + error.message)
    errorMessage.value = '启动训练出错: ' + error.message
  }
}

const checkTrainingStatus = async () => {
  if (!currentTaskId.value) return

  try {
    const response = await fetch(`/api/train/status/?task_id=${currentTaskId.value}`)
    const data = await response.json()

    if (data.success) {
      // 更新训练步骤
      if (data.status === 'initializing') {
        currentStep.value = 1
      } else if (data.status === 'data_preparation') {
        currentStep.value = 2
      } else if (data.status === 'training') {
        currentStep.value = 3
      } else if (data.status === 'finished') {
        currentStep.value = 4
        stopPolling()
        isTraining.value = false
        await fetchTrainingResult()
      } else if (data.status === 'failed') {
        stopPolling()
        isTraining.value = false
        errorMessage.value = data.error_message || '训练失败'
        ElMessage.error('训练失败: ' + errorMessage.value)
      }
    }
  } catch (error) {
    console.error('查询训练状态出错:', error)
  }
}

const fetchTrainingResult = async () => {
  if (!currentTaskId.value) return

  try {
    const response = await fetch(`/api/train/result/?result_id=${currentTaskId.value}`)
    const data = await response.json()

    if (data.success && data.metrics) {
      trainingMetrics.value = data.metrics
      ElMessage.success('训练完成！')
    }
  } catch (error) {
    console.error('获取训练结果出错:', error)
    ElMessage.error('获取训练结果出错')
  }
}

const startPolling = () => {
  stopPolling()
  statusPolling.value = setInterval(checkTrainingStatus, 2000)
}

const stopPolling = () => {
  if (statusPolling.value) {
    clearInterval(statusPolling.value)
    statusPolling.value = null
  }
}

onMounted(() => {
  fetchStations()
})

onUnmounted(() => {
  stopPolling()
})
</script>

const fetchTrainingResult = async () => {
  if (!currentTaskId.value) return

  try {
    const response = await fetch(`/api/train/result/?result_id=${currentTaskId.value}`)
    const data = await response.json()

    if (data.success && data.metrics) {
      trainingMetrics.value = data.metrics
      ElMessage.success('训练完成！')
    }
  } catch (error) {
    console.error('获取训练结果出错:', error)
    ElMessage.error('获取训练结果出错')
  }
}

const startPolling = () => {
  stopPolling()
  statusPolling.value = setInterval(checkTrainingStatus, 2000) // 每2秒轮询一次
}

const stopPolling = () => {
  if (statusPolling.value) {
    clearInterval(statusPolling.value)
    statusPolling.value = null
  }
}

onMounted(() => {
  fetchStations()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.train-model-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.train-header {
  margin-bottom: 24px;
}

.train-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 14px;
}

.train-form-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.status-card {
  margin-top: 24px;
}

.status-content {
  padding: 20px 0;
}

.metrics-section {
  margin-top: 32px;
}

.metrics-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
}

.metric-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.metric-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
}

.error-message {
  margin-top: 24px;
}
</style>