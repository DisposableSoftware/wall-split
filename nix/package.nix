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
  ];

  meta = {
    description = manifest.description;
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
    mainProgram = "wall-split";
  };
}
