# tap-tiktok-business

`tap-tiktok-business` is a Singer tap for the TikTok Business API.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

```bash
pipx install git+https://github.com/hkuffel/tap-tiktok-business.git
```

## Configuration

### Accepted Config Options
In order to use this tap, you will need a TikTok for Business developer account and an app that's authenticated to access data from at least one business account. Accepted config parameters are:

- [ ] Client ID: The client ID for your Tiktok developer app
- [ ] Client Secret: The client secret for your developer app
- [ ] Access Token: your app's access token; expires 24 hours after generation
- [ ] Refresh Token: your app's refresh token; expires 1 year after generation
- [ ] Business IDs: a list of business IDs your app is authenticated to read data about
- [ ] Start Date

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-tiktok-business --about
```

### Source Authentication and Authorization

You can refer to the [TikTok documentation](https://ads.tiktok.com/marketing_api/docs?id=1702716474845185) for instructions on creating and authenticating your own developer app.

## Usage

You can easily run `tap-tiktok-business` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-tiktok-business --version
tap-tiktok-business --help
tap-tiktok-business --config CONFIG --discover > ./catalog.json
```

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_tiktok_business/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-tiktok-business` CLI interface directly using `poetry run`:

```bash
poetry run tap-tiktok-business --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-tiktok-business
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-tiktok-business --version
# OR run a test `elt` pipeline:
meltano elt tap-tiktok-business target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
