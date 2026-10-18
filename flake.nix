{
  description = "wall-split";
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in pkgs.mkShell {
      packages = with pkgs; [
        (python3.withPackages (p: [
          p.pygobject3
          p.pytest
        ]))
        gtk4
        glib
        gobject-introspection
        pkg-config
        gdk-pixbuf
      ];
    };
  };
}
