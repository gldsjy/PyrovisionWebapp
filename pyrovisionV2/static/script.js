let chart;

async function fetchChartData() {
  const response = await fetch('/chart-data');
  const data = await response.json();
  console.log('Fetched chart data:', data); 
  return data;
}

async function updateChart() {
  const data = await fetchChartData(); 
  if (chart) {
    chart.data.labels = data.labels;
    chart.data.datasets[0].data = data.values;
    chart.update(); // ← this is what actually redraws the chart
  }
}

window.onload = async function () {
  const data = await fetchChartData();

  const ctx = document.getElementById('lineChart').getContext('2d');
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Fire Intensity vs Time',
        data: data.values,
        borderColor: '#F47334',
        fill: false,
        tension: 0.4
      }]
    },
   options: {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: {
        callback: function(value) {
          return value >= 50 ? 'High' : 'Low';
        }
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: function(context) {
          const val = context.raw;
          return val >= 50 ? 'High Intensity' : 'Low Intensity';
        }
      }
    }
  }
}
  });

  setInterval(updateChart, 5000);
};

async function alertMessage() {
  const response = await fetch('/alert-message');
  const data = await response.json();
  alert(data.message);
}
