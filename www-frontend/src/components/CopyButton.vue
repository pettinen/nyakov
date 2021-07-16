<template>
  <SplitButton
    label="Copy"
    icon="pi pi-copy"
    :model="buttonItems"
    @click="copyRaw"
  />
</template>

<script lang="ts">
import {defineComponent} from "vue";
import type {PropType} from "vue";

import SplitButton from "primevue/splitbutton";

import type {APISuccess} from "../types";


const staticEmotes: Record<string, string> = {
  AYAYA: "<:AYAYA:745336981524971670>",
  EBINYA: "<:EBINYA:753990280587378698>",
  KEKW: "<:KEKW:719244572105900112>",
  Kappa: "<:Kappa:836384492754436177>",
  MrDestructoid: "<:MrDestructoid:865234555593555969>",
  POGGERS: "<:POGGERS:730474687209144461>",
  neonyaDab: "<:neonyaDab:737602724748853369>",
  neonyaHi: "<:neonyaHi:723558619114766446>",
  neonyaJam: "<:neonyaJam:723558668917801050>",
  neonyaKakkActivated: "<:neonyaKakkActivated:865154579023659008>",
  neonyaKakkakun: "<:kakkakun:718569202214240358>",
  neonyaLove: "<:neonyaLove:723558689511833625>",
  neonyaRave: "<:neonyaRave:737602687247581275>",
  neonyaWink: "<:neonyaWink:730394904361959434>",
};

const animatedEmotes: Record<string, string> = {
  "02Hype": "<a:02Hype:730446608470376458>",
  "02HypeFlip": "<a:02HypeFlip:733241460123631696>",
  BBoomer: "<a:BBoomer:719244544264110172>",
  BirbRave: "<a:BirbRave:730447106992504894>",
  CatJam: "<a:CatJam:744271580120481954>",
  PartyKirby: "<a:PartyKirby:817934213960826881>",
  RainbowHyper: "<a:RainbowHyper:855898720385892382>",
  RainbowPls: "<a:RainbowPls:719244418728853575>",
  RainbowPlsFAST: "<a:RainbowPlsFAST:730444965833998386>",
  TambChan: "<a:TambChan:832667131244970124>",
  TambIntensifies: "<a:TambIntensifies:832667224765497354>",
  blobDance: "<a:blobDance:719244474496319498>",
  blobHYPERS: "<a:blobHYPERS:762102995008618508>",
  monkaSTEER: "<a:monkaSTEER:751877723391262780>",
  peepoShy: "<a:peepoShy:730447121119182958>",
  pepeD: "<a:pepeD:719244446620712980>",
  pepeJAM: "<a:pepeJAM:719244391037796432>",
  popCat: "<a:popCat:805164784055091251>",
};

const escapeDiscord = function(word: string): string {
  return word.replace(/[\\/|:_*~`]/gu, "\\$&");
};

export default defineComponent({
  components: {
    SplitButton,
  },
  props: {
    data: {
      type: Object as PropType<APISuccess>,
      required: true,
    },
  },
  data() {
    return {
      buttonItems: [
        {
          label: "Copy to Discord",
          command: this.copyDiscord,
        },
        {
          label: "Copy to Discord (no\xA0animated emotes)",
          command: this.copyDiscordStatic,
        },
      ],
    };
  },
  methods: {
    async copy(transform: string | null = null): Promise<void> {
      const escapeFn = transform === "discord" || transform === "discord-static"
        ? escapeDiscord
        : (x: string): string => x;

      const words = [this.data.timestamp, this.data.username].map(escapeFn);

      for (const node of this.data.message) {
        if (node.type === "emote") {
          const animatedEmote = animatedEmotes[node.name];
          const staticEmote = staticEmotes[node.name];
          if (transform === "discord" && animatedEmote)
            words.push(animatedEmote);
          else if (
            (transform === "discord" || transform === "discord-static")
            && staticEmote
          )
            words.push(staticEmote);
          else
            words.push(escapeFn(node.name));
        } else {
          words.push(escapeFn(node.text));
        }
      }

      await navigator.clipboard.writeText(words.join(" "));
      this.$toast.add({severity: "success", detail: "Copied!", life: 1000});
    },
    async copyRaw(): Promise<void> {
      await this.copy();
    },
    async copyDiscord(): Promise<void> {
      await this.copy("discord");
    },
    async copyDiscordStatic(): Promise<void> {
      await this.copy("discord-static");
    },
  },
});
</script>
