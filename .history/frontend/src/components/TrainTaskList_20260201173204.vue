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
import { ref, onMounted, nextTick } from 'vue'
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

const formatTime = (timeStr) => {
  if (!timeStr) return '--'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
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
  padding: 32px;
  max-width: 1600px;
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
  animation: float-pattern 25s ease-in-out infinite;
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
  bottom: -50px;
  left: 10%;
  animation-delay: 8s;
}

.circle-3 {
  width: 250px;
  height: 250px;
  top: 40%;
  left: -80px;
  animation-delay: 15s;
}

@keyframes float-pattern {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

/* 页面头部 */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
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
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, #2c3e50 0%, #667eea 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-subtitle {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.refresh-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.refresh-btn:hover::before {
  opacity: 1;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.refresh-btn:active {
  transform: translateY(0);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 18px;
  animation: rotate-refresh 2s linear infinite;
}

.refresh-btn:not(:disabled):hover .btn-icon {
  animation-play-state: running;
}

@keyframes rotate-refresh {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-total { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-completed { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.stat-running { background: linear-gradient(135deg, #f39c12, #e67e22); }
.stat-failed { background: linear-gradient(135deg, #e74c3c, #c0392b); }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

/* 加载和空状态 */
.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  position: relative;
  z-index: 1;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(102, 126, 234, 0.1);
  border-top-color: #667eea;
  border-right-color: #764ba2;
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.loading-text {
  margin-top: 20px;
  color: #667eea;
  font-size: 16px;
  font-weight: 500;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-container h3 {
  color: #2c3e50;
  font-size: 24px;
  margin: 0 0 8px 0;
}

.empty-container p {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

/* 任务卡片网格 */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  position: relative;
  z-index: 1;
}

/* 任务卡片 */
.task-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  position: relative;
}

.task-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
}

/* 状态标识条 */
.task-status-bar {
  height: 5px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.status-pending { background: linear-gradient(90deg, #95a5a6, #7f8c8d); }
.status-running { background: linear-gradient(90deg, #f39c12, #e67e22); }
.status-completed { background: linear-gradient(90deg, #27ae60, #2ecc71); }
.status-failed { background: linear-gradient(90deg, #e74c3c, #c0392b); }

/* 卡片头部 */
.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
}

.task-id-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  padding: 8px 16px;
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.badge-label {
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
}

.badge-value {
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
}

.task-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.badge-pending { background: #95a5a6; }
.badge-running { background: #f39c12; }
.badge-completed { background: #27ae60; }
.badge-failed { background: #e74c3c; }

/* 任务信息 */
.task-info {
  padding: 0 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-size: 14px;
  color: #7f8c8d;
  min-width: 100px;
  font-weight: 500;
}

.info-value {
  font-size: 15px;
  color: #2c3e50;
  font-weight: 600;
  flex: 1;
}

.forecast-type {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  display: inline-block;
}

.type-ultra_short { background: rgba(39, 174, 96, 0.1); color: #27ae60; }
.type-short { background: rgba(243, 156, 18, 0.1); color: #f39c12; }
.type-medium { background: rgba(52, 152, 219, 0.1); color: #3498db; }

/* 训练指标区域 */
.metrics-section {
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.metrics-title {
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 12px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.metric-label {
  font-size: 12px;
  color: #7f8c8d;
  margin-bottom: 4px;
  font-weight: 500;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: #667eea;
}

/* 错误信息区域 */
.error-section {
  padding: 16px 24px;
  background: rgba(231, 76, 60, 0.05);
  border-top: 1px solid rgba(231, 76, 60, 0.1);
  border-bottom: 1px solid rgba(231, 76, 60, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.error-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.error-text {
  font-size: 14px;
  color: #e74c3c;
  line-height: 1.5;
  font-weight: 500;
}

/* 时间信息 */
.time-section {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.time-icon {
  font-size: 16px;
}

.time-label {
  color: #7f8c8d;
  font-weight: 500;
}

.time-value {
  color: #2c3e50;
  font-weight: 600;
}

/* 操作按钮 */
.task-actions {
  padding: 16px 24px 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 80px;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: white;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-warning {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.action-btn:active {
  transform: translateY(0);
}

/* 详情对话框样式保留 */
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .tasks-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .task-list-container {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .task-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>