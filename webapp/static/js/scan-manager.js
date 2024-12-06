// Scan Plan Manager
class ScanPlanManager {
    constructor() {
        this.countdownTime = 5;
        this.scans = new Map();
        this.isPaused = false;
    }

    async initialize() {
        // Load scan templates
        this.scans.set('ports', {
            friendly: 'Check for hidden listening ports',
            command: 'lsof -i -n -P | grep LISTEN',
            description: 'Identifies potentially malicious listening ports'
        });

        this.scans.set('network', {
            friendly: 'Monitor suspicious network activity',
            command: 'tcpdump -i any -n',
            description: 'Captures and analyzes network traffic in real-time'
        });

        this.scans.set('connections', {
            friendly: 'Check active connections',
            command: 'netstat -tunapl',
            description: 'Lists all active network connections and their processes'
        });

        // Initialize UI
        this.renderScanPlan();
        this.startCountdown();
    }

    renderScanPlan() {
        const template = document.getElementById('scan-plan');
        const container = document.getElementById('crisis-stream');
        
        // Clone and populate template
        const plan = template.content.cloneNode(true);
        container.appendChild(plan);

        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Modify plan button
        const modifyBtn = document.querySelector('[data-action="modify-plan"]');
        modifyBtn?.addEventListener('click', () => {
            this.pauseCountdown();
            this.showModifyModal();
        });

        // Any key press
        document.addEventListener('keypress', () => {
            if (this.countdownTime > 0) {
                this.pauseCountdown();
                this.showModifyModal();
            }
        });

        // Scan toggles
        document.querySelectorAll('.scan-item input[type="checkbox"]')
            .forEach(checkbox => {
                checkbox.addEventListener('change', (e) => {
                    this.updateScanPlan(e.target.dataset.scan, e.target.checked);
                });
            });
    }

    startCountdown() {
        this.countdownInterval = setInterval(() => {
            if (!this.isPaused) {
                this.countdownTime--;
                this.updateCountdownDisplay();

                if (this.countdownTime <= 0) {
                    this.executeScans();
                    clearInterval(this.countdownInterval);
                }
            }
        }, 1000);
    }

    pauseCountdown() {
        this.isPaused = true;
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
        }
    }

    resumeCountdown() {
        this.isPaused = false;
        this.startCountdown();
    }

    updateCountdownDisplay() {
        const display = document.getElementById('countdown');
        if (display) {
            display.textContent = this.countdownTime;
        }
    }

    async executeScans() {
        // Get selected scans
        const selectedScans = Array.from(document.querySelectorAll('.scan-item input[type="checkbox"]:checked'))
            .map(checkbox => checkbox.dataset.scan);

        // Execute each scan
        for (const scanId of selectedScans) {
            const scan = this.scans.get(scanId);
            if (scan) {
                try {
                    await this.executeScan(scan);
                } catch (error) {
                    console.error(`Failed to execute scan ${scanId}:`, error);
                }
            }
        }
    }

    async executeScan(scan) {
        // Emit scan start to both streams
        this.emitToStream('crisis', `Starting: ${scan.friendly}`);
        this.emitToStream('knowledge', `Executing ${scan.command} to ${scan.description}`);

        // Execute scan via backend
        const response = await fetch('/api/execute-scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: scan.command
            })
        });

        if (!response.ok) {
            throw new Error(`Scan failed: ${response.statusText}`);
        }

        // Handle streaming response
        const reader = response.body.getReader();
        while (true) {
            const {done, value} = await reader.read();
            if (done) break;

            // Process and display results
            this.processStreamingResults(new TextDecoder().decode(value));
        }
    }

    processStreamingResults(data) {
        try {
            const result = JSON.parse(data);
            this.emitToStream('crisis', result.crisis);
            this.emitToStream('knowledge', result.knowledge);
        } catch (error) {
            console.error('Failed to process streaming results:', error);
        }
    }

    emitToStream(streamType, content) {
        const stream = document.getElementById(`${streamType}-stream`);
        if (stream) {
            const entry = document.createElement('div');
            entry.className = 'stream-entry new';
            entry.textContent = content;
            stream.appendChild(entry);
            stream.scrollTop = stream.scrollHeight;
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    const scanManager = new ScanPlanManager();
    scanManager.initialize();
});
