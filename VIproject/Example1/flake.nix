{
	inputs = {
		nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
		flake-utils.url = "github:numtide/flake-utils";
		poetry2nix.url = "github:nix-community/poetry2nix";
		poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
	};

	outputs = {self, nixpkgs, flake-utils, poetry2nix, ...} :
		let
			supportedSystems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
		in
		flake-utils.lib.eachSystem supportedSystems (system:
			let
				# import nixpkgs
				pkgs = import nixpkgs { config.allowUnfree = true; inherit system; };
				p2n = import poetry2nix { pkgs = pkgs; };
				lib = pkgs.lib;

				# python interpreter to use
				python-interp = pkgs.python311;

				# define poetry application
				poetry-app = p2n.mkPoetryApplication {
					python = python-interp;
					projectDir = ./.;
					preferWheels = true;

					# Override for azure-kinect-video-player to build with poetry-core
					overrides = p2n.defaultPoetryOverrides.extend (self: super: {
						azure-kinect-video-player = super.azure-kinect-video-player.overridePythonAttrs (old: {
							buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry-core ];
						});
					});
				};
			in
			{
				packages = {
					myapp = poetry-app;
					default = self.packages.${system}.myapp;
				};

				devShells.default = pkgs.mkShell {
					inherit system;
					buildInputs = with pkgs; [ poetry ffmpeg ] ++ [ poetry-app.dependencyEnv ];
				};
			});
}
