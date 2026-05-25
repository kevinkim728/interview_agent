class RealtimeClient {
    constructor() {
        this.pc = null;
        this.audioEl = null;
        this.dc = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];
    }
}
