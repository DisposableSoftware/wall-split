{
  description = "Wall Split — cuts one wide wallpaper into two";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAll = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAll (pkgs: {
        default = pkgs.callPackage ./nix/package.nix { };
      });

      devShells = forAll (pkgs: {
        default = pkgs.mkShell {
          inputsFrom = [ self.packages.${pkgs.stdenv.hostPlatform.system}.default ];
          packages = [
            (pkgs.python3.withPackages (p: [
              p.pygobject3
              p.pytest
            ]))
          ];
        };
      });

      # INT-4: building the package runs the tests.
      checks = forAll (pkgs: {
        tests = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
      });

      formatter = forAll (pkgs: pkgs.nixfmt);
    };
}
