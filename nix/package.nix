{
  lib,
  python3Packages,
  wrapGAppsHook4,
  gobject-introspection,
  gtk4,
  gdk-pixbuf,
}:
let
  manifest = (lib.importTOML ../pyproject.toml).project;
in
python3Packages.buildPythonApplication {
  pname = manifest.name;
  inherit (manifest) version;
  pyproject = true;

  src = lib.fileset.toSource {
    root = ../.;
    fileset = lib.fileset.unions [
      ../pyproject.toml
      ../src
      ../tests
      ../data
      ../spec
    ];
  };

  build-system = [ python3Packages.setuptools ];
  dependencies = [ python3Packages.pygobject3 ];

  nativeBuildInputs = [
    wrapGAppsHook4
    gobject-introspection
  ];
  buildInputs = [
    gtk4
    gdk-pixbuf
  ];

  postInstall = ''
    install -Dm644 data/io.github.DisposableSoftware.WallSplit.desktop -t $out/share/applications
    install -Dm644 data/io.github.DisposableSoftware.WallSplit.svg -t $out/share/icons/hicolor/scalable/apps
    install -Dm644 data/io.github.DisposableSoftware.WallSplit-symbolic.svg -t $out/share/icons/hicolor/symbolic/apps
    install -Dm644 data/style.css data/config.example.ini -t $out/share/wall-split
    install -Dm644 data/themes/*.css -t $out/share/wall-split/themes
  '';

  # wrapGAppsHook4 and the Python wrapper would each wrap the script; fold the GApps
  # environment into the Python wrapper instead.
  dontWrapGApps = true;
  preFixup = ''
    makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
  '';

  nativeCheckInputs = [ python3Packages.pytestCheckHook ];
  pythonImportsCheck = [
    "wall_split.split"
    "wall_split.pairings"
    "wall_split.config"
  ];

  meta = {
    description = manifest.description;
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
    mainProgram = "wall-split";
  };
}
