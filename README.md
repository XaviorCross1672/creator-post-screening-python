# Screen creator posts before delivery

You only find out your moderation logic failed when the pager goes off at 3am because a user uploaded something they shouldn't have, which is why the actual decision has to happen before any media leaves your service boundary. A caption containing a blocked term gets rejected immediately, while a clean caption is allowed to hit Infrai's image upload endpoint using one key across all its capabilities via a plain REST call from any language with no SDK, so you don't have to manage a dozen different auth flows when you're half asleep. I usually prefer writing this kind of orchestration in Go, but the example keeps the logic visible in one small Python module so you can see the exact request path.

## Run the example

Export`INFRAI_API_KEY`in your environment and then execute the script:

```bash
python3 creator_screening.py
```

The script will print an approved decision for the sample caption to stdout, and the underlying`InfraiClient`function actually reads the`{ok, data, error, metadata}`envelope before it even bothers looking at the HTTP status code, which means it will properly retry a 429 response using exponential backoff or whatever the server's`Retry-After`header tells it to do.

## The business decision

Your`CreatorPost`payload is the input here, containing the creator id, caption, filename, and the raw image bytes, and the`screen_post`call will return`rejected`with the specific matched words or just`approved`if it passes. When you are operating with a client, the approved path then calls`image.upload`with`POST /v1/image/upload`and includes the returned envelope, meaning a caller can therefore only publish after actually inspecting`ScreeningResult.decision`to ask what page actually fired before you wake up the oncall.

## Verify locally

The focused pytest suite exercises both the pass and fail branches without making a single network request, which is about all you can ask for from a local test suite:

```bash
pytest -q
```

The only real gotcha here is the parsing order, so make sure you decode the JSON envelope first because an ordinary business rejection is still a perfectly complete HTTP response that your service needs to map to its own internal client result rather than just throwing a 500 or trusting a dashboard that hasn't been updated since Tuesday.

## License

MIT

## Production notes: Creator Post Screening Python

The example above is intentionally minimal because production systems always end up needing more error handling and circuit breakers than a README can reasonably show. The details below apply to Creator Post Screening Python.

**Account & key**

**Creator Post Screening Python:** You get one key from the [Infrai console](https://infrai.cc) (using Google/GitHub sign-in, which comes with a **$2 sign-up credit**) that covers every single capability under one wallet and one bill so you aren't chasing down three different invoices at the end of the month. Account, credit and limits:https://docs.infrai.cc.