<template>
  <div class="task-list-container">
    <!-- 顶部装饰背景 -->
    <div class="bg-pattern">
      <div class="pattern-circle circle-1"></div>
      <div class="pattern-circle circle-2"></div>
      <div class="pattern-circle circle-3"></div>
    </div>

    <!-- 页面头部 -->
    <div class="task-header">
      <div class="header-content">
        <div class="header-icon">📋</div>
        <div class="header-text">
          <h2>训练任务列表</h2>
          <p class="header-subtitle">管理和监控模型训练任务</p>
        </div>
      </div>
      <button class="refresh-btn" @click="refreshTasks" :disabled="loading">
        <span class="btn-icon">🔄</span>
        <span>{{ loading ? '加载中...' : '刷新' }}</span>
      </button>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-total">📊</div>
        <div class="stat-content">
          <div class="stat-label">总任务数</div>
          <div class="stat-value">{{ tasks.length }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-completed">✅</div>
        <div class="stat-content">
          <div class="stat-label">已完成</div>
          <div class="stat-value">{{ tasks.filter(t => t.status === 'completed').length }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-running">⚡</div>
        <div class="stat-content">
          <div class="stat-label">训练中</div>
          <div class="stat-value">{{ tasks.filter(t => t.status === 'running').length }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-failed">❌</div>
        <div class="stat-content">
          <div class="stat-label">失败</div>
          <div class="stat-value">{{ tasks.filter(t => t.status === 'failed').length }}</div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载任务数据...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="tasks.length === 0" class="empty-container">
      <div class="empty-icon">📭</div>
      <h3>暂无训练任务</h3>
      <p>开始创建您的第一个训练任务吧</p>
    </div>

    <!-- 任务卡片列表 -->
    <div v-else class="tasks-grid">
      <div
        v-for="task in tasks"
        :key="task.task_id"
        class="task-card"
        :class="`task-${task.status}`"
      >
        <!-- 状态标识条 -->
        <div class="task-status-bar" :class="`status-${task.status}`"></div>
        
        <!-- 卡片头部 -->
        <div class="task-card-header">
          <div class="task-id-badge">
            <span class="badge-label">ID</span>
            <span class="badge-value">{{ task.task_id }}</span>
          </div>
          <div class="task-status-badge" :class="`badge-${task.status}`">
            <span class="status-dot"></span>
            <span>{{ getStatusText(task.status) }}</span>
          </div>
        </div>

        <!-- 场站和模型信息 -->
        <div class="task-info">
          <div class="info-row">
            <div class="info-label">🏭 场站</div>
            <div class="info-value">{{ task.station_name || getStationName(task.station_id) }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">🤖 模型</div>
            <div class="info-value">{{ task.model_type }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">📈 预测类型</div>
            <div class="info-value forecast-type" :class="`type-${task.forecast_type}`">
              {{ getForecastTypeName(task.forecast_type) }}
            </div>
          </div>
        </div>

        <!-- 训练指标（仅完成状态显示） -->
        <div v-if="task.status === 'completed'" class="metrics-section">
          <div class="metrics-title">📊 训练指标</div>
          <div class="metrics-grid">
            <div class="metric-item">
              <div class="metric-label">MAE</div>
              <div class="metric-value">{{ task.mae?.toFixed(4) || '--' }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">RMSE</div>
              <div class="metric-value">{{ task.rmse?.toFixed(4) || '--' }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">MAPE</div>
              <div class="metric-value">{{ task.mape?.toFixed(2) || '--' }}%</div>
            </div>
          </div>
        </div>

        <!-- 错误信息（仅失败状态显示） -->
        <div v-if="task.status === 'failed' && task.error_message" class="error-section">
          <div class="error-icon">⚠️</div>
          <div class="error-text">{{ task.error_message }}</div>
        </div>

        <!-- 时间信息 -->
        <div class="time-section">
          <div class="time-item">
            <span class="time-icon">🕐</span>
            <span class="time-label">开始：</span>
            <span class="time-value">{{ formatTime(task.start_time) }}</span>
          </div>
          <div v-if="task.end_time" class="time-item">
            <span class="time-icon">🏁</span>
            <span class="time-label">结束：</span>
            <span class="time-value">{{ formatTime(task.end_time) }}</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="task-actions">
          <button
            v-if="task.status === 'completed'"
            class="action-btn btn-primary"
            @click="viewDetails(task)"
          >
            <span>📄</span>
            <span>详情</span>
          </button>
          <button
            v-if="task.status === 'completed'"
            class="action-btn btn-warning"
            @click="viewVisualization(task)"
          >
            <span>📊</span>
            <span>可视化</span>
          </button>
          <button
            v-if="task.status === 'completed'"
            class="action-btn btn-success"
            @click="useModel(task)"
          >
            <span>🚀</span>
            <span>使用</span>
          </button>
          <button
            v-if="task.status === 'failed'"
            class="action-btn btn-danger"
            @click="viewError(task)"
          >
            <span>⚠️</span>
            <span>错误</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="训练任务详情"
      width="600px"
    >
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">
            {{ selectedTask.task_id }}
          </el-descriptions-item>
          <el-descriptions-item label="场站">
            {{ getStationName(selectedTask.station_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="预测类型">
            {{ getForecastTypeName(selectedTask.forecast_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="模型类型">
            {{ selectedTask.model_type }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedTask.status)">
              {{ getStatusText(selectedTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ selectedTask.start_time }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedTask.end_time || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="测试开始时间">
            {{ selectedTask.test_start_time || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedTask.status === 'completed'" class="metrics-detail">
          <h4>训练指标</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="metric-card">
                <div class="metric-label">MAE</div>
                <div class="metric-value">{{ selectedTask.mae?.toFixed(4) || '--' }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="metric-card">
                <div class="metric-label">RMSE</div>
                <div class="metric-value">{{ selectedTask.rmse?.toFixed(4) || '--' }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="metric-card">
                <div class="metric-label">MAPE</div>
                <div class="metric-value">{{ selectedTask.mape?.toFixed(2) || '--' }}%</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div v-if="selectedTask.status === 'failed' && selectedTask.error_message" class="error-detail">
          <h4>错误信息</h4>
          <el-alert
            :title="selectedTask.error_message"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-dialog>

    <!-- 可视化对话框 -->
    <el-dialog
      v-model="visualizationDialogVisible"
      title="训练结果可视化"
      width="90%"
      :close-on-click-modal="false"
      destroy-on-close
      @opened="handleDialogOpened"
    >
      <TrainResultVisualization
        v-if="visualizationTaskId && visualizationDialogVisible"
        :key="visualizationTaskId"
        :task-id="visualizationTaskId"
        @close="visualizationDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const tasks = ref([])
const stations = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedTask = ref(null)
const visualizationDialogVisible = ref(false)
const visualizationTaskId = ref(null)

const fetchStations = async () => {
  try {
    const response = await fetch('/api/stations/')
    if (response.ok) {
      stations.value = await response.json()
    }
  } catch (error) {
    console.error('获取场站列表出错:', error)
  }
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/train/tasks/')
    if (response.ok) {
      const text = await response.text()
      try {
        tasks.value = JSON.parse(text)
      } catch (parseError) {
        console.error('JSON解析错误:', parseError, 'Response:', text)
        ElMessage.error('数据格式错误，请检查服务器日志')
        tasks.value = []
      }
    } else {
      const errorText = await response.text()
      try {
        const errorData = JSON.parse(errorText)
        ElMessage.error(errorData.error || '获取任务列表失败')
      } catch {
        ElMessage.error(`获取任务列表失败: ${response.status}`)
      }
    }
  } catch (error) {
    console.error('获取任务列表出错:', error)
    ElMessage.error('获取任务列表出错: ' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshTasks = () => {
  fetchTasks()
}

const getStationName = (stationId) => {
  const station = stations.value.find(s => s.id === stationId)
  return station ? station.station_name : `场站 ${stationId}`
}

const getForecastTypeName = (type) => {
  const typeMap = {
    'ultra_short': '超短期',
    'short': '短期',
    'medium': '中期'
  }
  return typeMap[type] || type
}

const getForecastTypeTag = (type) => {
  const tagMap = {
    'ultra_short': 'success',
    'short': 'warning',
    'medium': 'info'
  }
  return tagMap[type] || ''
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待开始',
    'running': '训练中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return typeMap[status] || ''
}

const viewDetails = (task) => {
  selectedTask.value = task
  detailDialogVisible.value = true
}

const useModel = (task) => {
  ElMessage.info('模型使用功能开发中...')
  // TODO: 实现模型使用功能
}

const viewError = (task) => {
  selectedTask.value = task
  detailDialogVisible.value = true
}

const viewVisualization = (task) => {
  visualizationTaskId.value = task.task_id
  visualizationDialogVisible.value = true
  console.log('打开可视化对话框，task_id:', task.task_id)
}

const handleDialogOpened = () => {
  console.log('对话框已完全打开')
}

onMounted(() => {
  fetchStations()
  fetchTasks()
})
</script>

<style scoped>
.task-list-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.task-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.metrics-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-item {
  font-size: 12px;
  color: #606266;
}

.metric-item strong {
  color: #409eff;
}

.empty-state {
  padding: 40px 0;
}

.task-detail {
  padding: 20px 0;
}

.metrics-detail {
  margin-top: 24px;
}

.metrics-detail h4 {
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

.error-detail {
  margin-top: 24px;
}

.error-detail h4 {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
}
</style>