# Release Bootstrap

First-run setup for projects without a release spec.

## Detection

1. Read `.dominion/dominion.toml` — get `[cli]` language and build_system
2. Scan project root for version sources:
   - `package.json` → npm/node ecosystem
   - `Cargo.toml` → Rust/cargo ecosystem
   - `pyproject.toml` or `setup.py` → Python ecosystem
   - `go.mod` → Go ecosystem
   - `pom.xml` or `build.gradle` → Java/JVM ecosystem
   - `*.csproj` → .NET ecosystem
3. Scan for existing changelog: `CHANGELOG.md`, `CHANGES.md`, `HISTORY.md`
4. Check git tags for existing version scheme: `git tag --list 'v*'`

## Interview

Present detected setup and ask to confirm:

```
Release setup detected:
  Version source: {file} ({strategy})
  Build command:  {detected or "none detected"}
  Changelog:      {existing file or "none — will create CHANGELOG.md"}
  Registries:     {detected or "none"}

Confirm? [Y / customize]
```

If **customize**, ask per-section:
1. "Version strategy?" → semver / calver / custom
2. "Version source file?" → file path
3. "Build command?" → free text or "none"
4. "Build artifacts to include?" → file paths or "none"
5. "Publish to which registries?" → github-releases / npm / pypi / crates / docker / none
6. "Changelog format?" → conventional / keep-a-changelog / custom

## Generation

For each detected or confirmed registry, generate a `[[publish.steps]]` entry:

### GitHub Releases
```toml
[[publish.steps]]
name = "github-release"
registry = "github-releases"
command = "gh release create v{{version}} --title 'v{{version}}' --notes-file .dominion/release/changelog-draft.md"
auth_check = "gh auth status"
```

### npm
```toml
[[publish.steps]]
name = "npm-publish"
registry = "npm"
command = "npm publish"
auth_check = "npm whoami"
skip_if = "private"
```

### PyPI
```toml
[[publish.steps]]
name = "pypi-publish"
registry = "pypi"
command = "python -m twine upload dist/*"
auth_check = "python -m twine check dist/*"
```

### Docker
```toml
[[publish.steps]]
name = "docker-push"
registry = "docker"
command = "docker push {{image}}"
auth_check = "docker info"
```

### crates.io
```toml
[[publish.steps]]
name = "crates-publish"
registry = "crates"
command = "cargo publish"
auth_check = "cargo login --help"
```

## Output

Write populated spec to `.dominion/specs/release-spec.toml`.
Validate: `python3 -c "import tomllib; tomllib.load(open('.dominion/specs/release-spec.toml','rb'))"`

```
Release spec created at .dominion/specs/release-spec.toml
Proceeding with release...
```
