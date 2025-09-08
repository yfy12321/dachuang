<template>
  <div class="charts-container">
    <!-- 风速图表 -->
    <div class="chart-card">
      <h3>风速趋势 (m/s)</h3>
      <canvas ref="speedChart"></canvas>
    </div>
    
    <!-- 风向图表 -->
    <div class="chart-card">
      <h3>风向分布</h3>
      <canvas ref="directionChart"></canvas>
    </div>
    
    <!-- 温度图表 -->
    <div class="chart-card">
      <h3>温度变化 (°C)</h3>
      <canvas ref="tempChart"></canvas>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

export default {
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  
  setup(props) {
    const speedChart = ref(null)
    const directionChart = ref(null)
    const tempChart = ref(null)
    let chartInstances = []

    const renderCharts = () => {
      // 销毁旧图表
      chartInstances.forEach(instance => instance.destroy())
      chartInstances = []

      // 风速图表
      if (speedChart.value) {
        chartInstances.push(new Chart(speedChart.value, {
          type: 'line',
          data: {
            labels: props.chartData.timestamps,
            datasets: [{
              label: '风速',
              data: props.chartData.wind_speed,
              borderColor: '#667eea',
              backgroundColor: 'rgba(102, 126, 234, 0.1)',
              tension: 0.1,
              fill: true
            }]
          },
          options: getChartOptions('风速 (m/s)')
        }))
      }

      // 风向玫瑰图
      if (directionChart.value) {
        chartInstances.push(new Chart(directionChart.value, {
          type: 'polarArea',
          data: {
            labels: ['北', '东北', '东', '东南', '南', '西南', '西', '西北'],
            datasets: [{
              data: calculateDirectionFrequency(),
              backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                '#9966FF', '#FF9F40', '#8AC24A', '#F06292'
              ]
            }]
          }
        }))
      }

      // 温度图表
      if (tempChart.value) {
        chartInstances.push(new Chart(tempChart.value, {
          type: 'line',
          data: {
            labels: props.chartData.timestamps,
            datasets: [{
              label: '温度',
              data: props.chartData.temperature,
              borderColor: '#ff6384',
              backgroundColor: 'rgba(255, 99, 132, 0.1)',
              tension: 0.1,
              fill: true
            }]
          },
          options: getChartOptions('温度 (°C)')
        }))
      }
    }

    const calculateDirectionFrequency = () => {
      const directions = [0, 45, 90, 135, 180, 225, 270, 315, 360]
      const counts = new Array(8).fill(0)
      
      props.chartData.wind_direction.forEach(angle => {
        for (let i = 0; i < directions.length - 1; i++) {
          if (angle >= directions[i] && angle < directions[i+1]) {
            counts[i]++
            break
          }
        }
      })
      
      return counts
    }

    const getChartOptions = (title) => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: title }
      },
      scales: {
        x: {
          ticks: { maxRotation: 45, minRotation: 45 }
        }
      }
    })

    onMounted(renderCharts)
    onBeforeUnmount(() => {
      chartInstances.forEach(instance => instance.destroy())
    })

    return { speedChart, directionChart, tempChart }
  }
}
</script>

<style scoped>
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  padding: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.chart-card h3 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
}

.chart-card canvas {
  width: 100% !important;
  height: 300px !important;
}
</style>