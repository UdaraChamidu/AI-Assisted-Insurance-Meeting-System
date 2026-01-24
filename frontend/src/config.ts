/**
 * Frontend configuration
 */

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  zoomSdkKey: import.meta.env.VITE_ZOOM_SDK_KEY || '',
};
