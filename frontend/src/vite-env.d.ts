/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ZOOM_SDK_KEY: string;
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
