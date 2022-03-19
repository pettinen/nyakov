<template>
  <header class="p-component p-d-flex p-ai-center p-jc-between p-p-2 p-mb-3">
    <strong class="p-component p-p-2">nyakov</strong>
    <Button
      class="p-button-text"
      icon="pi pi-question-circle"
      @click="aboutVisible = true"
    />
  </header>

  <main class="p-component p-p-3">
    <div v-if="current">
      <FakeQuote
        v-if="current"
        class="p-component"
        :data="current"
      />
      <CopyButton :data="current" />
    </div>
    <p
      v-for="error in errors"
      :key="error"
      class="error p-component p-m-2"
    >
      {{ errorMessage(error) }}
    </p>
    <Divider v-if="current || errors.length > 0" />

    <div class="p-d-flex">
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
      <Button
        class="no-round-left p-button-info"
        label="New&nbsp;quote"
        :loading="loading"
        @click="fetchQuote"
      />
    </div>

    <Accordion
      v-if="history.length > 0"
      class="p-mt-2"
    >
      <AccordionTab header="History">
        <ul class="p-p-0">
          <li
            v-for="item in history"
            :key="item"
            class="history-item p-d-flex p-jc-between p-ai-center p-px-3"
          >
            <FakeQuote :data="item" />
            <CopyButton
              :data="item"
              class="p-ml-2"
            />
          </li>
        </ul>
      </AccordionTab>
    </Accordion>
  </main>

  <Dialog
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
          v-for="({ lines, logFiles, first, last }, channel) in sources"
          :key="channel"
        >
          <a :href="`https://www.twitch.tv/${channel}`">{{ channel }}</a>:
          {{ formatThousands(logFiles) }} days of chatlogs with {{ formatThousands(lines) }} lines,
          from <time>{{ first }}</time> to <time>{{ last }}</time>
        </li>
      </ul>
    </div>

    <template #footer>
      <p class="p-d-flex p-ai-center">
        <span>Made with</span>
        <img
          class="emote p-mx-2"
          src="https://cdn.discordapp.com/emojis/745336981524971670.png"
        >
        <span>by <a href="https://aho.ge/home">aho</a></span>
      </p>
    </template>
  </Dialog>

  <Toast />
</template>

<script lang="ts">
import { format } from "d3-format";
import { defineComponent } from "vue";

import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Divider from "primevue/divider";
import InputText from "primevue/inputtext";
import Toast from "primevue/toast";

import CopyButton from "@/components/CopyButton.vue";
import FakeQuote from "@/components/FakeQuote.vue";

import type { APIErrors, APIResponse, APISources, APISuccess } from "./types";

import "normalize.css";
import "@/../scss/main.css";
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
  user: string | null;
  sources: Record<string, Source> | null;
}


export default defineComponent({
  components: {
    Accordion,
    AccordionTab,
    Button,
    CopyButton,  // eslint-disable-line @typescript-eslint/no-unsafe-assignment
    Dialog,
    Divider,
    FakeQuote,  // eslint-disable-line @typescript-eslint/no-unsafe-assignment
    InputText,
    Toast,
  },
  data() {
    return {
      aboutVisible: false,
      current: null,
      errors: [],
      history: [],
      loading: false,
      user: new URLSearchParams(location.search).get("user"),
      sources: null,
    } as AppData;
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
