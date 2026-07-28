import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("https://proofframe.test/", {
      headers: {
        accept: "text/html",
        host: "proofframe.test",
        "x-forwarded-host": "proofframe.test",
        "x-forwarded-proto": "https",
      },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the ProofFrame control room", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>ProofFrame — Generate until it passes<\/title>/i);
  assert.match(html, /Generate until it passes\./);
  assert.match(html, /Prove every pixel\./);
  assert.match(html, /Genblaze × B2/);
  assert.match(html, /B2 release manifest/);
  assert.match(html, /brand-launch-v4\.json/);
  assert.match(html, /pixel-policy-v1/);
  assert.match(html, /no upload claimed/i);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/i);
});

test("emits absolute social preview metadata for the incoming host", async () => {
  const response = await render();
  const html = await response.text();

  assert.match(html, /property="og:title" content="ProofFrame — Generate until it passes"/i);
  assert.match(html, /property="og:image" content="https:\/\/proofframe\.test\/og\.png"/i);
  assert.match(html, /name="twitter:card" content="summary_large_image"/i);
});
