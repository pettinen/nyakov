<template>
  <p class="p-component p-d-flex p-flex-wrap p-ai-center">
    <span
      class="p-mr-1"
      v-text="data.timestamp"
    />
    <span
      class="p-mr-1"
      v-text="data.username"
    />
    <template v-for="(node, index) in data.message">
      <span
        v-if="node.type === 'word'"
        :key="{node, index}"
        class="p-mr-1"
        v-text="node.text"
      />
      <img
        v-if="node.type === 'emote'"
        :key="{node, index}"
        class="emote p-mr-1"
        :src="emoteURL(node)"
        :title="node.name"
        :alt="node.name"
      >
    </template>
  </p>
</template>

<script lang="ts">
import {defineComponent} from "vue";

import type {EmoteNode} from "../types";


export default defineComponent({
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
  methods: {
    emoteURL(node: EmoteNode) {
      if (node.source === "twitch")
        return `https://static-cdn.jtvnw.net/emoticons/v2/${node.id}/default/dark/3.0`;
      if (node.source === "bttv")
        return `https://cdn.betterttv.net/emote/${node.id}/3x`;
      return "/favicon.png";
    },
  },
});
</script>

<style scoped>
.emote {
  max-width: 2rem;
  max-height: 2rem;
}
</style>
