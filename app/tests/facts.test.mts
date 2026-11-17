// Run with: npm test
import { readFileSync } from "node:fs";
import { lookAlike, lookAlikeMessage, lookAlikesOf, type FactsFile } from "../src/facts.ts";

const facts = JSON.parse(readFileSync(new URL("../../catalog/sign-facts.json", import.meta.url), "utf8")) as FactsFile;
const id = (gloss: string) => `popsign-v1-0:game:${gloss}`;
let failures = 0;
const check = (name: string, ok: boolean) => { console.log(`${ok ? "PASS" : "FAIL"} ${name}`); if (!ok) failures++; };

const pairs = Object.keys(facts.signs).flatMap((a) => lookAlikesOf(a, facts.signs).filter((b) => a < b).map((b) => `${a.split(":").pop()}/${b.split(":").pop()}`));
check(`the only look-alike pair among the supported signs is boat/book (found: ${pairs.join(", ") || "none"})`, pairs.length === 1 && pairs[0] === "boat/book");
check("a sign is not a look-alike of itself", !lookAlikesOf(id("book"), facts.signs).includes(id("book")));
const message = lookAlikeMessage([{ id: id("book"), label: "book" }, { id: id("apple"), label: "apple" }, { id: id("boat"), label: "boat" }], facts.signs);
check("book and boat in the top three produce a note", message !== null && message.startsWith("book and boat look alike"));
check("no note when look-alikes are not both shown", lookAlikeMessage([{ id: id("book"), label: "book" }, { id: id("apple"), label: "apple" }], facts.signs) === null);
const base = facts.signs[id("book")];
check("a field ASL-LEX leaves out never counts as a match", !lookAlike({ ...base, movement: null }, { ...base, movement: null }));
check("signs whose forms vary in hand count are never look-alikes", !lookAlike({ ...base, hands: "varies" }, { ...base, hands: "varies" }));
process.exit(failures ? 1 : 0);
