// SA5X Monitor Web Application JavaScript

class SA5XMonitor {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.isConnected = false;
        this.isMonitoring = false;
        this.dataHistory = {
            timestamps: [],
            frequency_error: [],
            temperature: [],
            voltage: [],
            current: [],
            lock_status: [],
            holdover_status: []
        };
        this.maxDataPoints = 100;
        this.currentChartView = 'freq-temp';
        
        this.initializeSocket();
        this.initializeCharts();
        this.setupEventListeners();
        this.loadConfiguration();
    }
    
    initializeSocket() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('status_update', (data) => {
            this.updateStatusDisplay(data);
            this.updateCharts(data);
            this.updateStatistics();
        });
        
        this.socket.on('test_completed', (data) => {
            this.showTestResults(data);
        });
        
        this.socket.on('test_error', (data) => {
            this.showError('Test failed: ' + data.error);
        });
    }
    
    initializeCharts() {
        // Main real-time chart
        this.initializeMainChart();
        
        // Frequency stability chart
        this.initializeFrequencyChart();
        
        // Temperature and electrical chart
        this.initializeTempElectricalChart();
        
        // Allan deviation chart
        this.initializeAllanChart();
    }
    
    initializeMainChart() {
        const ctx = document.getElementById('realtime-chart').getContext('2d');
        
        this.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Frequency Error (ppm)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Temperature (°C)',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Frequency Error (ppm)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    initializeFrequencyChart() {
        const ctx = document.getElementById('frequency-chart').getContext('2d');
        
        this.charts.frequency = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Frequency Error',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Moving Average',
                        data: [],
                        borderColor: 'rgb(255, 159, 64)',
                        backgroundColor: 'rgba(255, 159, 64, 0.1)',
                        tension: 0.1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Frequency Error (ppm)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    initializeTempElectricalChart() {
        const ctx = document.getElementById('temp-electrical-chart').getContext('2d');
        
        this.charts.tempElectrical = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Voltage (V)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.1,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Current (A)',
                        data: [],
                        borderColor: 'rgb(255, 205, 86)',
                        backgroundColor: 'rgba(255, 205, 86, 0.1)',
                        tension: 0.1,
                        yAxisID: 'y2'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Voltage (V)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    y2: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Current (A)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    initializeAllanChart() {
        const ctx = document.getElementById('allan-chart').getContext('2d');
        
        this.charts.allan = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Allan Deviation',
                        data: [],
                        borderColor: 'rgb(153, 102, 255)',
                        backgroundColor: 'rgba(153, 102, 255, 0.5)',
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'logarithmic',
                        display: true,
                        title: {
                            display: true,
                            text: 'Tau (seconds)'
                        }
                    },
                    y: {
                        type: 'logarithmic',
                        display: true,
                        title: {
                            display: true,
                            text: 'Allan Deviation'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        // Connection buttons
        document.getElementById('connect-btn').addEventListener('click', () => {
            this.connect();
        });
        
        document.getElementById('disconnect-btn').addEventListener('click', () => {
            this.disconnect();
        });
        
        // Monitoring buttons
        document.getElementById('start-monitor-btn').addEventListener('click', () => {
            this.startMonitoring();
        });
        
        document.getElementById('stop-monitor-btn').addEventListener('click', () => {
            this.stopMonitoring();
        });
        
        // Holdover buttons
        document.getElementById('start-holdover-btn').addEventListener('click', () => {
            this.startHoldover();
        });
        
        document.getElementById('stop-holdover-btn').addEventListener('click', () => {
            this.stopHoldover();
        });
        
        // Test button
        document.getElementById('run-test-btn').addEventListener('click', () => {
            this.runHoldoverTest();
        });
        
        // Log upload
        document.getElementById('upload-log-btn').addEventListener('click', () => {
            this.uploadLogFile();
        });
        
        // Configuration
        document.getElementById('save-config-btn').addEventListener('click', () => {
            this.saveConfiguration();
        });
        
        // Chart view buttons
        document.getElementById('chart-freq-temp').addEventListener('click', () => {
            this.switchChartView('freq-temp');
        });
        
        document.getElementById('chart-electrical').addEventListener('click', () => {
            this.switchChartView('electrical');
        });
        
        document.getElementById('chart-status').addEventListener('click', () => {
            this.switchChartView('status');
        });
        
        document.getElementById('chart-allan').addEventListener('click', () => {
            this.switchChartView('allan');
        });
        
        // Allan deviation buttons
        document.getElementById('allan-freq').addEventListener('click', () => {
            this.switchAllanView('frequency');
        });
        
        document.getElementById('allan-temp').addEventListener('click', () => {
            this.switchAllanView('temperature');
        });
        
        // Modal events
        document.getElementById('download-results-btn').addEventListener('click', () => {
            this.downloadResults();
        });
    }
    
    switchChartView(view) {
        this.currentChartView = view;
        
        // Update button states
        document.querySelectorAll('#chart-freq-temp, #chart-electrical, #chart-status, #chart-allan')
            .forEach(btn => btn.classList.remove('active'));
        document.getElementById(`chart-${view}`).classList.add('active');
        
        // Update main chart based on view
        this.updateMainChartView(view);
    }
    
    switchAllanView(type) {
        // Update Allan deviation chart based on type
        document.querySelectorAll('#allan-freq, #allan-temp')
            .forEach(btn => btn.classList.remove('active'));
        document.getElementById(`allan-${type}`).classList.add('active');
        
        this.updateAllanChart(type);
    }
    
    updateMainChartView(view) {
        const chart = this.charts.main;
        
        switch(view) {
            case 'freq-temp':
                chart.data.datasets[0].label = 'Frequency Error (ppm)';
                chart.data.datasets[1].label = 'Temperature (°C)';
                chart.options.scales.y.title.text = 'Frequency Error (ppm)';
                chart.options.scales.y1.title.text = 'Temperature (°C)';
                break;
            case 'electrical':
                chart.data.datasets[0].label = 'Voltage (V)';
                chart.data.datasets[1].label = 'Current (A)';
                chart.options.scales.y.title.text = 'Voltage (V)';
                chart.options.scales.y1.title.text = 'Current (A)';
                break;
            case 'status':
                chart.data.datasets[0].label = 'Lock Status';
                chart.data.datasets[1].label = 'Holdover Status';
                chart.options.scales.y.title.text = 'Status';
                chart.options.scales.y1.title.text = 'Status';
                break;
            case 'allan':
                chart.data.datasets[0].label = 'Allan Deviation';
                chart.data.datasets[1].label = 'Tau';
                chart.options.scales.y.title.text = 'Allan Deviation';
                chart.options.scales.y1.title.text = 'Tau (s)';
                break;
        }
        
        chart.update();
    }
    
    updateAllanChart(type) {
        // Calculate Allan deviation for the specified type
        const data = type === 'frequency' ? this.dataHistory.frequency_error : this.dataHistory.temperature;
        const allanData = this.calculateAllanDeviation(data);
        
        this.charts.allan.data.datasets[0].data = allanData;
        this.charts.allan.update();
    }
    
    calculateAllanDeviation(data) {
        // Simple Allan deviation calculation
        // In a real implementation, this would be more sophisticated
        const allanData = [];
        const maxTau = Math.min(50, Math.floor(data.length / 2));
        
        for (let tau = 1; tau <= maxTau; tau++) {
            let sum = 0;
            let count = 0;
            
            for (let i = 0; i < data.length - 2 * tau; i++) {
                const diff = data[i + 2 * tau] - 2 * data[i + tau] + data[i];
                sum += diff * diff;
                count++;
            }
            
            if (count > 0) {
                const allanDev = Math.sqrt(sum / (2 * count * tau * tau));
                allanData.push({ x: tau, y: allanDev });
            }
        }
        
        return allanData;
    }
    
    updateStatistics() {
        const freqData = this.dataHistory.frequency_error;
        const tempData = this.dataHistory.temperature;
        const voltageData = this.dataHistory.voltage;
        
        if (freqData.length > 0) {
            const freqStdDev = this.calculateStdDev(freqData);
            document.getElementById('freq-std-dev').textContent = freqStdDev.toExponential(3);
        }
        
        if (tempData.length > 0) {
            const tempStdDev = this.calculateStdDev(tempData);
            document.getElementById('temp-std-dev').textContent = tempStdDev.toFixed(3);
        }
        
        if (voltageData.length > 0) {
            const voltageStdDev = this.calculateStdDev(voltageData);
            document.getElementById('voltage-std-dev').textContent = voltageStdDev.toFixed(3);
        }
        
        document.getElementById('data-points').textContent = this.dataHistory.timestamps.length;
    }
    
    calculateStdDev(data) {
        const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
        const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
        return Math.sqrt(variance);
    }
    
    async connect() {
        const port = document.getElementById('port').value;
        const baudrate = parseInt(document.getElementById('baudrate').value);
        const timeout = parseFloat(document.getElementById('timeout').value);
        
        try {
            const response = await fetch('/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    port: port,
                    baudrate: baudrate,
                    timeout: timeout
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.isConnected = true;
                this.updateButtonStates();
                this.showSuccess('Connected to SA5X');
                this.updateConnectionStatus(true);
            } else {
                this.showError('Connection failed: ' + data.error);
            }
        } catch (error) {
            this.showError('Connection error: ' + error.message);
        }
    }
    
    async disconnect() {
        try {
            const response = await fetch('/disconnect', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.isConnected = false;
                this.isMonitoring = false;
                this.updateButtonStates();
                this.showSuccess('Disconnected from SA5X');
                this.updateConnectionStatus(false);
            } else {
                this.showError('Disconnect failed: ' + data.error);
            }
        } catch (error) {
            this.showError('Disconnect error: ' + error.message);
        }
    }
    
    async startMonitoring() {
        const interval = parseInt(document.getElementById('monitor-interval').value);
        
        try {
            const response = await fetch('/monitor/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    interval: interval
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.isMonitoring = true;
                this.updateButtonStates();
                this.showSuccess('Monitoring started');
            } else {
                this.showError('Failed to start monitoring: ' + data.error);
            }
        } catch (error) {
            this.showError('Monitoring error: ' + error.message);
        }
    }
    
    async stopMonitoring() {
        try {
            const response = await fetch('/monitor/stop', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.isMonitoring = false;
                this.updateButtonStates();
                this.showSuccess('Monitoring stopped');
            } else {
                this.showError('Failed to stop monitoring: ' + data.error);
            }
        } catch (error) {
            this.showError('Monitoring error: ' + error.message);
        }
    }
    
    async startHoldover() {
        try {
            const response = await fetch('/holdover/start', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Holdover mode started');
            } else {
                this.showError('Failed to start holdover: ' + data.error);
            }
        } catch (error) {
            this.showError('Holdover error: ' + error.message);
        }
    }
    
    async stopHoldover() {
        try {
            const response = await fetch('/holdover/stop', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Holdover mode stopped');
            } else {
                this.showError('Failed to stop holdover: ' + data.error);
            }
        } catch (error) {
            this.showError('Holdover error: ' + error.message);
        }
    }
    
    async runHoldoverTest() {
        const duration = parseInt(document.getElementById('test-duration').value);
        const interval = parseInt(document.getElementById('test-interval').value);
        const outputFile = document.getElementById('test-output').value;
        
        try {
            const response = await fetch('/test/holdover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    duration: duration,
                    interval: interval,
                    output_file: outputFile
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Holdover test started');
                document.getElementById('test-status').innerHTML = 
                    '<span class="badge badge-info">Test Running</span>';
            } else {
                this.showError('Failed to start test: ' + data.error);
            }
        } catch (error) {
            this.showError('Test error: ' + error.message);
        }
    }
    
    async uploadLogFile() {
        const fileInput = document.getElementById('log-file');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showError('Please select a file to upload');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showLogAnalysis(data.results);
                this.showSuccess('Log file uploaded and analyzed');
            } else {
                this.showError('Upload failed: ' + data.error);
            }
        } catch (error) {
            this.showError('Upload error: ' + error.message);
        }
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/config');
            const config = await response.json();
            
            document.getElementById('config-port').value = config.serial_port || '';
            document.getElementById('config-interval').value = config.monitoring_interval || 10;
            document.getElementById('config-duration').value = config.holdover_duration || 3600;
        } catch (error) {
            console.error('Failed to load configuration:', error);
        }
    }
    
    async saveConfiguration() {
        const config = {
            'serial.default_port': document.getElementById('config-port').value,
            'monitoring.default_interval': parseInt(document.getElementById('config-interval').value),
            'holdover_test.default_duration': parseInt(document.getElementById('config-duration').value)
        };
        
        try {
            const response = await fetch('/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Configuration saved');
            } else {
                this.showError('Failed to save configuration: ' + data.error);
            }
        } catch (error) {
            this.showError('Configuration error: ' + error.message);
        }
    }
    
    updateStatusDisplay(data) {
        // Update dashboard values
        document.getElementById('status-value').textContent = data.status || '--';
        document.getElementById('freq-error-value').textContent = 
            data.frequency_error ? data.frequency_error.toExponential(3) : '--';
        document.getElementById('temp-value').textContent = 
            data.temperature ? data.temperature.toFixed(2) + '°C' : '--';
        document.getElementById('voltage-value').textContent = 
            data.voltage ? data.voltage.toFixed(2) + 'V' : '--';
        
        // Update system info
        document.getElementById('lock-status').textContent = 
            data.lock_status ? 'Locked' : 'Not Locked';
        document.getElementById('holdover-status').textContent = 
            data.holdover_status ? 'Active' : 'Inactive';
        document.getElementById('current-value').textContent = 
            data.current ? data.current.toFixed(3) + 'A' : '--';
        document.getElementById('last-update').textContent = 
            data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '--';
        
        // Add animation
        const elements = document.querySelectorAll('#status-value, #freq-error-value, #temp-value, #voltage-value');
        elements.forEach(el => {
            el.classList.add('status-update');
            setTimeout(() => el.classList.remove('status-update'), 300);
        });
    }
    
    updateCharts(data) {
        const timestamp = new Date(data.timestamp).toLocaleTimeString();
        
        // Update data history
        this.dataHistory.timestamps.push(timestamp);
        this.dataHistory.frequency_error.push(data.frequency_error || 0);
        this.dataHistory.temperature.push(data.temperature || 0);
        this.dataHistory.voltage.push(data.voltage || 0);
        this.dataHistory.current.push(data.current || 0);
        this.dataHistory.lock_status.push(data.lock_status ? 1 : 0);
        this.dataHistory.holdover_status.push(data.holdover_status ? 1 : 0);
        
        // Keep only last maxDataPoints
        if (this.dataHistory.timestamps.length > this.maxDataPoints) {
            this.dataHistory.timestamps.shift();
            this.dataHistory.frequency_error.shift();
            this.dataHistory.temperature.shift();
            this.dataHistory.voltage.shift();
            this.dataHistory.current.shift();
            this.dataHistory.lock_status.shift();
            this.dataHistory.holdover_status.shift();
        }
        
        // Update main chart based on current view
        this.updateMainChartData();
        
        // Update frequency chart
        this.charts.frequency.data.labels = [...this.dataHistory.timestamps];
        this.charts.frequency.data.datasets[0].data = [...this.dataHistory.frequency_error];
        this.charts.frequency.data.datasets[1].data = this.calculateMovingAverage(this.dataHistory.frequency_error, 5);
        
        // Update temp-electrical chart
        this.charts.tempElectrical.data.labels = [...this.dataHistory.timestamps];
        this.charts.tempElectrical.data.datasets[0].data = [...this.dataHistory.temperature];
        this.charts.tempElectrical.data.datasets[1].data = [...this.dataHistory.voltage];
        this.charts.tempElectrical.data.datasets[2].data = [...this.dataHistory.current];
        
        // Update Allan chart periodically (every 10 points)
        if (this.dataHistory.frequency_error.length % 10 === 0) {
            this.updateAllanChart('frequency');
        }
        
        // Update all charts
        this.charts.main.update('none');
        this.charts.frequency.update('none');
        this.charts.tempElectrical.update('none');
    }
    
    updateMainChartData() {
        const chart = this.charts.main;
        
        switch(this.currentChartView) {
            case 'freq-temp':
                chart.data.labels = [...this.dataHistory.timestamps];
                chart.data.datasets[0].data = [...this.dataHistory.frequency_error];
                chart.data.datasets[1].data = [...this.dataHistory.temperature];
                break;
            case 'electrical':
                chart.data.labels = [...this.dataHistory.timestamps];
                chart.data.datasets[0].data = [...this.dataHistory.voltage];
                chart.data.datasets[1].data = [...this.dataHistory.current];
                break;
            case 'status':
                chart.data.labels = [...this.dataHistory.timestamps];
                chart.data.datasets[0].data = [...this.dataHistory.lock_status];
                chart.data.datasets[1].data = [...this.dataHistory.holdover_status];
                break;
            case 'allan':
                // Allan deviation data is handled separately
                break;
        }
    }
    
    calculateMovingAverage(data, window) {
        const result = [];
        for (let i = 0; i < data.length; i++) {
            const start = Math.max(0, i - window + 1);
            const values = data.slice(start, i + 1);
            const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
            result.push(avg);
        }
        return result;
    }
    
    updateButtonStates() {
        const connectBtn = document.getElementById('connect-btn');
        const disconnectBtn = document.getElementById('disconnect-btn');
        const startMonitorBtn = document.getElementById('start-monitor-btn');
        const stopMonitorBtn = document.getElementById('stop-monitor-btn');
        const startHoldoverBtn = document.getElementById('start-holdover-btn');
        const stopHoldoverBtn = document.getElementById('stop-holdover-btn');
        const runTestBtn = document.getElementById('run-test-btn');
        
        connectBtn.disabled = this.isConnected;
        disconnectBtn.disabled = !this.isConnected;
        startMonitorBtn.disabled = !this.isConnected || this.isMonitoring;
        stopMonitorBtn.disabled = !this.isConnected || !this.isMonitoring;
        startHoldoverBtn.disabled = !this.isConnected;
        stopHoldoverBtn.disabled = !this.isConnected;
        runTestBtn.disabled = !this.isConnected;
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        const icon = statusElement.querySelector('i');
        const text = statusElement.querySelector('span') || statusElement;
        
        if (connected) {
            icon.className = 'fas fa-circle text-success';
            text.textContent = 'Connected';
        } else {
            icon.className = 'fas fa-circle text-danger';
            text.textContent = 'Disconnected';
        }
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.container-fluid').insertBefore(alertDiv, document.querySelector('.row'));
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    showTestResults(data) {
        const modal = new bootstrap.Modal(document.getElementById('testResultsModal'));
        const content = document.getElementById('test-results-content');
        
        const results = data.results;
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Test Overview</h6>
                    <div class="result-item">
                        <span class="result-label">Duration:</span>
                        <span class="result-value">${results.test_duration.toFixed(2)}s</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Measurements:</span>
                        <span class="result-value">${results.measurement_count}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <h6>Frequency Stability</h6>
                    <div class="result-item">
                        <span class="result-label">Stability:</span>
                        <span class="result-value">${results.freq_stability.toExponential(3)}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Allan Deviation (1s):</span>
                        <span class="result-value">${results.allan_deviation_1s.toExponential(3)}</span>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <h6>Temperature Stability</h6>
                    <div class="result-item">
                        <span class="result-label">Stability:</span>
                        <span class="result-value">${results.temp_stability.toFixed(3)}°C</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Mean Temperature:</span>
                        <span class="result-value">${results.temp_mean.toFixed(2)}°C</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <h6>File Information</h6>
                    <div class="result-item">
                        <span class="result-label">Output File:</span>
                        <span class="result-value">${data.output_file}</span>
                    </div>
                </div>
            </div>
        `;
        
        modal.show();
        document.getElementById('test-status').innerHTML = 
            '<span class="badge badge-success">Test Completed</span>';
    }
    
    showLogAnalysis(results) {
        const container = document.getElementById('log-analysis-results');
        const content = document.getElementById('analysis-content');
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Test Overview</h6>
                    <div class="result-item">
                        <span class="result-label">Duration:</span>
                        <span class="result-value">${results.duration.toFixed(2)}s</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Measurements:</span>
                        <span class="result-value">${results.measurement_count}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <h6>Frequency Analysis</h6>
                    <div class="result-item">
                        <span class="result-label">Stability:</span>
                        <span class="result-value">${results.freq_stability.toExponential(3)}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Allan Deviation:</span>
                        <span class="result-value">${results.allan_deviation.toExponential(3)}</span>
                    </div>
                </div>
            </div>
        `;
        
        container.style.display = 'block';
    }
    
    downloadResults() {
        // Implementation for downloading test results
        console.log('Download results functionality');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SA5XMonitor();
});