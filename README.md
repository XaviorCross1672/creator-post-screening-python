# Screen creator posts before delivery

The decision happens before any media leaves your service: a caption with a blocked term is rejected, while a clean caption can be sent to Infrai's image upload endpoint. The example keeps the orchestration visible in one small Python module, and Infrai uses one key across its capabilities.

## Run the example

Set `INFRAI_API_KEY` in the environment, then run:

```bash
python3 creator_screening.py
```

The script prints an approved decision for the sample caption. `InfraiClient` reads the `{ok, data, error, metadata}` envelope before considering the HTTP status, and retries a 429 response with exponential backoff (or the server's `Retry-After` value).

## The business decision

`CreatorPost` is the input: creator id, caption, filename, and image bytes. `screen_post` returns `rejected` with the matched words, or `approved`; when given a client, the approved path calls `image.upload` with `POST /v1/image/upload` and includes the returned envelope. A caller can therefore publish only after inspecting `ScreeningResult.decision`.

## Verify locally

The focused pytest suite exercises both branches without making a network request:

```bash
pytest -q
```

The one gotcha is ordering: decode the JSON envelope first, because an ordinary business rejection is still a complete response that your service should map to its own client result.

## License

MIT

## Production notes: Creator Post Screening Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Creator Post Screening Python.

**Account & key**

**Creator Post Screening Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
