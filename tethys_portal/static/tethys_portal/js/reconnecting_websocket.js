class ReconnectingWebSocket {
  constructor(url, protocols = [], options = {}) {
    this.url = url;
    this.protocols = protocols;
    this.options = {
      maxReconnectionDelay: options.maxReconnectionDelay || 10000,
      minReconnectionDelay: options.minReconnectionDelay || 1000 + Math.random() * 4000,
      reconnectionDelayGrowFactor: options.reconnectionDelayGrowFactor || 1.3,
      maxRetries: options.maxRetries || Infinity,
    };
    this.retries = 0;
    this.websocket;
    this.connect();
  }

  connect() {
    this.websocket = new WebSocket(this.url, this.protocols);

    this.websocket.onopen = () => {
      this.retries = 0;
      if (this.onopen) this.onopen();
    };

    this.websocket.onmessage = (event) => {
      if (this.onmessage) this.onmessage(event);
    };

    this.websocket.onerror = (error) => {
      if (this.onerror) this.onerror(error);
    };

    this.websocket.onclose = (event) => {
      if (this.onclose) this.onclose(event);
      this.reconnect();
    };
  }

  reconnect() {
    if (this.retries < this.options.maxRetries) {
      const delay = Math.min(
        this.options.minReconnectionDelay * Math.pow(this.options.reconnectionDelayGrowFactor, this.retries),
        this.options.maxReconnectionDelay
      );

      setTimeout(() => {
        this.retries++;
        this.connect();
      }, delay);
    } else {
      if (this.onmaximum) this.onmaximum();
    }
  }

  send(data) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(data);
    } else {
      throw new Error('WebSocket is not open; unable to send data');
    }
  }

  close() {
    if (this.websocket) {
      this.websocket.close();
    }
  }
}