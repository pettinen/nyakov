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
      <Quote
        v-if="current"
        class="p-component"
        :data="current"
      />
      <CopyButton :data="current" />
    </div>
    <p
      v-else-if="error"
      class="error p-component p-m-2"
      v-text="error"
    />
    <Divider v-if="current || error" />

    <div class="p-d-flex">
      <span class="p-float-label">
        <InputText
          id="user"
          v-model="user"
          class="no-round-right"
          :disabled="loading"
          @keyup.enter="fetch"
        />
        <label for="user">Twitch user (optional)</label>
      </span>
      <Button
        class="no-round-left p-button-info"
        label="New&nbsp;quote"
        :loading="loading"
        @click="fetch"
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
            <Quote :data="item" />
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
import {defineComponent} from "vue";

import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Divider from "primevue/divider";
import InputText from "primevue/inputtext";
import Toast from "primevue/toast";

import CopyButton from "@/components/CopyButton.vue";
import Quote from "@/components/Quote.vue";

import type {APIError, APIResponse, APISuccess} from "./types";

import "normalize.css";
import "@/../scss/main.css";
import "primevue/resources/themes/md-dark-indigo/theme.css";
import "primevue/resources/primevue.min.css";
import "primeflex/primeflex.css";
import "primeicons/primeicons.css";


// Mock i18n
const _ = function(message: string): string {
  if (message === "unexpected-error")
    return "Oopsie woopsie! We made a fucky wucky!! The code monkeys at our headquarters are working VEWY HAWD to fix this!";
  else if (message === "user-not-found")
    return "No such user.";
  return message;
};


interface AppData {
  aboutVisible: boolean;
  current: APISuccess | null;
  error: string | null;
  history: APISuccess[];
  loading: boolean;
  user: string | null;
}


export default defineComponent({
  components: {
    Accordion,
    AccordionTab,
    Button,
    CopyButton,  // eslint-disable-line @typescript-eslint/no-unsafe-assignment
    Dialog,
    Divider,
    InputText,
    Quote,  // eslint-disable-line @typescript-eslint/no-unsafe-assignment
    Toast,
  },
  data() {
    return {
      aboutVisible: false,
      current: null,
      error: null,
      history: [],
      loading: false,
      user: new URLSearchParams(location.search).get("user"),
    } as AppData;
  },
  async mounted(): Promise<void> {
    await this.fetch();
  },
  methods: {
    async fetch(): Promise<void> {
      if (this.loading)
        return;

      this.loading = true;

      const newURL = new URL(location.href);
      if (this.user)
        newURL.searchParams.set("user", this.user);
      else
        newURL.searchParams.delete("user");
      history.replaceState({user: this.user}, "nyakov", newURL.href);

      try {
        let url = "/api/v1/generate";
        if (this.user)
          url += `?user=${this.user}`;
        let response = await fetch(url);

        const data = await response.json() as APIResponse;
        if (response.ok) {
          const successResponse = data as APISuccess;
          this.error = null;
          this.current = successResponse;
          this.history.unshift(successResponse);
        } else {
          const errorResponse = data as APIError;
          this.error = _(errorResponse.error);
          this.current = null;
        }
      } catch (error: unknown) {
        this.error = _("unexpected-error");
        this.current = null;
      }
      this.loading = false;
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
