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
          if (value === 20) return 'Low';
          if (value === 80) return 'High';
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


const powerButton = document.getElementById('power-button');
const sprayButton = document.getElementById('spray-button');
async function initializeButtons(){
  const power = await fetch('/power-status')
  const power_status = await power.json();
  const spray = await fetch('/spray-manual-status')
  const spray_status = await spray.json();
  if (power_status.power_on == true){
    powerButton.textContent = "SYSTEM POWER ON";
    powerButton.style.backgroundColor = "#F47334";
  }
  else{
    powerButton.textContent =  "SYSTEM POWER OFF";
    powerButton.style.backgroundColor = "#808080";
  }


  if(spray_status.spray_on == true){
    sprayButton.textContent = "SPRAY ON"
    sprayButton.style.backgroundColor = "#f6a427";
  }
  else{
    sprayButton.textContent = "SPRAY OFF"
    sprayButton.style.backgroundColor = "#808080";
  }
}


window.onload(initializeButtons());




powerButton.addEventListener('click', async function () {
  try {
    const response = await fetch('/power-status');
    const data = await response.json();
   
    if (data.power_on === false) {
      powerButton.textContent = "POWER ON";
      powerButton.style.backgroundColor = "#F47334";
      const response = await fetch('/control-power', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: "POWER_ON" })
    });
   
     
    } else {
      powerButton.textContent = "POWER OFF";
      powerButton.style.backgroundColor = "#808080";
      const response = await fetch('/control-power', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: "POWER_OFF" })
    });
   
    }


  } catch (error) {
    console.error('Error toggling power:', error);
  }
});


sprayButton.addEventListener('click', async function () {
  try {
    const response = await fetch('/spray-manual-status');
    const data = await response.json();
   
    if (data.spray_on === false) {
      sprayButton.textContent = "SPRAY ON";
      sprayButton.style.backgroundColor = "#f6a427";
      const response = await fetch('/control-spray', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: "SPRAY_ON" })
    });


     
    } else {
      sprayButton.textContent = "SPRAY OFF";
      sprayButton.style.backgroundColor = "#808080";
      const response = await fetch('/control-spray', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: "SPRAY_OFF" })
    });
   
    }


  } catch (error) {
    console.error('Error toggling power:', error);
  }
});


