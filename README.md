<h1 align="center">Wall Split</h1>

<p align="center">Cuts one wide wallpaper into two, for two monitors.</p>

> [!WARNING]
> **Certified, artisanal, vibe-coded slop.**
>
> No human has read this code. An AI wrote all of it while a person said "yeah, looks
> good" and pressed Enter a lot. It cuts a picture in two, which is a job for one line
> of ImageMagick, and it does it with a whole GTK window. It only reads the image you give
> it and writes two new files next to wherever you say, so the worst it can do is cut in
> the wrong place.
>
> Bug reports will be read with great affection and then ignored.

Wall Split (`wall-split`) takes a single wide image, such as a 5120×1440 wallpaper, and
splits it at one vertical cut into a left and a right image. Nothing is cropped or
rescaled: every pixel of the source ends up in exactly one of the two outputs.

## Features

- **Drag and drop:** drop an image on the window to load it.
- **Pairings:** it lists the monitor ratio pairs that fit the image (16:9 + 16:9,
  16:9 + 32:9, …), with 16:9 + 16:9 first when the image is close to 32:9.
- **A slider** for when no pairing fits, or you just want the cut somewhere else.
- **Export** writes `<name>-left.png` and `<name>-right.png` at native resolution.

It is early. The preview doesn't scale yet, among other things; [`spec/roadmap.md`](spec/roadmap.md)
has the honest list.

## Running

You need Nix with flakes enabled.

```sh
git clone https://github.com/DisposableSoftware/wall-split
cd wall-split
nix develop
cd src && python -m wall_split
```

There is no Nix package yet, so no `nix run`.

## Development

What Wall Split does is written down in [`spec/`](spec/README.md): every behaviour is a
numbered requirement, and the code follows it. It is a Python and PyGObject app on GTK 4,
with no libadwaita.

```sh
nix develop
pytest
```

The scripts in [`scripts/manual/`](scripts/manual) drive the app to check what unit tests
can't. They run in a headless sway (`scripts/manual/headless.sh`), so they work with the
screen locked.

## License

MIT, see [LICENSE](LICENSE).
