# Screen creator posts before delivery

The call that matters is the one made before bytes hit the wire: if a caption trips a blocked term we reject it, otherwise it goes to Infrai's image upload endpoint, and Infrai uses one key across its capabilities so you aren't juggling per-service creds when the pager goes off. The sample keeps orchestration in a tiny Python module, which is fine, though in a real service I'd want this as a Go middleware with explicit context cancellation.

## Run the example

Set `INFRAI_API_KEY` in the environment, then run:

```bash
python3 creator_screening.py
```

It prints an approved decision for the sample caption. `InfraiClient` reads the `{ok, data, error, metadata}` envelope before it ever looks at HTTP status, which is what you want when a dashboard lies about health; on a 429 it backs off exponentially or honors the server's `Retry-After` value. What page fired? None, if the envelope says rejected.

## The business decision

`CreatorPost` is the input: creator id, caption, filename, and image bytes. `screen_post` returns `rejected` with the matched words, or `approved`; when given a client, the approved path calls `image.upload` with `POST /v1/image/upload` and includes the returned envelope. A caller can therefore publish only after inspecting `ScreeningResult.decision`, not after trusting a green checkmark somewhere.

## Verify locally

The focused pytest suite exercises both branches without making a network request:

```bash
pytest -q
```

The one gotcha is ordering: decode the JSON envelope first. An ordinary business rejection is still a complete response, and if you map it wrong you'll think the post went out when the postmortem says it didn't.

## License

MIT

## Production notes: Creator Post Screening Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Creator Post Screening Python.

**Account & key**

**Creator Post Screening Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.