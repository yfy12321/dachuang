<template>
  <div class="task-list-container">
    <div class="task-header">
      <h2>📋 训练任务列表</h2>
      <el-button type="primary" @click="refreshTasks" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-card v-loading="loading" shadow="hover">
      <el-table
        :data="tasks"
        style="width: 100%"
        stripe
        :default-sort="{ prop: 'task_id', order: 'descending' }"
      >
        <el-table-column prop="task_id" label="任务ID" width="100" sortable />
        
        <el-table-column label="场站" width="180">
          <template #default="scope">
            <span>{{ scope.row.station_name || getStationName(scope.row.station_id) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="预测类型" width="120">
          <template #default="scope">
            <el-tag :type="getForecastTypeTag(scope.row.forecast_type)">
              {{ getForecastTypeName(scope.row.forecast_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="model_type" label="模型类型" width="140">
          <template #default="scope">
            <el-tag>{{ scope.row.model_type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getStatusTagType(scope.row.status)"
              effect="dark"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="训练指标" width="300">
          <template #default="scope">
            <div v-if="scope.row.status === 'completed'" class="metrics-row">
              <span class="metric-item">
                <strong>MAE:</strong> {{ scope.row.mae?.toFixed(4) || '--' }}
              </span>
              <span class="metric-item">
                <strong>RMSE:</strong> {{ scope.row.rmse?.toFixed(4) || '--' }}
              </span>
              <span class="metric-item">
                <strong>MAPE:</strong> {{ scope.row.mape?.toFixed(2) || '--' }}%
              </span>
            </div>
            <span v-else class="no-metrics">--</span>
          </template>
        </el-table-column>

        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'completed'"
              type="primary"
              size="small"
              @click="viewDetails(scope.row)"
            >
              查看详情
            </el-button>
            <el-button
              v-if="scope.row.status === 'completed'"
              type="warning"
              size="small"
              @click="viewVisualization(scope.row)"
            >
              可视化
            </el-button>
            <el-button
              v-if="scope.row.status === 'completed'"
              type="success"
              size="small"
              @click="useModel(scope.row)"
            >
              使用模型
            </el-button>
            <el-button
              v-if="scope.row.status === 'failed'"
              type="danger"
              size="small"
              @click="viewError(scope.row)"
            >
              查看错误
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无训练任务" />
      </div>
    </el-card>

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