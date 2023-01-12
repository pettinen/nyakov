<template>
  <header class="p-component flex align-items-center justify-content-between p-2 mb-3">
    <strong class="p-component p-2">nyakov</strong>
    <PButton
      class="p-button-text"
      icon="pi pi-question-circle"
      @click="aboutVisible = true"
    />
  </header>

  <main class="p-component p-3">
    <div v-if="current">
      <FakeQuote
        v-if="current"
        class="p-component"
        :data="current"
      />
      <CopyButton :data="current" />
    </div>
    <p
      v-for="error of errors"
      :key="error"
      class="p-error p-component m-2"
    >
      {{ errorMessage(error) }}
    </p>
    <Divider v-if="current || errors.length > 0" />

    <div class="flex">
      <span class="p-float-label">
        <InputText
          id="user"
          v-model="user"
          class="no-round-right"
          :disabled="loading"
          @keyup.enter="fetchQuote"
        />
        <label for="user">Twitch user (optional)</label>
      </span>
      <PButton
        class="no-round-left p-button-info"
        label="New&nbsp;quote"
        :loading="loading"
        @click="fetchQuote"
      />
    </div>

    <Accordion
      v-if="history.length > 0"
      class="mt-2"
    >
      <AccordionTab header="History">
        <ul class="p-0">
          <li
            v-for="(item, index) of history"
            :key="index"
            class="history-item flex justify-content-between align-items-center px-3"
          >
            <FakeQuote :data="item" />
            <CopyButton
              :data="item"
              class="ml-2"
            />
          </li>
        </ul>
      </AccordionTab>
    </Accordion>
  </main>

  <PDialog
    v-model:visible="aboutVisible"
    header="What&rsquo;s this?"
    :modal="true"
    :dismissable-mask="true"
    :draggable="false"
    position="top"
  >
    <p>
      Generates nonsense from the Twitch chatlogs of
      <a href="https://www.twitch.tv/neonyaparty">Neonya!! Stream!</a>
      with <a href="https://en.wikipedia.org/wiki/Markov_chain">Markov chains</a>.
    </p>
    <p>Code available on <a href="https://github.com/pettinen/nyakov">GitHub</a>.</p>
    <div v-if="sources">
      <h3>Chatlog sources:</h3>
      <ul>
        <li
          v-for="({ lines, logFiles, first, last }, channel) of sources"
          :key="channel"
        >
          <a :href="`https://www.twitch.tv/${String(channel)}`">{{ channel }}</a>:
          {{ formatThousands(logFiles) }} days of chatlogs with {{ formatThousands(lines) }} lines,
          from <time>{{ first }}</time> to <time>{{ last }}</time>
        </li>
      </ul>
    </div>

    <template #footer>
      <p class="flex align-items-center">
        <span>Made with</span>
        <img
          class="emote mx-2"
          src="https://cdn.discordapp.com/emojis/745336981524971670.png"
        >
        <span>by <a href="https://aho.ge/home">aho</a></span>
      </p>
    </template>
  </PDialog>

  <Toast />
</template>

<script lang="ts">
import { format } from "d3-format";
import { defineComponent } from "vue";

import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import PButton from "primevue/button";
import PDialog from "primevue/dialog";
import Divider from "primevue/divider";
import InputText from "primevue/inputtext";
import Toast from "primevue/toast";

import CopyButton from "@/components/CopyButton.vue";
import FakeQuote from "@/components/FakeQuote.vue";

import type { APIErrors, APIResponse, APISources, APISuccess } from "./types";

import "normalize.css";
import "@/../scss/main.css";
import "@fontsource/roboto";
import "primevue/resources/themes/md-dark-indigo/theme.css";
import "primevue/resources/primevue.min.css";
import "primeflex/primeflex.css";
import "primeicons/primeicons.css";


interface Source {
  lines: number;
  logFiles: number;
  first: string;
  last: string;
}

interface AppData {
  aboutVisible: boolean;
  current: APISuccess | null;
  errors: string[];
  history: APISuccess[];
  loading: boolean;
  user?: string;
  sources: Record<string, Source> | null;
}


export default defineComponent({
  components: {
    Accordion,
    AccordionTab,
    PButton,
    CopyButton,  // eslint-disable-line @typescript-eslint/no-unsafe-assignment
    PDialog,
    Divider,
    FakeQuote,  // eslint-disable-line @typescript-eslint/no-unsafe-assignment
    InputText,
    Toast,
  },
  data() {
    const rv: AppData = {
      aboutVisible: false,
      current: null,
      errors: [],
      history: [],
      loading: false,
      sources: null,
    };
    const user = new URLSearchParams(location.search).get("user");
    if (user)
      rv.user = user;
    return rv;
  },
  mounted(): void {
    void this.fetchQuote();
    void this.fetchSources();
  },
  methods: {
    async fetchQuote(): Promise<void> {
      if (this.loading)
        return;

      this.loading = true;

      const newURL = new URL(location.href);
      if (this.user)
        newURL.searchParams.set("user", this.user);
      else
        newURL.searchParams.delete("user");
      history.replaceState({ user: this.user }, "nyakov", newURL.href);

      try {
        let url = `${process.env.ROOT_PATH ?? "/"}api/v1/generate`;
        if (this.user)
          url += `?user=${this.user}`;
        const response = await fetch(url);

        const data = await response.json() as APIResponse;
        if (response.ok) {
          const successResponse = data as APISuccess;
          this.errors = [];
          this.current = successResponse;
          this.history.unshift(successResponse);
        } else {
          const errorResponse = data as APIErrors;
          this.errors = errorResponse.errors.map(error => error.id);
          this.current = null;
        }
      } catch (error: unknown) {
        this.errors = ["internal-server-error"];
        this.current = null;
      }
      this.loading = false;
    },
    async fetchSources(): Promise<void> {
      const url = `${process.env.ROOT_PATH ?? "/"}api/v1/sources`;
      const res = await fetch(url);
      this.sources = await res.json() as APISources;
    },
    formatThousands(num: number): string {
      return format(",")(num);
    },
    errorMessage(message: string): string {
      if (message === "internal-server-error")
        return "Oopsie woopsie! We made a fucky wucky!! The code monkeys at our headquarters are working VEWY HAWD to fix this!";
      else if (message === "user-not-found")
        return "No such user.";
      return message;
    },
  },
});
</script>

<style scoped>
  a {
    color: var(--primary-color);
    text-decoration: none;
  }

  strong {
    font-weight: bold;
  }

  .emote {
    max-height: 2rem;
  }

  .error {
    color: var(--yellow-300);
  }

  .history-item {
    list-style-type: none;
  }

  .history-item:nth-child(2n) {
    background: var(--surface-50);
  }
</style>
