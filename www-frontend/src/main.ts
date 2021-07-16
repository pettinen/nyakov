import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import {createApp} from "vue";

import App from "@/App.vue";


// eslint-disable-next-line @typescript-eslint/no-unsafe-argument
createApp(App)
  .use(PrimeVue)
  .use(ToastService)
  .mount("#app");
