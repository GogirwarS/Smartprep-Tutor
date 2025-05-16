// Proctoring functionality for assessments

class Proctor {
    constructor() {
        this.tabSwitchCount = 0;
        this.cameraStream = null;
        this.microphoneStream = null;
        this.isProctoring = false;
        this.cameraElement = document.getElementById('camera-feed');
        this.microphoneIndicator = document.getElementById('microphone-indicator');
        this.tabSwitchIndicator = document.getElementById('tab-switch-indicator');
        this.warningElement = document.getElementById('proctor-warning');
        
        // Bind methods
        this.startProctoring = this.startProctoring.bind(this);
        this.stopProctoring = this.stopProctoring.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.updateTabSwitchCount = this.updateTabSwitchCount.bind(this);
        this.startCamera = this.startCamera.bind(this);
        this.startMicrophone = this.startMicrophone.bind(this);
        this.stopCamera = this.stopCamera.bind(this);
        this.stopMicrophone = this.stopMicrophone.bind(this);
        
        // Initialize event listeners
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
    }
    
    async startProctoring() {
        if (this.isProctoring) return;
        this.isProctoring = true;
        
        try {
            await Promise.all([
                this.startCamera(),
                this.startMicrophone()
            ]);
            console.log('Proctoring started successfully');
            return true;
        } catch (error) {
            console.error('Failed to start proctoring:', error);
            this.warningElement.textContent = 'Failed to start camera or microphone. Please allow access to continue.';
            this.warningElement.classList.remove('d-none');
            this.isProctoring = false;
            return false;
        }
    }
    
    stopProctoring() {
        if (!this.isProctoring) return;
        
        this.stopCamera();
        this.stopMicrophone();
        this.isProctoring = false;
        console.log('Proctoring stopped');
    }
    
    async startCamera() {
        try {
            this.cameraStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 320 },
                    height: { ideal: 240 }
                }
            });
            
            if (this.cameraElement) {
                this.cameraElement.srcObject = this.cameraStream;
                this.cameraElement.classList.remove('d-none');
            }
            return true;
        } catch (error) {
            console.error('Camera access error:', error);
            throw new Error('Camera access was denied');
        }
    }
    
    async startMicrophone() {
        try {
            this.microphoneStream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
            
            if (this.microphoneIndicator) {
                this.microphoneIndicator.classList.remove('bg-danger');
                this.microphoneIndicator.classList.add('bg-success');
            }
            return true;
        } catch (error) {
            console.error('Microphone access error:', error);
            throw new Error('Microphone access was denied');
        }
    }
    
    stopCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        
        if (this.cameraElement) {
            this.cameraElement.srcObject = null;
            this.cameraElement.classList.add('d-none');
        }
    }
    
    stopMicrophone() {
        if (this.microphoneStream) {
            this.microphoneStream.getTracks().forEach(track => track.stop());
            this.microphoneStream = null;
        }
        
        if (this.microphoneIndicator) {
            this.microphoneIndicator.classList.remove('bg-success');
            this.microphoneIndicator.classList.add('bg-danger');
        }
    }
    
    handleVisibilityChange() {
        if (document.hidden && this.isProctoring) {
            this.tabSwitchCount++;
            this.updateTabSwitchCount();
        }
    }
    
    async updateTabSwitchCount() {
        if (this.tabSwitchIndicator) {
            this.tabSwitchIndicator.textContent = this.tabSwitchCount;
        }
        
        try {
            const response = await fetch('/api/tab-switch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ count: this.tabSwitchCount }),
            });
            
            const data = await response.json();
            
            if (data.status === 'exceeded') {
                this.warningElement.textContent = 'Tab switch limit exceeded! Your assessment will be auto-submitted.';
                this.warningElement.classList.remove('d-none');
                
                // Auto-submit the assessment
                if (typeof autoSubmitAssessment === 'function') {
                    autoSubmitAssessment();
                }
            }
        } catch (error) {
            console.error('Failed to update tab switch count:', error);
        }
    }
}

// Initialize proctor when script loads
const proctor = new Proctor();

// Export the proctor instance
window.proctor = proctor;